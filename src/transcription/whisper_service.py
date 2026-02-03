"""
Whisper Transcription Service.

Uses faster-whisper for efficient audio transcription.
"""

import io
import tempfile
from typing import Any, Dict

import structlog
from faster_whisper import WhisperModel

from config.settings import settings

logger = structlog.get_logger()


class WhisperService:
    """
    Audio transcription service using faster-whisper.

    Converts audio files (MP3, WAV, etc.) to text using OpenAI's
    Whisper model optimized with CTranslate2.
    """

    def __init__(self):
        """Initialize the Whisper model."""
        logger.info(
            "Initializing Whisper model",
            model=settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )

        self.model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )

        logger.info("Whisper model initialized successfully")

    def transcribe(
        self,
        audio_content: bytes,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Transcribe audio content to text.

        Args:
            audio_content: Raw audio file bytes
            language: Language code (default: "en")

        Returns:
            Dict containing transcript, segments, duration, and language
        """
        logger.info("Starting transcription", content_size=len(audio_content))

        # Write to temporary file (faster-whisper requires file path)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
            temp_file.write(audio_content)
            temp_file.flush()

            # Transcribe
            segments, info = self.model.transcribe(
                temp_file.name,
                language=language,
                beam_size=5,
                best_of=5,
                vad_filter=True,  # Voice activity detection
                vad_parameters={
                    "min_silence_duration_ms": 500,
                },
            )

            # Collect segments
            segment_list = []
            full_text_parts = []

            for segment in segments:
                segment_data = {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip(),
                }
                segment_list.append(segment_data)
                full_text_parts.append(segment.text.strip())

            full_text = " ".join(full_text_parts)

            logger.info(
                "Transcription complete",
                duration=round(info.duration, 2),
                segments=len(segment_list),
                text_length=len(full_text),
            )

            return {
                "text": full_text,
                "segments": segment_list,
                "duration": round(info.duration, 2),
                "language": info.language,
            }

    def transcribe_with_timestamps(
        self,
        audio_content: bytes,
        word_timestamps: bool = True,
    ) -> Dict[str, Any]:
        """
        Transcribe with detailed word-level timestamps.

        Args:
            audio_content: Raw audio file bytes
            word_timestamps: Include word-level timestamps

        Returns:
            Dict with transcript and detailed timing info
        """
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
            temp_file.write(audio_content)
            temp_file.flush()

            segments, info = self.model.transcribe(
                temp_file.name,
                word_timestamps=word_timestamps,
                beam_size=5,
            )

            result = {
                "text": "",
                "segments": [],
                "words": [],
                "duration": 0.0,
                "language": "en",
            }

            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())
                result["segments"].append({
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip(),
                })

                if word_timestamps and segment.words:
                    for word in segment.words:
                        result["words"].append({
                            "word": word.word,
                            "start": round(word.start, 2),
                            "end": round(word.end, 2),
                            "probability": round(word.probability, 3),
                        })

            result["text"] = " ".join(text_parts)
            result["duration"] = round(info.duration, 2)
            result["language"] = info.language

            return result
