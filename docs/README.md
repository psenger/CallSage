# CallSage Documentation

Complete documentation index.

---

## 🚀 Getting Started

**New here? Start with these:**

1. **[Getting Started](GETTING_STARTED.md)** ← **Start here!**
   - 3-step setup
   - First-time installation
   - Testing

2. **[Database Priming](DATABASE_PRIMING.md)**
   - Load documents (idiot-proof guide)
   - insurance documentation loading
   - Custom documents

---

## 📖 User Guides

**Using the system:**

- **[API Documentation](API.md)**
  - All endpoints
  - Request/response formats
  - Examples

- **[Configuration](CONFIGURATION.md)**
  - Environment variables
  - Settings explained
  - Tuning performance

- **[Troubleshooting](TROUBLESHOOTING.md)**
  - Common problems
  - Error messages
  - Solutions

---

## 🛠️ Developer Guides

**Building with CallSage:**

- **[OpenAPI Specification](OPENAPI.md)**
  - Swagger/OpenAPI docs
  - Client generation
  - Frontend integration

- **[Audio Architecture](AUDIO.md)**
  - How voice works
  - Browser integration
  - Recording & upload

- **[Examples](../examples/README.md)**
  - Working code
  - React, Vue, Vanilla JS
  - Voice chat UI

---

## 📋 Reference

**Technical details:**

- **[Setup Guide](SETUP.md)**
  - Detailed installation
  - Docker configuration
  - Advanced setup

- **[Specification](SPECIFICATION.md)**
  - System architecture
  - Component details
  - Design decisions

---

## 📚 Documentation by Topic

### Installation & Setup
- [Getting Started](GETTING_STARTED.md) - Quick 3-step setup
- [Setup Guide](SETUP.md) - Detailed installation
- [Database Priming](DATABASE_PRIMING.md) - Load documents

### Using the System
- [API Documentation](API.md) - Endpoint reference
- [Configuration](CONFIGURATION.md) - Settings & tuning
- [Troubleshooting](TROUBLESHOOTING.md) - Fix problems

### Development
- [OpenAPI Specification](OPENAPI.md) - API spec & clients
- [Audio Architecture](AUDIO.md) - Voice system details
- [Examples](../examples/README.md) - Code samples

### Reference
- [Specification](SPECIFICATION.md) - Technical design
- [Architecture Diagrams](SPECIFICATION.md#architecture) - Visual overview

---

## 🎯 Common Tasks

**I want to...**

### Get started
→ [Getting Started](GETTING_STARTED.md)

### Load my documents
→ [Database Priming](DATABASE_PRIMING.md)

### Use the API
→ [API Documentation](API.md)

### Build a frontend
→ [Examples](../examples/README.md) + [OpenAPI](OPENAPI.md)

### Fix an error
→ [Troubleshooting](TROUBLESHOOTING.md)

### Change settings
→ [Configuration](CONFIGURATION.md)

### Understand how it works
→ [Specification](SPECIFICATION.md)

### Add voice features
→ [Audio Architecture](AUDIO.md)

---

## 📁 File Organization

```
docs/
├── README.md                  # This file (index)
├── GETTING_STARTED.md         # Quick start guide
├── DATABASE_PRIMING.md        # Load documents
├── API.md                     # API reference
├── CONFIGURATION.md           # Settings guide
├── TROUBLESHOOTING.md         # Problem solving
├── OPENAPI.md                 # API spec & clients
├── AUDIO.md                   # Voice architecture
├── SETUP.md                   # Detailed setup
└── SPECIFICATION.md           # Technical design
```

---

## 🔗 External Resources

- **OpenAPI Spec File:** `../openapi.yaml`
- **Code Examples:** `../examples/`
- **Test Scripts:** `../test_*.py`
- **Docker Config:** `../docker-compose.yml`

---

## 💡 Quick Reference Card

```bash
# Start/Stop
make start              # Start everything
make stop               # Stop everything

# Database
make ingest-insurance documentation       # Load insurance documentation
make stats              # Check DB status

# Testing
make test-chat          # Quick test
make health             # System health

# Docs
make docs               # API docs (browser)
```

---

## Need Help?

1. **Check [Troubleshooting](TROUBLESHOOTING.md)** first
2. **Search this documentation** for your problem
3. **Check [API docs](API.md)** for endpoint help
4. **Look at [Examples](../examples/README.md)** for code

---

**Happy building!** 🎉
