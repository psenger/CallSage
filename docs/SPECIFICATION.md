# Technical Specification: IVR RAG System

## 1. Overview

### 1.1 Purpose
This system processes MP3 recordings from IVR (Interactive Voice Response) phone systems, transcribes them, and uses Retrieval-Augmented Generation (RAG) to answer customer queries based on a company knowledge base.

### 1.2 Goals
- Accurately transcribe IVR audio recordings
- Safely process customer queries with input/output guardrails
- Provide helpful, accurate responses grounded in company documentation
- Gracefully handle queries that cannot be answered
- Maintain a friendly, professional tone at all times

### 1.3 Non-Goals
- Real-time voice processing (batch processing only)
- Multi-language support (English only for v1)
- Sentiment analysis or call scoring
- Integration with specific CRM systems

---

## 2. System Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Docker Environment                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      FastAPI Application                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │Transcription│  │ Guardrails  │  │    RAG Pipeline     │   │  │
│  │  │   Service   │  │   Service   │  │  ┌──────┐ ┌──────┐  │   │  │
│  │  │             │  │             │  │  │Embed │ │Retrieve│ │   │  │
│  │  │ Faster-     │  │ Input/Output│  │  │dings │ │  r    │  │   │  │
│  │  │ Whisper     │  │ Validation  │  │  └──────┘ └──────┘  │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                │                                      │
│  ┌─────────────────┐    ┌─────┴─────┐    ┌─────────────────────┐   │
│  │    ChromaDB     │    │  Ollama   │    │   Volume Mounts     │   │
│  │  (Vector Store) │    │  (LLM)    │    │  - /data/audio      │   │
│  │                 │    │  Mistral  │    │  - /data/knowledge  │   │
│  └─────────────────┘    └───────────┘    └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
1. INPUT PHASE
   MP3 File → Faster-Whisper → Raw Transcript

2. GUARDRAIL PHASE (Input)
   Raw Transcript → PII Detection → Topic Classification → Sanitized Query
   
3. RETRIEVAL PHASE
   Sanitized Query → Embedding → ChromaDB Search → Relevant Documents

4. GENERATION PHASE
   Query + Documents → Ollama/Mistral → Raw Response

5. GUARDRAIL PHASE (Output)
   Raw Response → Confidence Check → Tone Check → Final Response

6. OUTPUT PHASE
   Final Response → API Response (JSON)
```

---

## 3. Component Specifications

### 3.1 Transcription Service

**Technology:** Faster-Whisper (CTranslate2 optimized Whisper)

**Model:** `base.en` (English only, good speed/accuracy balance)

**Configuration:**
```python
{
    "model_size": "base.en",
    "device": "cpu",           # Use "cuda" if GPU available
    "compute_type": "int8",    # Quantized for speed
    "beam_size": 5,
    "best_of": 5,
    "language": "en"
}
```

**Input Requirements:**
- Format: MP3, WAV, M4A, FLAC
- Max duration: 10 minutes
- Max file size: 25MB

**Output:**
```python
{
    "text": "transcribed text here",
    "segments": [...],         # Word-level timestamps
    "language": "en",
    "duration": 45.2
}
```

### 3.2 Guardrails Service

#### 3.2.1 Input Guardrails

| Guard | Purpose | Action |
|-------|---------|--------|
| PII Detection | Detect personal information | Redact with [REDACTED] |
| Profanity Filter | Detect abusive language | Flag for review, sanitize |
| Length Check | Prevent oversized inputs | Truncate with warning |
| Topic Classification | Check if query is in-scope | Route or reject |
| Injection Detection | Prevent prompt injection | Sanitize or reject |

**PII Patterns Detected:**
- Phone numbers: `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`
- Email addresses: `\b[\w.-]+@[\w.-]+\.\w+\b`
- SSN: `\b\d{3}-\d{2}-\d{4}\b`
- Credit cards: `\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b`

#### 3.2.2 Output Guardrails

| Guard | Purpose | Action |
|-------|---------|--------|
| Confidence Check | Verify retrieval quality | Fallback if below threshold |
| Hallucination Check | Ensure grounded response | Reject ungrounded claims |
| Tone Check | Maintain professional tone | Adjust language |
| Length Check | Prevent overly long responses | Summarize |

**Confidence Thresholds:**
```python
{
    "high_confidence": 0.85,    # Answer directly
    "medium_confidence": 0.70,  # Answer with caveat
    "low_confidence": 0.50,     # Suggest escalation
    "no_confidence": 0.0        # Use fallback response
}
```

### 3.3 RAG Pipeline

#### 3.3.1 Document Processing

**Supported Formats:** PDF, TXT, MD, DOCX

**Chunking Strategy:**
```python
{
    "chunk_size": 500,         # Characters per chunk
    "chunk_overlap": 50,       # Overlap between chunks
    "separators": ["\n\n", "\n", ". ", " "]
}
```

#### 3.3.2 Embedding Model

**Model:** `sentence-transformers/all-MiniLM-L6-v2`

**Specifications:**
- Dimensions: 384
- Max sequence length: 256 tokens
- Speed: ~14,000 sentences/second on CPU

#### 3.3.3 Vector Store

**Technology:** ChromaDB

**Configuration:**
```python
{
    "collection_name": "knowledge_base",
    "distance_function": "cosine",
    "persist_directory": "/data/chroma"
}
```

#### 3.3.4 Retrieval

**Strategy:** Maximum Marginal Relevance (MMR)

```python
{
    "k": 4,                    # Number of documents to retrieve
    "fetch_k": 20,             # Candidates to consider for MMR
    "lambda_mult": 0.5         # Diversity factor
}
```

### 3.4 LLM Service

**Technology:** Ollama with Mistral 7B

**Configuration:**
```python
{
    "model": "mistral",
    "temperature": 0.1,        # Low for factual responses
    "max_tokens": 512,
    "top_p": 0.9,
    "repeat_penalty": 1.1
}
```

**System Prompt:**
```
You are a helpful customer service assistant. Your role is to answer 
questions based ONLY on the provided context. 

