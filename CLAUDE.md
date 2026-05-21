# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

CallSage is a FastAPI-based REST API that combines speech-to-text, RAG (Retrieval-Augmented Generation), and local LLM inference to answer questions from a knowledge base. Everything runs locally via Docker: Ollama (Mistral) for the LLM, ChromaDB for the vector store, and faster-whisper for audio transcription.

## Commands

```bash
# Start all services (app + ollama + chroma)
make start          # docker compose up -d
make stop           # docker compose down

# Health & status
make health         # GET /health
make stats          # GET /knowledge/stats

# Testing
pytest tests/                        # unit tests (guardrails module)
pytest tests/test_guardrails.py      # single test file
python test_api.py                   # integration test against running services

# Code quality
black .
isort .
flake8 .
mypy src/

# Docs
make docs    # opens Swagger UI
make redoc   # opens ReDoc
```

## Architecture

The request flow for a voice query:

```
Audio upload → WhisperService (faster-whisper) → transcribed text
                                                      ↓
                                            InputGuardrails (PII, injection, profanity)
                                                      ↓
                                            VectorStore.retrieve() → relevant chunks (ChromaDB/MMR)
                                                      ↓
                                            OllamaClient.generate() → LLM response (Mistral)
                                                      ↓
                                            OutputGuardrails → confidence score + validation
                                                      ↓
                                            ProcessResponse (with sources, confidence, flags)
```

Text queries via `POST /query` skip the transcription step and go directly to guardrails.

### Key modules

- `config/settings.py` — Pydantic Settings loaded from `.env`. Cached via `@lru_cache()`. All tunables (models, thresholds, chunk sizes, guardrail toggles) live here.
- `src/main.py` — FastAPI app with a lifespan handler that initializes all services (vectorstore, LLM, transcription) at startup.
- `src/api/routes.py` — All HTTP endpoints. Depends on service instances injected via FastAPI dependency injection.
- `src/api/schemas.py` — Pydantic v2 models for all request/response shapes.
- `src/rag/vectorstore.py` — ChromaDB HTTP client wrapper. Uses SentenceTransformer embeddings. `retrieve()` uses MMR search.
- `src/rag/ingest.py` — Loads PDF/TXT/MD/DOCX, chunks with LangChain's `RecursiveCharacterTextSplitter`, writes embeddings to ChromaDB.
- `src/llm/ollama_client.py` — Async HTTP client to Ollama. Constructs the system prompt. Uses tenacity for retries.
- `src/guardrails/input_guards.py` — PII detection (Presidio + regex), prompt injection detection (pattern matching), profanity filtering (better-profanity).
- `src/guardrails/output_guards.py` — Response validation and confidence scoring from retrieval relevance.
- `src/transcription/whisper_service.py` — faster-whisper wrapper; returns transcript, duration, language, and optional segments.

### Docker services

Three containers defined in `docker-compose.yml`:
- **app** (port 8000) — the FastAPI application
- **ollama** (internal port 11434, mapped to 11435 externally) — local LLM server running Mistral
- **chroma** (internal port 8000, mapped to 8001 externally) — vector database

Within the Docker network, `app` reaches Ollama at `http://ollama:11434` and ChromaDB at `http://chroma:8000`. These hostnames come from `config/settings.py` defaults and can be overridden in `.env`.

## Configuration

Copy `.env.example` to `.env` before running. Key variables:

| Variable | Default | Notes |
|----------|---------|-------|
| `OLLAMA_MODEL` | `mistral` | LLM model name in Ollama |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | For ChromaDB embeddings |
| `WHISPER_MODEL` | `base.en` | Whisper model size |
| `CONFIDENCE_THRESHOLD_HIGH` | `0.85` | Above this = high confidence |
| `CONFIDENCE_THRESHOLD_MEDIUM` | `0.70` | Between medium/high = medium |
| `GUARDRAILS_ENABLE_PII` | `true` | Toggle individual guardrails |
| `RAG_CHUNK_SIZE` | `500` | Document chunk size in tokens |
| `RAG_RETRIEVAL_TOP_K` | `4` | Number of chunks retrieved per query |

## Knowledge Base

Documents (PDF, TXT, MD, DOCX) go in `data/knowledge_base/`. Use `POST /knowledge/ingest` to load them into ChromaDB. Audio files for processing go in `data/audio/`.

## Testing Notes

- `tests/test_guardrails.py` tests the guardrails module in isolation (no Docker required).
- `test_api.py` is an integration script that requires all three Docker services running.
- pytest is configured for async tests via `pytest-asyncio`.
