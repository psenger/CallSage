# Configuration Guide

How to configure and tune CallSage.

---

## Configuration File

**Location:** `.env` (create from `.env.example`)

```bash
cp .env.example .env
```

**Then edit:**
```bash
nano .env
# or
code .env
```

---

## Quick Settings

### Use Defaults (Recommended)

Don't create `.env` - defaults work fine!

### Custom Settings

Create `.env` and override what you need:

```bash
# Example .env
OLLAMA_MODEL=llama3
LLM_TEMPERATURE=0.2
RETRIEVAL_TOP_K=6
```

---

## Key Settings

### LLM (Language Model)

```bash
# Which AI model to use
OLLAMA_MODEL=mistral
# Options: mistral, llama3, phi3, gemma

# How creative (0 = factual, 1 = creative)
LLM_TEMPERATURE=0.1
# Recommended: 0.1-0.3 for factual answers

# Max response length
LLM_MAX_TOKENS=512
# Higher = longer answers, slower
```

### Audio/Transcription

```bash
# Whisper model size
WHISPER_MODEL=base.en
# Options: tiny.en, base.en, small.en, medium.en, large-v3
# Larger = more accurate, slower

# Max audio length
MAX_AUDIO_DURATION=600
# In seconds (600 = 10 minutes)

# Max file size
MAX_AUDIO_SIZE_MB=25
# In megabytes
```

### Document Processing

```bash
# Chunk size for documents
CHUNK_SIZE=500
# Characters per chunk
# Larger = more context, less precise

# Overlap between chunks
CHUNK_OVERLAP=50
# Prevents splitting mid-sentence

# How many documents to retrieve
RETRIEVAL_TOP_K=4
# More = more context, slower
# Recommended: 3-6
```

### Confidence Thresholds

```bash
# High confidence (answer directly)
CONFIDENCE_HIGH=0.85

# Medium confidence (answer with caveat)
CONFIDENCE_MEDIUM=0.70

# Low confidence (suggest human)
CONFIDENCE_LOW=0.50

# Below LOW = use fallback response
```

### Guardrails

```bash
# Enable PII detection
ENABLE_PII_DETECTION=true

# Enable profanity filter
ENABLE_PROFANITY_FILTER=true

# Enable prompt injection detection
ENABLE_INJECTION_DETECTION=true

# Max input length
MAX_INPUT_LENGTH=2000
```

### Database

```bash
# ChromaDB host
CHROMA_HOST=chroma
# Don't change unless using external DB

# ChromaDB port
CHROMA_PORT=8000

# Collection name
CHROMA_COLLECTION=knowledge_base
```

### Logging

```bash
# Log level
LOG_LEVEL=INFO
# Options: DEBUG, INFO, WARNING, ERROR

# Log format
LOG_FORMAT=json
# Options: json, text
```

---

## Performance Tuning

### Faster Responses

```bash
# Use smaller model
OLLAMA_MODEL=phi3

# Reduce retrieval
RETRIEVAL_TOP_K=3

# Smaller chunks
CHUNK_SIZE=300

# Shorter responses
LLM_MAX_TOKENS=256
```

### Better Accuracy

```bash
# Use larger model
OLLAMA_MODEL=llama3

# More context
RETRIEVAL_TOP_K=6

# Larger chunks
CHUNK_SIZE=700

# More retrieval candidates
RETRIEVAL_FETCH_K=30
```

### Save Memory

```bash
# Use tiny Whisper
WHISPER_MODEL=tiny.en

# Smaller LLM
OLLAMA_MODEL=phi3

# Reduce chunk overlap
CHUNK_OVERLAP=25
```

---

## Changing Models

### Switch LLM Model

```bash
# Edit .env
OLLAMA_MODEL=llama3

# Restart
docker compose restart ollama

# Wait for model download
docker compose logs -f ollama
```

**Available models:**
- `mistral` - Balanced (default)
- `llama3` - Better quality
- `phi3` - Faster, smaller
- `gemma` - Alternative

### Switch Whisper Model

```bash
# Edit .env
WHISPER_MODEL=small.en

# Restart
docker compose restart app
```

**Available models:**
- `tiny.en` - Fastest, least accurate
- `base.en` - Good balance (default)
- `small.en` - Better accuracy
- `medium.en` - Best accuracy, slower
- `large-v3` - Best quality, very slow

---

## Environment Variables

### All Available Settings

See `.env.example` for complete list with descriptions.

### Apply Changes

```bash
# Edit .env
nano .env

# Restart affected services
docker compose restart

# Or restart everything
docker compose down
docker compose up -d
```

---

## Docker Configuration

### Memory Limits

Edit `docker-compose.yml`:

```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G  # Increase for larger models
```

### Port Changes

```yaml
services:
  app:
    ports:
      - "9000:8000"  # Change external port
```

---

## Advanced Settings

### Custom Prompts

Edit `src/llm/ollama_client.py`:

```python
SYSTEM_PROMPT = """
Your custom system prompt here...
"""
```

### Custom Guardrails

Edit `src/guardrails/input_guards.py` or `output_guards.py`

### Custom Chunking

Edit `src/rag/ingest.py`:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Custom size
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

---

## Troubleshooting Config

### Changes Not Applied

```bash
# Restart everything
docker compose down
docker compose up -d
```

### Invalid Config

Check logs:
```bash
docker compose logs app
```

### Reset to Defaults

```bash
rm .env
docker compose restart
```

---

## Production Settings

```bash
# .env for production
LOG_LEVEL=WARNING
ENABLE_PII_DETECTION=true
ENABLE_PROFANITY_FILTER=true
MAX_AUDIO_SIZE_MB=10
MAX_INPUT_LENGTH=1000
LLM_TEMPERATURE=0.1
RETRIEVAL_TOP_K=4
```

---

## Next Steps

- **Test changes:** `make test-chat`
- **View logs:** `make logs`
- **Monitor:** `make health`
