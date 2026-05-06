# Getting Started

Simple guide to get CallSage running in 5 minutes.

---

## What You Need

- **Docker Desktop** (includes Docker Compose)
  - macOS: https://docs.docker.com/desktop/install/mac-install/
  - Windows: https://docs.docker.com/desktop/install/windows-install/
  - Linux: https://docs.docker.com/desktop/install/linux-install/

- **8GB RAM** minimum (16GB recommended)
- **10GB free disk space**

---

## 3 Steps to Get Running

### Step 1: Start the System

```bash
cd /path/to/CallSage
make start
```

**What this does:**
- Starts 4 Docker containers (API, Ollama, ChromaDB, Whisper)
- Downloads AI models (~4GB, first time only)
- Runs health checks

**Takes:** 2-3 minutes first time, 30 seconds after that

**You'll see:**
```
✅ Services started. Waiting for health check...
```

### Step 2: Load the Database

```bash
make ingest-insurance documentation
```

**What this does:**
- Copies 1,256 insurance documentation markdown files
- Processes them into searchable chunks
- Loads into vector database

**Takes:** 5-10 minutes

**You'll see:**
```
✅ insurance documentation Ingestion Complete!
📊 Total Documents: 1256
📦 Total Chunks: ~18,000
```

### Step 3: Test It

```bash
make test-chat
```

**You'll see:**
```json
{
  "response": "The insurance documentation teaches that love is patient, kind...",
  "confidence": 0.87,
  ...
}
```

**If you see a response, it's working!** 🎉

---

## Try the Web Interface

Open this in your browser:
```bash
open examples/vanilla-js-chat.html
```

Or:
```bash
open examples/simple-voice-chat.html
```

You can:
- Type questions
- Record voice questions
- See AI responses

---

## Common Commands

```bash
make start          # Start everything
make stop           # Stop everything
make logs           # View logs
make health         # Check if running
make stats          # Check database
make docs           # View API docs
make test-chat      # Test with sample question
```

---

## What's Running?

After `make start`, you have 4 services:

| Service | Port | Purpose |
|---------|------|---------|
| **API** | 8000 | Main application |
| **Ollama** | 11434 | AI language model |
| **ChromaDB** | 8001 | Vector database |
| **Whisper** | - | Audio transcription |

**Check status:**
```bash
docker compose ps
```

**View API docs:**
```
http://localhost:8000/docs
```

---

## Troubleshooting

### "Command not found: make"

**macOS:**
```bash
xcode-select --install
```

**Windows:**
Use commands directly:
```bash
docker compose up -d
python ingest_insurance documentation.py
```

### "Cannot connect to Docker daemon"

**Fix:** Start Docker Desktop app

### "Port 8000 already in use"

**Find what's using it:**
```bash
lsof -i :8000
```

**Kill it:**
```bash
kill -9 <PID>
```

### "Services won't start"

**Check Docker:**
```bash
docker --version
docker compose version
```

**Restart Docker Desktop, then:**
```bash
make start
```

### "Database is empty"

```bash
make ingest-insurance documentation
make stats  # Should show 1256 documents
```

---

## Next Steps

Now that it's running:

1. **[Prime the database](DATABASE_PRIMING.md)** - Load your own documents
2. **[Use the API](API.md)** - Make requests from code
3. **[View examples](../examples/README.md)** - See working implementations
4. **[Customize](CONFIGURATION.md)** - Change settings

---

## Quick Reference

**Start/Stop:**
```bash
make start          # Start
make stop           # Stop
make logs           # View logs
```

**Database:**
```bash
make ingest-insurance documentation   # Load insurance documentation
make stats          # Check status
make reset          # Clear everything
```

**Testing:**
```bash
make test-chat      # Quick test
make test-insurance documentation     # Full insurance documentation tests
make health         # Check health
```

**Documentation:**
```bash
make docs           # API docs (browser)
```

---

## What's Next?

- **Add your own documents** → [Database Priming Guide](DATABASE_PRIMING.md)
- **Build a frontend** → [Examples](../examples/README.md)
- **Use the API** → [API Documentation](API.md)
- **Customize** → [Configuration](CONFIGURATION.md)

---

## Still Stuck?

See **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for detailed help.
