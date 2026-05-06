# CallSage

AI-powered voice and chat system. Ask questions, get answers from your knowledge base.

## 3-Step Setup

```bash
# 1. Start everything
make start

# 2. Load your documents
# Copy your PDF/TXT/MD files to data/knowledge_base/
# Then ingest: docker compose exec app python -m src.rag.ingest /data/knowledge_base

# 3. Test it
make test-chat
```

**Done!** 🎉

---

## What This Does

- **🎤 Voice:** Record questions → Get AI answers
- **💬 Chat:** Type questions → Get AI answers
- **📖 Knowledge:** Answers from your documents (PDF, TXT, MD, DOCX)

---

## Quick Commands

```bash
make start          # Start the system
make stop           # Stop the system
make docs           # View API docs in browser
make test-chat      # Test with a sample question
```

---

## Documentation

📖 **[Getting Started Guide](docs/GETTING_STARTED.md)** ← Start here!

All docs are in the `docs/` folder:
- [Getting Started](docs/GETTING_STARTED.md) - First-time setup
- [Database Priming](docs/DATABASE_PRIMING.md) - Load your data
- [API Guide](docs/API.md) - Use the API
- [Examples](examples/) - Working code

See **[docs/README.md](docs/README.md)** for complete index.

---

## Requirements

- **Docker Desktop** (macOS/Windows) or Docker (Linux)
- **8GB RAM** minimum (16GB better)
- **10GB disk space** for AI models

---

## Need Help?

1. **Can't start?** → See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. **API questions?** → See [docs/API.md](docs/API.md)
3. **Database empty?** → See [docs/DATABASE_PRIMING.md](docs/DATABASE_PRIMING.md)

---

## License

MIT
