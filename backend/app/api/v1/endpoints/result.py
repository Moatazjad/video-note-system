from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.database_schema import Video, ProcessedContent, NoteTranslation
from app.models.schemas import VideoResultResponse
from app.services.export_service import ExportService

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


def _get_completed_or_409(video: Video):
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


@router.get("/result/{video_id}", response_model=VideoResultResponse)
async def get_video_result(
    video_id: int,
    db: Session = Depends(get_db),
):
    video = _get_video_or_404(video_id, db)
    _get_completed_or_409(video)

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
        transcript_source=processed.transcript_source if processed else None,
        topics=processed.topics if processed else None,
        duration=video.duration,
        created_at=video.created_at,
    )


def _resolve_export_content(video: Video, db: Session, lang: Optional[str]) -> tuple[str, str]:
    """Returns (content, language) for the requested export language,
    defaulting to the video's original language. Falls back to a cached
    NoteTranslation for any other language."""
    target_language = lang or video.language

    if target_language == video.language:
        processed = (
            db.query(ProcessedContent)
            .filter(ProcessedContent.video_id == video.id)
            .first()
        )
        if not processed or not processed.notes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notes not available",
            )
        return processed.notes, target_language

    translation = (
        db.query(NoteTranslation)
        .filter(
            NoteTranslation.video_id == video.id,
            NoteTranslation.language == target_language,
        )
        .first()
    )
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No translation available for language '{target_language}'. "
            "Request one via POST /translate first.",
        )
    return translation.content, target_language


@router.get("/export/{video_id}/markdown")
async def download_markdown(
    video_id: int,
    lang: Optional[str] = None,
    db: Session = Depends(get_db),
):
    video = _get_video_or_404(video_id, db)
    _get_completed_or_409(video)

    if lang is None or lang == video.language:
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

    content, target_language = _resolve_export_content(video, db, lang)
    md_path = ExportService.save_markdown(
        content=content,
        filename=f"video_{video_id}_notes_{target_language}",
        output_dir=settings.OUTPUT_DIR,
    )
    return FileResponse(
        path=str(md_path),
        media_type="text/markdown",
        filename=f"notes_{video_id}_{target_language}.md",
    )


@router.get("/export/{video_id}/pdf")
async def download_pdf(
    video_id: int,
    lang: Optional[str] = None,
    db: Session = Depends(get_db),
):
    video = _get_video_or_404(video_id, db)
    _get_completed_or_409(video)

    if lang is None or lang == video.language:
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

    content, target_language = _resolve_export_content(video, db, lang)
    pdf_path = ExportService.markdown_to_pdf(
        content=content,
        filename=f"video_{video_id}_notes_{target_language}",
        output_dir=settings.OUTPUT_DIR,
        language=target_language,
    )
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"notes_{video_id}_{target_language}.pdf",
    )
