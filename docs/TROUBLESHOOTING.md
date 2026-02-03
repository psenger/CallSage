# Troubleshooting

Common problems and solutions.

---

## Quick Fixes

### Nothing Works

```bash
# Stop everything
make stop

# Start fresh
make start

# Wait 30 seconds
sleep 30

# Test
make health
```

### "Connection refused"

```bash
# Check if running
docker compose ps

# If not running
make start
```

### "Database is empty"

```bash
make ingest-insurance documentation
```

---

## Startup Problems

### "Command not found: make"

**macOS:**
```bash
xcode-select --install
```

**Windows:** Use commands directly:
```bash
docker compose up -d
python ingest_insurance documentation.py
```

### "Cannot connect to Docker daemon"

**Fix:** Start Docker Desktop app

**Check:**
```bash
docker --version
docker compose version
```

### "Port 8000 already in use"

**Find what's using it:**
```bash
lsof -i :8000
```

**Kill it:**
```bash
kill -9 <PID>
```

**Or change port** in `docker-compose.yml`:
```yaml
ports:
  - "9000:8000"  # Use 9000 instead
```

### Services Won't Start

**Check logs:**
```bash
docker compose logs
```

**Look for errors:**
```bash
docker compose logs app
docker compose logs ollama
docker compose logs chroma
```

**Common issues:**
- Not enough memory (need 8GB)
- Ports in use
- Docker Desktop not running

---

## Database Problems

### "total_documents: 0"

**Problem:** Database is empty.

**Fix:**
```bash
make ingest-insurance documentation
```

**Verify:**
```bash
make stats
```

Should show:
```json
{
  "total_documents": 1256,
  ...
}
```

### Ingestion Fails

**Check path exists:**
```bash
ls "/data/knowledge_base"
```

**If path is wrong:**
Edit `ingest_insurance documentation.py` line 11 with YOUR path.

### Ingestion Takes Forever

**Normal!** 1,256 files = 5-10 minutes.

**Check progress:**
```bash
docker compose logs -f app
```

### Database Reset

```bash
# Stop services
make stop

# Delete database
docker volume rm ivr-chroma-data

# Restart
make start

# Reload data
make ingest-insurance documentation
```

---

## API Problems

### "404 Not Found"

**Check URL:**
```bash
# Correct
http://localhost:8000/query

# Wrong
http://localhost:8000/api/query
```

### "422 Validation Error"

**Problem:** Bad request format.

**Fix:** Check request body:
```json
{
  "text": "Your question here"
}
```

**Not:**
```json
{
  "query": "Your question here"  // Wrong field name
}
```

### "500 Internal Server Error"

**Check logs:**
```bash
docker compose logs app
```

**Common causes:**
- Database not loaded
- Ollama not running
- Out of memory

### Low Confidence Scores

**Problem:** All responses have confidence < 0.5

**Causes:**
1. **Database empty**
   ```bash
   make stats  # Should show documents
   ```

2. **Query not relevant**
   - Only ask questions about loaded documents

3. **Too few documents**
   - Load more documents

**Fix:**
```bash
make ingest-insurance documentation
make test-chat
```

---

## Audio Problems

### "Microphone access denied"

**Browser needs permission.**

**Chrome:**
1. Click lock icon in address bar
2. Allow microphone

**Safari:**
1. Safari → Settings → Websites → Microphone
2. Allow for your site

### "Audio file too large"

**Limits:**
- Max: 25MB
- Max duration: 600 seconds

**Fix:** Record shorter clips or increase limit in `.env`:
```bash
MAX_AUDIO_SIZE_MB=50
```

### "Audio format not supported"

**Supported:** MP3, WAV, WebM, M4A, FLAC

**WebM works** (browser default)

### Poor Transcription Quality

**Fixes:**
1. **Better audio**
   - Reduce background noise
   - Speak clearly
   - Use good microphone

2. **Better model**
   ```bash
   # Edit .env
   WHISPER_MODEL=medium.en

   # Restart
   docker compose restart
   ```

3. **Better format**
   - WAV > WebM > MP3

---

## Performance Problems

### Slow Responses

