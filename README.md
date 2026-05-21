<div align="center">

# CallSage

**Local AI assistant that answers questions from your documents — voice or text, no cloud required.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

[Quick Start](#quick-start) • [API](#api) • [Configuration](#configuration) • [Development](#development)

</div>

---

CallSage is a self-hosted REST API that lets you query a knowledge base using natural language — either by uploading audio or typing text. It runs entirely on your machine: a local LLM (Mistral via Ollama), a local vector database (ChromaDB), and speech-to-text (faster-whisper), all wired together with FastAPI and LangChain.

## Quick start

You need Docker Desktop and ~10 GB of free disk space (for the Mistral model).

```bash
# 1. Start all services (app + Ollama + ChromaDB)
make start

# 2. Load your documents
#    Copy PDFs, TXT, Markdown, or DOCX files to data/knowledge_base/, then:
curl -X POST http://localhost:8000/knowledge/ingest \
  -F "files=@data/knowledge_base/my-doc.pdf"

# 3. Ask a question
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the return policy?"}'
```

The first `make start` pulls the Mistral model (~4 GB) and may take several minutes.

## How it works

A text query goes through:

1. **Input guardrails** — PII detection (Presidio), prompt injection, profanity filter
2. **Retrieval** — MMR search over ChromaDB embeddings (all-MiniLM-L6-v2)
3. **LLM generation** — Mistral via Ollama, grounded on retrieved chunks
4. **Output validation** — confidence scoring from retrieval relevance

Voice queries follow the same path, with a faster-whisper transcription step first.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health (Whisper, ChromaDB, Ollama) |
| `POST` | `/query` | Text query → answer with sources and confidence |
| `POST` | `/process` | Audio file → answer (transcribe + query) |
| `POST` | `/transcribe` | Audio file → transcript only |
| `GET` | `/knowledge/stats` | Document counts, embedding model info |
| `POST` | `/knowledge/ingest` | Upload documents to the knowledge base |
| `POST` | `/knowledge/search` | Semantic search without LLM generation |
| `POST` | `/guardrails/check` | Debug: check input for PII/injection/profanity |

Full interactive docs at `http://localhost:8000/docs` once running, or see [`docs/API.md`](docs/API.md).

**Example response from `POST /query`:**

```json
{
  "success": true,
  "response": "The return window is 30 days from the date of purchase...",
  "confidence": 0.91,
  "sources": [
    { "document": "return-policy.pdf", "relevance": 0.91 }
  ],
  "processing_time_ms": 1240
}
```

## Configuration

Copy `.env.example` to `.env` before starting:

```bash
cp .env.example .env
```

Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `mistral` | Any model available in your Ollama instance |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model for ChromaDB |
| `WHISPER_MODEL` | `base.en` | Whisper model size (`tiny`, `base`, `small`, `medium`) |
| `RAG_CHUNK_SIZE` | `500` | Token size for document chunks |
| `RAG_RETRIEVAL_TOP_K` | `4` | Number of chunks retrieved per query |
| `CONFIDENCE_THRESHOLD_HIGH` | `0.85` | Score above which confidence is reported as "high" |
| `GUARDRAILS_ENABLE_PII` | `true` | Toggle PII detection on/off |

See [`.env.example`](.env.example) for the full list with descriptions.

## Requirements

- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- 8 GB RAM minimum; 16 GB recommended
- ~10 GB disk space for Ollama + ChromaDB data

## Development

```bash
# Unit tests (no Docker required)
pytest tests/

# Single test file
pytest tests/test_guardrails.py -v

# Integration tests (requires make start)
python test_api.py

# Linting and type checks
black . && isort . && flake8 . && mypy src/
```

See [`docs/`](docs/) for architecture notes, troubleshooting, and advanced RAG configuration.

## License

MIT

---

<div align="center">

**A private, local AI that answers from your documents.**

[Report Bug](../../issues) • [Request Feature](../../issues) • [Documentation](docs/README.md)

</div>
