from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_schema import Video, ProcessedContent
from app.models.schemas import VideoResultResponse

router = APIRouter()

STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"


def _get_video_or_404(video_id: int, db: Session) -> Video:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video {video_id} not found",
        )
    return video


@router.get("/result/{video_id}", response_model=VideoResultResponse)
async def get_video_result(
    video_id: int,
    db: Session = Depends(get_db),
):
    video = _get_video_or_404(video_id, db)

    if video.status == STATUS_FAILED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=video.error_message or "Video processing failed",
        )

    if video.status != STATUS_COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Video processing not completed. Current status: {video.status}",
        )

    processed = (
        db.query(ProcessedContent)
        .filter(ProcessedContent.video_id == video_id)
        .first()
    )

    return VideoResultResponse(
        id=video.id,
        url=video.url,
        status=video.status,
        transcript=processed.transcript if processed else None,
        notes=processed.notes if processed else None,
        detected_language=processed.detected_language if processed else None,
        markdown_path=video.markdown_path,
        pdf_path=video.pdf_path,
        duration=video.duration,
        created_at=video.created_at,
    )


@router.get("/export/{video_id}/markdown")
async def download_markdown(
    video_id: int,
    db: Session = Depends(get_db),
):
    video = _get_video_or_404(video_id, db)

    if not video.markdown_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Markdown file not available",
        )

    path = Path(video.markdown_path)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Markdown file not found on disk",
        )

    return FileResponse(
        path=str(path),
        media_type="text/markdown",
        filename=f"notes_{video_id}.md",
    )


@router.get("/export/{video_id}/pdf")
async def download_pdf(
    video_id: int,
    db: Session = Depends(get_db),
):
    video = _get_video_or_404(video_id, db)

    if not video.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not available",
        )

    path = Path(video.pdf_path)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found on disk",
        )

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=f"notes_{video_id}.pdf",
    )