**Check what's slow:**
```bash
# Response includes timing
{
  "processing_time_ms": 5234
}
```

**If > 5 seconds:**

1. **Use faster model**
   ```bash
   OLLAMA_MODEL=phi3
   WHISPER_MODEL=tiny.en
   ```

2. **Reduce retrieval**
   ```bash
   RETRIEVAL_TOP_K=3
   ```

3. **Add more RAM**
   - 16GB recommended

### Out of Memory

**Symptoms:**
- Services crash
- Docker Desktop shows high memory
- "Killed" in logs

**Fixes:**
1. **Increase Docker memory**
   - Docker Desktop → Settings → Resources
   - Set to 8GB minimum

2. **Use smaller models**
   ```bash
   OLLAMA_MODEL=phi3
   WHISPER_MODEL=base.en
   ```

3. **Close other apps**

### High CPU Usage

**Normal during:**
- Audio transcription
- LLM generation
- Document ingestion

**Reduce CPU:**
```bash
# Use CPU limits in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
```

---

## Docker Problems

### "docker: command not found"

**Install Docker Desktop:**
- macOS: https://docs.docker.com/desktop/install/mac-install/
- Windows: https://docs.docker.com/desktop/install/windows-install/

### "docker compose: command not found"

**Update Docker Desktop** to version 3.4+

**Or use old syntax:**
```bash
docker-compose up  # With hyphen
```

### Containers Keep Restarting

**Check logs:**
```bash
docker compose logs <service>
```

**Common causes:**
- Health check failing
- Crash on startup
- Port conflict

**Fix:**
```bash
docker compose down
docker compose up -d
```

### "No space left on device"

**Clean up Docker:**
```bash
docker system prune -a
docker volume prune
```

---

## CORS Errors

### "Access-Control-Allow-Origin"

**Should work by default!**

**If not:**

1. **Check API is running**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Don't use file://**
   Serve HTML with:
   ```bash
   python3 -m http.server 8080
   ```

3. **Check browser console**
   - May need HTTPS for microphone

---

## Other Issues

### Logs Not Showing

```bash
# Try different services
docker compose logs app
docker compose logs ollama
docker compose logs chroma

# Follow logs
docker compose logs -f app
```

### Can't Access API Docs

```bash
# Should work:
http://localhost:8000/docs

# Check if API is running:
curl http://localhost:8000/health
```

### Ingestion Script Fails

```bash
# Check Python is installed
python3 --version

# Install dependencies
pip3 install requests

# Run with full output
python3 ingest_insurance documentation.py
```

### Changes Not Applying

```bash
# Full restart
docker compose down
docker compose up -d --build

# Check environment loaded
docker compose exec app env | grep OLLAMA
```

---

## Getting Help

### Check These First

1. **Logs**
   ```bash
   make logs
   ```

2. **Health**
   ```bash
   make health
   ```

3. **Stats**
   ```bash
   make stats
   ```

### Still Stuck?

1. **Search this documentation**
2. **Check [API docs](API.md)**
3. **Look at [examples](../examples/README.md)**
4. **Review [Getting Started](GETTING_STARTED.md)**

### Reporting Issues

Include:
- What you tried
- Error messages
- Logs (`docker compose logs`)
- Docker version
- OS version

---

## Common Error Messages

### "chromadb: not connected"

```bash
docker compose restart chroma
docker compose logs chroma
```

### "ollama: not connected"

```bash
docker compose restart ollama
docker compose logs ollama
```

### "whisper: not loaded"

```bash
docker compose restart app
docker compose logs app
```

### "Path does not exist"

Check path in `ingest_insurance documentation.py`:
```python
KNOWLEDGE_BASE_PATH = Path("YOUR_PATH_HERE")
```

---

## Reset Everything

**Nuclear option:**

```bash
# Stop all
make stop

# Delete everything
docker compose down -v
docker system prune -a

# Start fresh
make start
make ingest-insurance documentation
```

**Warning:** Deletes all data!

---

## Next Steps

- **If working:** [Use the API](API.md)
- **If still broken:** Check logs more carefully
- **Need help:** Include logs when asking for help
