import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_schema import Video, ProcessedContent, ChatMessage
from app.models.schemas import ChatMessageCreate, ChatMessageResponse, ChatHistoryResponse
from app.services import chat_service

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_completed_video_with_notes(video_id: int, db: Session) -> tuple[Video, ProcessedContent]:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video {video_id} not found",
        )

    if video.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Video processing not completed. Current status: {video.status}",
        )

    processed = (
        db.query(ProcessedContent)
        .filter(ProcessedContent.video_id == video_id)
        .first()
    )
    if not processed or not processed.notes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Notes not available for this video",
        )

    return video, processed


@router.post("/chat/{video_id}", response_model=ChatMessageResponse)
async def send_chat_message(
    video_id: int,
    request: ChatMessageCreate,
    db: Session = Depends(get_db),
):
    video, processed = _get_completed_video_with_notes(video_id, db)

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.video_id == video_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    user_msg = ChatMessage(video_id=video_id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    try:
        reply_content = chat_service.answer(
            context_text=processed.notes,
            language=video.language,
            history=history,
            user_message=request.message,
        )
    except Exception as exc:
        logger.error(f"Chat failed for video_id={video_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Chat response failed. Your message was saved.",
        )

    assistant_msg = ChatMessage(video_id=video_id, role="assistant", content=reply_content)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg


@router.get("/chat/{video_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    video_id: int,
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video {video_id} not found",
        )

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.video_id == video_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return ChatHistoryResponse(messages=messages)
