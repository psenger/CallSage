"""
Application configuration using Pydantic Settings.
Loads from environment variables and .env file.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key_required: bool = False
    api_key: Optional[str] = None

    # LLM Configuration
    ollama_host: str = "http://ollama:11434"
    ollama_model: str = "mistral"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 512
    llm_top_p: float = 0.9
    llm_repeat_penalty: float = 1.1

    # Transcription Configuration
    whisper_model: str = "base.en"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    max_audio_duration: int = 600
    max_audio_size_mb: int = 25

    # RAG Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_host: str = "chroma"
    chroma_port: int = 8000
    chroma_collection: str = "knowledge_base"
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_top_k: int = 4
    retrieval_fetch_k: int = 20
    retrieval_lambda: float = 0.5

    # Confidence Thresholds
    confidence_high: float = 0.85
    confidence_medium: float = 0.70
    confidence_low: float = 0.50

    # Guardrails Configuration
    enable_pii_detection: bool = True
    enable_profanity_filter: bool = True
    enable_injection_detection: bool = True
    enable_topic_classification: bool = True
    max_input_length: int = 2000
    pii_action: str = "redact"

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    enable_request_logging: bool = True

    # Performance Configuration
    request_timeout: int = 30
    max_concurrent_requests: int = 10
    enable_caching: bool = True
    cache_ttl: int = 3600


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience export
settings = get_settings()
