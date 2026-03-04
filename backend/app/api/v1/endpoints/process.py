from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from urllib.parse import urlparse, parse_qs
import logging

from app.core.database import get_db
from app.models.database_schema import Video
from app.models.schemas import VideoProcessRequest, VideoStatusResponse
from app.tasks.processing_tasks import process_video_task

router = APIRouter()
logger = logging.getLogger(__name__)

STATUS_PENDING = "pending"
MAX_DURATION = 1200


def normalize_youtube_url(url: str) -> str:
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    video_id = query_params.get('v', [None])[0]

    if not video_id:
        raise ValueError("Invalid YouTube URL: missing video ID")

    return f"https://www.youtube.com/watch?v={video_id}"


@router.post(
    "/process",
    response_model=VideoStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def process_video(
    request: VideoProcessRequest,
    db: Session = Depends(get_db),
):
    parsed = urlparse(str(request.url))
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid video URL",
        )

    if (
        request.start_time is not None
        and request.end_time is not None
        and request.end_time <= request.start_time
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time must be greater than start_time",
        )

    if request.start_time is not None and request.end_time is not None:
        duration = request.end_time - request.start_time
        if duration > MAX_DURATION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Video segment cannot exceed {MAX_DURATION // 60} minutes",
            )

    video = Video(
        url=normalize_youtube_url(str(request.url)),
        start_time=request.start_time,
        end_time=request.end_time,
        language=request.language,
        template_type=request.template_type,
        status=STATUS_PENDING,
        progress=0,
        is_cancelled=False,
    )

    try:
        db.add(video)
        db.commit()
        db.refresh(video)

        try:
            process_video_task.delay(video.id)
        except Exception as exc:
            logger.error("Failed to queue task for video %s: %s", video.id, exc)
            video.status = "failed"
            video.error_message = "Task queue unavailable"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Processing service is temporarily unavailable",
            )

        return VideoStatusResponse.from_orm(video)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Processing endpoint error: {exc}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@router.delete(
    "/process/{video_id}",
    status_code=status.HTTP_200_OK,
)
async def cancel_processing(
    video_id: int,
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    if video.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel {video.status} processing",
        )

    video.is_cancelled = True
    db.commit()

    logger.info(f"Cancellation requested: video_id={video_id}")

    return {
        "message": "Cancellation requested",
        "video_id": video_id,
    }
