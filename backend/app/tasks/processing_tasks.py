import os
import logging
from pathlib import Path
from celery import Task
from sqlalchemy.orm import Session


from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.video_service import VideoService
from app.services.transcription_service import TranscriptionService
from app.services.note_service import NoteService
from app.services.export_service import ExportService
from app.services.audio_chunker import AudioChunker
from app.models.database_schema import Video, ProcessedContent

logger = logging.getLogger(__name__)

STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"

MAX_DURATION = 1200
DURATION_TOLERANCE = 2

SAFE_ROOT = Path(os.getenv("OUTPUT_DIR", "outputs")).resolve()
SAFE_ROOT.mkdir(parents=True, exist_ok=True)


class DatabaseTask(Task):
    _db: Session = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db:
            self._db.close()
            self._db = None

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        video_id = args[0] if args else None
        if not video_id:
            return

        db = SessionLocal()
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video and not video.is_cancelled:
                video.status = STATUS_FAILED
                video.progress = 0
                video.current_step = None
                video.error_message = f"Processing failed after retries: {str(exc)}"
                db.commit()
                logger.error(f"Final failure hook: video_id={video_id}")
        finally:
            db.close()


def safe_delete_file(file_path: str, description: str) -> bool:
    try:
        resolved = Path(file_path).resolve()

        if SAFE_ROOT not in resolved.parents:
            logger.warning(f"Blocked unsafe delete: {file_path}")
            return False

        if resolved.exists():
            resolved.unlink()
            logger.info(f"Deleted {description}: {file_path}")
            return True
    except Exception as e:
        logger.warning(f"Failed deleting {description}: {e}")

    return False


def check_cancellation(db: Session, video_id: int) -> bool:
    db.expire_all()
    video = db.query(Video).filter(Video.id == video_id).first()

    if video and video.is_cancelled:
        video.status = STATUS_CANCELLED
        video.progress = 0
        video.current_step = None
        video.error_message = "Processing cancelled by user"
        db.commit()

        if video.video_path and safe_delete_file(video.video_path, "video"):
            video.video_path = None

        if video.audio_path and safe_delete_file(video.audio_path, "audio"):
            video.audio_path = None

        db.commit()
        logger.info(f"Cancelled: video_id={video_id}")
        return True

    return False


@celery_app.task(bind=True, base=DatabaseTask, max_retries=3)
def process_video_task(self, video_id: int):
    db = self.db
    chunk_paths = []

    try:
        video = (
            db.query(Video)
            .filter(Video.id == video_id)
            .with_for_update()
            .first()
        )

        if not video:
            logger.error(f"Video not found: video_id={video_id}")
            return

        if video.status in (STATUS_COMPLETED, STATUS_CANCELLED, STATUS_FAILED):
            logger.info(f"Terminal state: video_id={video_id}, status={video.status}")
            return

        video.status = STATUS_PROCESSING
        video.progress = 10
        video.current_step = "Downloading video"
        db.commit()

        if check_cancellation(db, video_id):
            return

        video_path, audio_path, duration = VideoService.process_video(
            url=video.url,
            start_time=video.start_time,
            end_time=video.end_time,
        )

        if duration > MAX_DURATION + DURATION_TOLERANCE:
            video.status = STATUS_FAILED
            video.current_step = None
            video.error_message = "Video exceeds 20 minute limit"
            db.commit()
            logger.warning(f"Duration limit: video_id={video_id}, duration={duration}s")
            return

        video.video_path = str(video_path)
        video.audio_path = str(audio_path)
        video.duration = duration
        video.progress = 30
        video.current_step = "Video downloaded"
        db.commit()

        if check_cancellation(db, video_id):
            return

        video.progress = 40
        video.current_step = "Preparing transcription"
        db.commit()

        chunk_paths = AudioChunker.split_audio(Path(audio_path))
        if not chunk_paths:
            raise RuntimeError("Audio chunking produced no chunks")

        transcripts = []

        for i, chunk_path in enumerate(chunk_paths):
            if check_cancellation(db, video_id):
                AudioChunker.cleanup_chunks(chunk_paths)
                return

            video.progress = 40 + int(((i + 1) / len(chunk_paths)) * 20)
            video.current_step = f"Transcribing chunk {i+1}/{len(chunk_paths)}"
            db.commit()

            transcript_text, detected_lang = TranscriptionService.transcribe(
               audio_path=Path(chunk_path),
               language=video.language,
            )
            transcripts.append(transcript_text)

        if len(chunk_paths) > 1:
            AudioChunker.cleanup_chunks(chunk_paths)

        full_transcript = " ".join(transcripts)
        if not full_transcript.strip():
            raise RuntimeError("Empty transcription result")

        logger.info(f"Transcribed: video_id={video_id}, length={len(full_transcript)}")

        if check_cancellation(db, video_id):
            return

        video.progress = 70
        video.current_step = "Generating notes"
        db.commit()

        notes = NoteService.generate_notes(
            transcript=full_transcript,
            language=video.language,
            template_type=video.template_type,
        )

        video.progress = 80
        video.current_step = "Notes generated"
        db.commit()

        if check_cancellation(db, video_id):
            return

        video.progress = 90
        video.current_step = "Exporting files"
        db.commit()

        markdown_path, pdf_path = ExportService.export(
            video_id=video_id,
            notes=notes,
            language=video.language,
        )

        if video.video_path and safe_delete_file(video.video_path, "video file"):
            video.video_path = None

        if video.audio_path and safe_delete_file(video.audio_path, "audio file"):
            video.audio_path = None

        language_map = {"en": "english", "ar": "arabic"}
        detected_language = language_map.get(video.language, video.language)

        existing = db.query(ProcessedContent).filter(
            ProcessedContent.video_id == video_id
        ).first()

        if existing:
            existing.transcript = full_transcript
            existing.notes = notes
            existing.detected_language = detected_language
        else:
            db.add(
                ProcessedContent(
                    video_id=video_id,
                    transcript=full_transcript,
                    notes=notes,
                    detected_language=detected_language,
                )
            )

        video.status = STATUS_COMPLETED
        video.progress = 100
        video.current_step = None
        video.markdown_path = str(markdown_path)
        video.pdf_path = str(pdf_path)
        db.commit()

        logger.info(f"Completed: video_id={video_id}")

        return {
            "video_id": video_id,
            "status": STATUS_COMPLETED,
            "markdown_path": str(markdown_path),
            "pdf_path": str(pdf_path),
        }

    except Exception as exc:
        logger.error(f"Processing error: video_id={video_id}", exc_info=True)

        db.rollback()

        if chunk_paths:
            AudioChunker.cleanup_chunks(chunk_paths)

        video = db.query(Video).filter(Video.id == video_id).first()

        if video and video.is_cancelled:
            check_cancellation(db, video_id)
            return

        transient_errors = (
            ConnectionError,
            TimeoutError,
            OSError,
        )

        if (
            video
            and isinstance(exc, transient_errors)
            and self.request.retries < self.max_retries
        ):
            video.current_step = f"Retrying ({self.request.retries + 1})..."
            video.error_message = str(exc)
            db.commit()
            logger.warning(
                f"Retrying: video_id={video_id}, attempt={self.request.retries + 1}"
            )
            raise self.retry(
                exc=exc,
                countdown=2 ** self.request.retries * 9,
            )

        if video and not video.is_cancelled:
            video.status = STATUS_FAILED
            video.progress = 0
            video.current_step = None
            video.error_message = str(exc)
            db.commit()
            logger.error(f"Permanent failure: video_id={video_id}")

        raise
