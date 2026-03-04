from pathlib import Path
from typing import Tuple, Optional
import yt_dlp
import ffmpeg
from app.core.config import settings


class VideoService:
    @staticmethod
    def download_video(
        url: str,
        output_dir: Optional[Path] = None
    ) -> Tuple[Path, float]:
        output_dir = output_dir or settings.UPLOAD_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
            "quiet": not settings.DEBUG,
            "no_warnings": not settings.DEBUG,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = Path(ydl.prepare_filename(info))
                duration = float(info.get("duration", 0))

            return filename, duration

        except Exception as exc:
            raise RuntimeError(f"Video download failed: {exc}") from exc

    @staticmethod
    def extract_audio(
        video_path: Path,
        output_dir: Optional[Path] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Path:
        output_dir = output_dir or settings.UPLOAD_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        if start_time is not None and start_time < 0:
            raise ValueError("start_time must be >= 0")
        if end_time is not None and end_time < 0:
            raise ValueError("end_time must be >= 0")
        if start_time is not None and end_time is not None:
            if end_time <= start_time:
                raise ValueError("end_time must be greater than start_time")

        audio_path = output_dir / f"{video_path.stem}.wav"

        try:
            stream = ffmpeg.input(str(video_path))

            if start_time is not None and end_time is not None:
                stream = stream.filter(
                    "atrim",
                    start=start_time,
                    duration=end_time - start_time,
                )
            elif start_time is not None:
                stream = stream.filter("atrim", start=start_time)

            (
                stream.output(
                    str(audio_path),
                    acodec="pcm_s16le",
                    ac=1,
                    ar="16000",
                )
                .overwrite_output()
                .run(quiet=True, capture_stdout=True, capture_stderr=True)
            )

            return audio_path

        except ffmpeg.Error as exc:
            stderr = exc.stderr.decode() if exc.stderr else str(exc)
            raise RuntimeError(f"Audio extraction failed: {stderr}") from exc

    @staticmethod
    def process_video(
        url: str,
        output_dir: Optional[Path] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Tuple[Path, Path, float]:
        video_path, duration = VideoService.download_video(url, output_dir)
        audio_path = VideoService.extract_audio(
            video_path,
            output_dir,
            start_time,
            end_time,
        )
        return video_path, audio_path, duration
