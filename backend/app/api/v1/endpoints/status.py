from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_schema import Video
from app.models.schemas import VideoStatusResponse

router = APIRouter()

STATUS_FAILED = "failed"


@router.get("/status/{video_id}", response_model=VideoStatusResponse)
async def get_video_status(
    video_id: int,
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video {video_id} not found",
        )

    return VideoStatusResponse(
        id=video.id,
        url=video.url,
        status=video.status,
        progress=video.progress,
        current_step=video.current_step,
        language=video.language,
        template_type=video.template_type,
        created_at=video.created_at,
        updated_at=video.updated_at,
        error_message=video.error_message if video.status == STATUS_FAILED else None
    )
