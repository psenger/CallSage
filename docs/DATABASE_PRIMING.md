# Database Priming - Simple Guide

**What this means:** Loading documents into the system so it can answer questions about them.

Think of it like teaching the AI - you give it documents to read, then it can answer questions about those documents.

---

## The Absolute Simplest Way

```bash
make ingest-insurance documentation
```

That's it. This loads the entire insurance documentation into the system.

**Wait 5-10 minutes** while it processes 1,256 files.

---

## Step-by-Step (For Beginners)

### Step 1: Make sure the system is running

```bash
make start
```

Wait until you see:
```
✅ Services started. Waiting for health check...
```

### Step 2: Load the insurance documentation

```bash
make ingest-insurance documentation
```

You'll see:
```
📖 Copying insurance documentation files...
⏳ Starting ingestion...
✅ insurance documentation Ingestion Complete!
```

### Step 3: Verify it worked

```bash
make stats
```

You should see:
```json
{
  "total_documents": 1256,
  "total_chunks": 18432,
  ...
}
```

If you see numbers like this, **it worked!** 🎉

---

## What Just Happened?

1. **Copied files** - insurance documentation markdown files → `data/knowledge_base/`
2. **Split into chunks** - Cut documents into ~500-character pieces
3. **Created embeddings** - Converted text to numbers the AI understands
4. **Stored in database** - Saved in ChromaDB (vector database)

Now the AI can search these documents and answer questions!

---

## Test It

```bash
make test-chat
```

Or manually:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What does the insurance documentation say about love?"}'
```

---

## Using Your Own Documents

### Step 1: Put your files in the folder

```bash
# Files go here:
data/knowledge_base/

# Supported formats:
# - PDF (.pdf)
# - Text (.txt)
# - Markdown (.md)
# - Word (.docx)
```

### Step 2: Load them

```bash
# Option 1: Use the API
curl -X POST http://localhost:8000/knowledge/ingest \
  -F "clear_existing=true"

# Option 2: Use Python script
python ingest_insurance documentation.py  # (modify path in script)
```

### Step 3: Check it loaded

```bash
make stats
```

---

## Common Problems

### "total_documents: 0"

**Problem:** Nothing loaded.

**Fix:**
```bash
# Check if files exist
ls data/knowledge_base/

# If empty, run:
make ingest-insurance documentation
```

### "Connection refused"

**Problem:** System not running.

**Fix:**
```bash
make start
# Wait 30 seconds, then try again
```

### "Takes forever"

**Normal.** Loading 1,256 files takes 5-10 minutes.

Get coffee. ☕

### "Error: Path does not exist"

**Problem:** insurance documentation files not found.

**Fix:**
```bash
# Check the path in ingest_insurance documentation.py
# Default: /data/knowledge_base

# Update it to YOUR path:
# Edit line 11 in ingest_insurance documentation.py
```

---

## How Much Data Can I Load?

**Limits:**
- **Files:** No limit
- **File size:** No limit per file
- **Total size:** Limited by disk space
- **Time:** ~1 second per file

**Example:**
- 100 files ≈ 2 minutes
- 1,000 files ≈ 10 minutes
- 10,000 files ≈ 90 minutes

---

## Do I Need to Reload Every Time?

**No!** The database is persistent.

- Load once → Works forever
- Restart Docker → Data still there
- Only reload when you add new files

---

## Starting Over

Want to delete everything and start fresh?

```bash
# Option 1: Via API
curl -X POST http://localhost:8000/knowledge/ingest \
  -F "clear_existing=true"

# Option 2: Delete Docker volume
make stop
docker volume rm ivr-chroma-data
make start
make ingest-insurance documentation
```

---

## Summary

**Quick version:**
```bash
make start
make ingest-insurance documentation
make stats  # Verify
```

**Manual version:**
```bash
# 1. Start system
docker compose up -d

# 2. Load insurance documentation
python ingest_insurance documentation.py

# 3. Check it worked
curl http://localhost:8000/knowledge/stats
```

**That's it!** 🎉

---

## Next Steps

- [Test the system](GETTING_STARTED.md#testing)
- [Use the API](API.md)
- [View web interface](../examples/vanilla-js-chat.html)
