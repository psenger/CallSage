# API Documentation

Base URL: `http://localhost:8000`

---

## Endpoints

### Health & Status

#### GET /health
Check system health and component status.

**Response:**
```json
{
    "status": "healthy",
    "components": {
        "ollama": "connected",
        "chromadb": "connected",
        "whisper": "loaded"
    },
    "version": "1.0.0"
}
```

**Status Codes:**
- `200` - All systems operational
- `503` - One or more components unhealthy

---

### Query Processing

#### POST /process
Process an audio file through the full pipeline (transcription → guardrails → RAG → response).

**Request:**
```
Content-Type: multipart/form-data

Parameters:
- audio (file, required): Audio file (MP3, WAV, M4A, FLAC)
- max_duration (int, optional): Maximum audio duration in seconds (default: 600)
```

**Example:**
```bash
curl -X POST http://localhost:8000/process \
  -F "audio=@recording.mp3"
```

**Response:**
```json
{
    "success": true,
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "transcript": "What is your return policy?",
    "response": "Our return policy allows you to return items within 30 days of purchase for a full refund. Items must be in original condition with tags attached.",
    "confidence": 0.89,
    "sources": [
        {
            "document": "return-policy.pdf",
            "chunk_id": "chunk_42",
            "relevance": 0.92
        }
    ],
    "guardrails": {
        "pii_detected": false,
        "profanity_detected": false,
        "in_scope": true
    },
    "processing_time_ms": 2340
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "Audio file too long (max 600 seconds)",
    "error_code": "AUDIO_TOO_LONG"
}
```

---

#### POST /query
Query with text directly (skips transcription).

**Request:**
```json
{
    "text": "What is your refund policy?",
    "conversation_id": "optional-uuid-for-context"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What is your refund policy?"}'
```

**Response:**
```json
{
    "success": true,
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "response": "Our refund policy allows returns within 30 days...",
    "confidence": 0.89,
    "sources": [
        {
            "document": "refund-policy.pdf",
            "chunk_id": "chunk_15",
            "relevance": 0.91
        }
    ],
    "fallback_used": false,
    "processing_time_ms": 890
}
```

---

#### POST /transcribe
Transcribe audio without querying (useful for testing).

**Request:**
```
Content-Type: multipart/form-data

Parameters:
- audio (file, required): Audio file
```

**Response:**
```json
{
    "success": true,
    "transcript": "Hello, I have a question about my order.",
    "segments": [
        {
            "start": 0.0,
            "end": 1.2,
            "text": "Hello,"
        },
        {
            "start": 1.2,
            "end": 3.5,
            "text": "I have a question about my order."
        }
    ],
    "duration": 3.5,
    "language": "en"
}
```

---

### Knowledge Base Management

#### GET /knowledge/stats
Get knowledge base statistics.

**Response:**
```json
{
    "total_documents": 12,
    "total_chunks": 458,
    "embedding_model": "all-MiniLM-L6-v2",
    "embedding_dimensions": 384,
    "last_updated": "2024-01-15T10:30:00Z",
    "documents": [
        {
            "name": "faq.pdf",
            "chunks": 45,
            "ingested_at": "2024-01-15T10:30:00Z"
        },
        {
            "name": "policies.md",
            "chunks": 23,
            "ingested_at": "2024-01-14T08:15:00Z"
        }
    ]
}
```

---

#### POST /knowledge/ingest
Ingest new documents into the knowledge base.

**Request:**
```
Content-Type: multipart/form-data

Parameters:
- documents (file[], required): One or more documents (PDF, TXT, MD, DOCX)
- replace (bool, optional): If true, replace existing document with same name
```

**Example:**
```bash
curl -X POST http://localhost:8000/knowledge/ingest \
  -F "documents=@new-faq.pdf" \
  -F "documents=@updated-policy.txt"
```

**Response:**
```json
{
    "success": true,
    "ingested": [
        {
            "name": "new-faq.pdf",
            "chunks_created": 34
        },
        {
            "name": "updated-policy.txt",
            "chunks_created": 12
        }
    ],
    "total_chunks_added": 46
}
```

---

#### DELETE /knowledge/document/{name}
Remove a document from the knowledge base.

**Example:**
```bash
curl -X DELETE http://localhost:8000/knowledge/document/old-policy.pdf
```

**Response:**
```json
{
    "success": true,
    "document": "old-policy.pdf",
    "chunks_removed": 28
}
```

---

#### POST /knowledge/search
Search the knowledge base directly (for debugging).

**Request:**
```json
{
    "query": "refund policy",
    "top_k": 5
}
```

**Response:**
```json
{
    "results": [
        {
            "content": "Our refund policy allows customers to return...",
            "document": "policies.pdf",
            "chunk_id": "chunk_42",
            "relevance": 0.94
        },
        {
            "content": "Refunds are processed within 5-7 business days...",
            "document": "faq.md",
            "chunk_id": "chunk_78",
            "relevance": 0.87
        }
    ]
}
```

---

### Guardrails

#### POST /guardrails/check
Check text against guardrails without processing.

**Request:**
```json
{
    "text": "My phone number is 555-123-4567"
}
```

**Response:**
```json
{
    "original": "My phone number is 555-123-4567",
    "sanitized": "My phone number is [PHONE_REDACTED]",
    "flags": {
        "pii_detected": true,
        "pii_types": ["phone_number"],
        "profanity_detected": false,
        "in_scope": true,
        "injection_detected": false
    }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `AUDIO_TOO_LONG` | Audio exceeds maximum duration |
| `AUDIO_INVALID` | Unsupported audio format |
| `TRANSCRIPTION_FAILED` | Whisper transcription error |
| `GUARDRAIL_BLOCKED` | Content blocked by guardrails |
| `RAG_ERROR` | Vector store or retrieval error |
| `LLM_ERROR` | Ollama connection or generation error |
| `DOCUMENT_NOT_FOUND` | Requested document doesn't exist |
| `INGESTION_FAILED` | Document ingestion error |

---

## Rate Limiting

Default limits (configurable in `.env`):

| Endpoint | Limit |
|----------|-------|
| `/process` | 10 requests/minute |
| `/query` | 30 requests/minute |
| `/knowledge/ingest` | 5 requests/minute |
| Other endpoints | 60 requests/minute |

**Rate limit headers:**
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 28
X-RateLimit-Reset: 1705312800
```

---

## Authentication (Optional)

If `API_KEY_REQUIRED=true` in `.env`:

```bash
curl -X POST http://localhost:8000/query \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "What is your refund policy?"}'
```

---

## WebSocket (Future)

Planned for real-time streaming:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/stream');
ws.send(JSON.stringify({ text: "What is your policy?" }));
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.token);  // Streamed tokens
};
```
