# Setup Guide

This guide walks you through setting up the IVR RAG System from scratch.

## Prerequisites

### Required Software

1. **Docker Desktop** (includes Docker Compose)
   - Windows/Mac: https://www.docker.com/products/docker-desktop
   - Linux: `sudo apt install docker.io docker compose`

2. **Git** (optional, for version control)
   - https://git-scm.com/downloads

### Hardware Requirements

| Component | Minimum      | Recommended      |
|-----------|--------------|------------------|
| CPU       | 4 cores      | 8 cores          |
| RAM       | 8 GB         | 16 GB            |
| Storage   | 20 GB        | 50 GB            |
| GPU       | Not required | NVIDIA 8GB+ VRAM |

---

## Step 1: Project Setup

### 1.1 Extract the Project

```bash
# Unzip the project
unzip ivr-rag-system.zip
cd ivr-rag-system
```

### 1.2 Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your preferred settings
nano .env  # or use any text editor
```

**Key settings to review:**

```bash
# .env file

# LLM Configuration
OLLAMA_MODEL=mistral           # or llama3, phi3
LLM_TEMPERATURE=0.1            # Keep low for factual responses
LLM_MAX_TOKENS=512

# RAG Configuration  
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVAL_TOP_K=4
CONFIDENCE_THRESHOLD=0.7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Guardrails
ENABLE_PII_DETECTION=true
ENABLE_PROFANITY_FILTER=true
```

---

## Step 2: Build and Start Services

### 2.1 Build Containers

```bash
# Build all containers (first time takes 5-10 minutes)
docker compose build
```

### 2.2 Start Services

```bash
# Start in foreground (see logs)
docker compose up

# Or start in background
docker compose up -d
```

### 2.3 Verify Services

```bash
# Check all containers are running
docker compose ps

# Expected output:
# NAME                    STATUS
# ivr-rag-system-app      Up
# ivr-rag-system-ollama   Up
# ivr-rag-system-chroma   Up
```

### 2.4 Pull the LLM Model

The first time you start, Ollama needs to download the model:

```bash
# This happens automatically, but you can trigger manually:
docker compose exec ollama ollama pull mistral

# Check model is available
docker compose exec ollama ollama list
```

---

## Step 3: Add Your Knowledge Base

### 3.1 Prepare Documents

Place your documents in the `data/knowledge_base/` folder:

```
data/knowledge_base/
├── company-faq.pdf
├── refund-policy.txt
├── product-guide.md
└── support-procedures.docx
```

**Supported formats:** PDF, TXT, MD, DOCX

### 3.2 Ingest Documents

```bash
# Run the ingestion script
docker compose exec app python -m src.rag.ingest

# Expected output:
# Loading documents from /data/knowledge_base...
# Found 4 documents
# Splitting into chunks... 156 chunks created
# Generating embeddings...
# Storing in ChromaDB...
# ✓ Ingestion complete!
```

### 3.3 Verify Ingestion

```bash
curl http://localhost:8000/knowledge/stats
```

Expected response:
```json
{
    "total_documents": 4,
    "total_chunks": 156,
    "last_updated": "2024-01-15T10:30:00Z"
}
```

---

## Step 4: Test the System

### 4.1 Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
    "status": "healthy",
    "components": {
        "ollama": "connected",
        "chromadb": "connected",
        "whisper": "loaded"
    }
}
```

### 4.2 Test with Text Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What is your refund policy?"}'
```

### 4.3 Test with Audio File

```bash
# Place a test MP3 in data/audio/
curl -X POST http://localhost:8000/process \
  -F "audio=@data/audio/test_recording.mp3"
```

---

## Step 5: Development Setup (Optional)

If you want to modify the code:

### 5.1 Local Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 5.2 Run Tests

```bash
# With Docker
docker compose exec app pytest

# Locally
pytest tests/
```

### 5.3 Code Formatting

```bash
# Format code
black src/
isort src/

# Lint
flake8 src/
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs app
docker compose logs ollama

# Restart services
docker compose down
docker compose up --build
```

### Ollama model not loading

```bash
# Check Ollama status
docker compose exec ollama ollama list

# Re-pull model
docker compose exec ollama ollama pull mistral
```

### Out of memory

Edit `docker compose.yml` to adjust memory limits:

```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G  # Increase if needed
```

### Slow transcription

- Ensure you're using the `base.en` model (not `large`)
- Consider using GPU if available
- Check CPU usage: `docker stats`

### ChromaDB errors

```bash
# Reset the database
docker compose down -v  # Warning: deletes all data
docker compose up -d
# Re-run ingestion
```

---

## Updating

### Pull Latest Changes

```bash
git pull origin main  # If using git
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Update Dependencies

```bash
docker compose exec app pip install -r requirements.txt --upgrade
```

---

## Stopping the System

```bash
# Stop containers (keeps data)
docker compose stop

# Stop and remove containers (keeps volumes)
docker compose down

# Stop and remove everything including data
docker compose down -v
```

---

## Next Steps

1. **Customize guardrails** - Edit `src/guardrails/input_guards.py` for your needs
2. **Add more documents** - Keep expanding your knowledge base
3. **Monitor usage** - Check logs for common queries
4. **Fine-tune prompts** - Adjust `config/settings.py` for better responses

See [API Documentation](API.md) for full endpoint reference.
