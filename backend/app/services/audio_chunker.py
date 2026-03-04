import subprocess
from pathlib import Path
from typing import List
import logging
import math

logger = logging.getLogger(__name__)

CHUNK_DURATION = 600
MAX_CHUNKS = 10
FFMPEG_TIMEOUT = 300
FFPROBE_TIMEOUT = 30


class AudioChunker:
    @staticmethod
    def split_audio(audio_path: str, chunk_duration: int = CHUNK_DURATION) -> List[str]:
        audio_file = Path(audio_path)

        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        duration = AudioChunker._get_duration(audio_path)

        if duration <= chunk_duration:
            logger.info(f"No chunking needed: {duration:.1f}s")
            return [audio_path]

        num_chunks = math.ceil(duration / chunk_duration)

        if num_chunks <= 0 or num_chunks > MAX_CHUNKS:
            raise RuntimeError(
                f"Invalid chunk calculation: duration={duration}, chunks={num_chunks}"
            )

        output_dir = audio_file.parent
        base_name = audio_file.stem
        chunk_paths = []

        logger.info(f"Splitting {duration:.1f}s into {num_chunks} chunks")

        try:
            for i in range(num_chunks):
                start_time = i * chunk_duration
                chunk_path = output_dir / f"{base_name}_chunk_{i}.mp3"

                cmd = [
                    "ffmpeg",
                    "-nostdin",
                    "-loglevel", "error",
                    "-ss", str(start_time),
                    "-i", str(audio_path),
                    "-t", str(chunk_duration),
                    "-vn",
                    "-acodec", "libmp3lame",
                    "-ar", "16000",
                    "-ac", "1",
                    "-b:a", "64k",
                    "-y",
                    str(chunk_path),
                ]

                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    timeout=FFMPEG_TIMEOUT,
                )

                if not chunk_path.exists():
                    raise RuntimeError(f"Chunk not created: {chunk_path}")

                chunk_paths.append(str(chunk_path))
                logger.info(f"Created chunk {i+1}/{num_chunks}")

        except Exception as e:
            logger.error(f"Chunking failed: {e}")

            for p in chunk_paths:
                Path(p).unlink(missing_ok=True)

            raise RuntimeError(f"Audio chunking failed: {e}") from e

        return chunk_paths

    @staticmethod
    def _get_duration(audio_path: str) -> float:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=FFPROBE_TIMEOUT,
            )

            duration = float(result.stdout.strip())

            if duration <= 0 or duration > 7200:
                raise ValueError(
                    f"Duration {duration}s outside valid range (0, 7200]"
                )

            return duration

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"ffprobe timeout (>{FFPROBE_TIMEOUT}s)")

        except ValueError as e:
            raise RuntimeError(f"Invalid duration: {e}") from e

        except Exception as e:
            raise RuntimeError(f"Could not get audio duration: {e}") from e

    @staticmethod
    def cleanup_chunks(chunk_paths: List[str]):
        for chunk_path in chunk_paths:
            try:
                Path(chunk_path).unlink(missing_ok=True)
            except Exception:
                pass
