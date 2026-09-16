import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_schema import Video, ProcessedContent, NoteTranslation
from app.models.schemas import TranslateRequest, TranslateResponse
from app.services.note_service import translate_notes

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/translate/{video_id}", response_model=TranslateResponse)
async def translate_video_notes(
    video_id: int,
    request: TranslateRequest,
    db: Session = Depends(get_db),
):
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notes not available",
        )

    target_language = request.target_language

    if target_language == video.language:
        return TranslateResponse(language=target_language, content=processed.notes)

    existing = (
        db.query(NoteTranslation)
        .filter(
            NoteTranslation.video_id == video_id,
            NoteTranslation.language == target_language,
        )
        .first()
    )
    if existing:
        return TranslateResponse(language=target_language, content=existing.content)

    try:
        translated = translate_notes(processed.notes, target_language)
    except Exception as exc:
        logger.error(f"Translation failed for video_id={video_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Translation failed",
        )

    db.add(
        NoteTranslation(
            video_id=video_id,
            language=target_language,
            content=translated,
        )
    )
    db.commit()

    return TranslateResponse(language=target_language, content=translated)