Rules:
1. Only use information from the provided context
2. If the context doesn't contain the answer, say so politely
3. Never make up information
4. Be concise and friendly
5. If unsure, offer to connect with a human agent

Context:
{context}

Question: {question}

Answer:
```

---

## 4. API Specification

### 4.1 Endpoints

#### POST /process
Process an audio file and get a response.

**Request:**
```
Content-Type: multipart/form-data
- audio: file (MP3, WAV, etc.)
```

**Response:**
```json
{
    "success": true,
    "transcript": "What is your refund policy?",
    "response": "Our refund policy allows returns within 30 days...",
    "confidence": 0.89,
    "processing_time_ms": 2340
}
```

#### POST /query
Query with text directly (skip transcription).

**Request:**
```json
{
    "text": "What is your refund policy?",
    "conversation_id": "optional-uuid"
}
```

**Response:**
```json
{
    "success": true,
    "response": "Our refund policy allows returns within 30 days...",
    "confidence": 0.89,
    "sources": ["refund-policy.pdf", "faq.md"]
}
```

#### GET /health
Health check endpoint.

**Response:**
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

#### POST /knowledge/ingest
Ingest documents into knowledge base.

**Request:**
```
Content-Type: multipart/form-data
- documents: file[] (PDF, TXT, MD)
```

#### GET /knowledge/stats
Get knowledge base statistics.

**Response:**
```json
{
    "total_documents": 45,
    "total_chunks": 892,
    "last_updated": "2024-01-15T10:30:00Z"
}
```

---

## 5. Fallback Response Strategy

### 5.1 Response Decision Tree

```
IF confidence >= 0.85:
    → Return answer directly
    
ELIF confidence >= 0.70:
    → Return answer with: "Based on our documentation..."
    
ELIF confidence >= 0.50:
    → Return partial answer with: "I found some related information, 
       but you may want to verify with our team..."
       
ELSE:
    → Use fallback response
```

### 5.2 Fallback Response Templates

**No Information Found:**
```
I want to make sure I give you accurate information. I couldn't find 
specific details about that in our documentation. Would you like me 
to connect you with someone who can help with this?
```

**Ambiguous Query:**
```
I'd be happy to help! Could you tell me a bit more about what 
you're looking for? For example, are you asking about [option A] 
or [option B]?
```

**Out of Scope:**
```
Thanks for your question! That's outside what I can help with directly, 
but our team would be glad to assist. Would you like me to transfer 
you to a representative?
```

---

## 6. Performance Requirements

| Metric | Target | Maximum |
|--------|--------|---------|
| Transcription time | 0.5x real-time | 1x real-time |
| Query response time | < 3 seconds | 5 seconds |
| API throughput | 10 req/sec | - |
| Memory usage | 4GB | 8GB |

---

## 7. Security Considerations

### 7.1 Data Protection
- All PII is redacted before LLM processing
- Audio files are deleted after processing (configurable)
- No customer data is used for model training

### 7.2 Prompt Injection Prevention
- Input sanitization removes control characters
- System prompts are not exposed to users
- Query length limits prevent overflow attacks

### 7.3 Access Control
- API key authentication (optional)
- Rate limiting per client
- Audit logging of all queries

---

## 8. Deployment Requirements

### 8.1 Minimum Hardware
- CPU: 4 cores
- RAM: 8GB
- Storage: 20GB SSD
- No GPU required (but recommended)

### 8.2 Recommended Hardware
- CPU: 8 cores
- RAM: 16GB
- Storage: 50GB SSD
- GPU: NVIDIA with 8GB+ VRAM (optional)

### 8.3 Docker Resources
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 4G
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G
```

---

## 9. Future Enhancements

### Phase 2
- Multi-language support
- Streaming responses
- Conversation memory
- Custom fine-tuned models

### Phase 3
- Real-time audio processing
- Sentiment analysis
- Integration with CRM systems
- Analytics dashboard
