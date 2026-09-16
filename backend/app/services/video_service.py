from pathlib import Path
from typing import Tuple, Optional
import yt_dlp
import ffmpeg
from app.core.config import settings


class VideoService:
    @staticmethod
    def get_duration(url: str) -> float:
        ydl_opts = {
            "quiet": not settings.DEBUG,
            "no_warnings": not settings.DEBUG,
            "skip_download": True,
            "cookiefile": settings.YT_DLP_COOKIEFILE,
            "remote_components": ["ejs:github"],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return float(info.get("duration", 0))
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch video metadata: {exc}") from exc

    @staticmethod
    def download_audio_only(
        url: str,
        output_dir: Optional[Path] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> Tuple[Path, float]:
        """Download ONLY the audio track (never video) via yt-dlp. When both
        start_time and end_time are given, fetches just that slice from the
        source instead of the whole audio."""
        output_dir = output_dir or settings.UPLOAD_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "0",
                }
            ],
            "quiet": not settings.DEBUG,
            "no_warnings": not settings.DEBUG,
            "cookiefile": settings.YT_DLP_COOKIEFILE,
            "remote_components": ["ejs:github"],
        }

        if start_time is not None and end_time is not None:
            ydl_opts["download_ranges"] = yt_dlp.utils.download_range_func(
                None, [(start_time, end_time)]
            )
            ydl_opts["force_keyframes_at_cuts"] = True

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = Path(ydl.prepare_filename(info))
                audio_path = filename.with_suffix(".wav")
                duration = float(info.get("duration", 0))

            return audio_path, duration

        except Exception as exc:
            raise RuntimeError(f"Audio download failed: {exc}") from exc

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
            "cookiefile": settings.YT_DLP_COOKIEFILE,
            "remote_components": ["ejs:github"],
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
