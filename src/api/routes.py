"""
API Routes for the IVR RAG System.

Defines all HTTP endpoints for processing audio, querying the RAG system,
and managing the knowledge base.
"""

import time
import uuid
from typing import Optional

import structlog
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from config.settings import settings
from src.api.schemas import (
    GuardrailCheckRequest,
    GuardrailCheckResponse,
    HealthResponse,
    IngestResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeStatsResponse,
    ProcessResponse,
    QueryRequest,
    QueryResponse,
    TranscribeResponse,
)
from src.guardrails.input_guards import InputGuardrails
from src.guardrails.output_guards import OutputGuardrails

logger = structlog.get_logger()

router = APIRouter()


# =============================================================================
# Health & Status Endpoints
# =============================================================================


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(request: Request) -> HealthResponse:
    """
    Check system health and component status.
    Returns status of Ollama, ChromaDB, and Whisper.
    """
    components = {}

    # Check Whisper
    try:
        if hasattr(request.app.state, "whisper") and request.app.state.whisper:
            components["whisper"] = "loaded"
        else:
            components["whisper"] = "not_loaded"
    except Exception:
        components["whisper"] = "error"

    # Check ChromaDB
    try:
        if hasattr(request.app.state, "vectorstore"):
            await request.app.state.vectorstore.health_check()
            components["chromadb"] = "connected"
        else:
            components["chromadb"] = "not_initialized"
    except Exception:
        components["chromadb"] = "disconnected"

    # Check Ollama
    try:
        if hasattr(request.app.state, "ollama"):
            await request.app.state.ollama.verify_connection()
            components["ollama"] = "connected"
        else:
            components["ollama"] = "not_initialized"
    except Exception:
        components["ollama"] = "disconnected"

    # Determine overall status
    all_healthy = all(
        v in ["loaded", "connected"] for v in components.values()
    )
    status = "healthy" if all_healthy else "degraded"

    return HealthResponse(
        status=status,
        components=components,
        version="1.0.0",
    )


# =============================================================================
# Query Processing Endpoints
# =============================================================================


@router.post("/process", response_model=ProcessResponse, tags=["Query"])
async def process_audio(
    request: Request,
    audio: UploadFile = File(..., description="Audio file (MP3, WAV, etc.)"),
    max_duration: Optional[int] = Form(None, description="Max audio duration in seconds"),
) -> ProcessResponse:
    """
    Process an audio file through the full pipeline:
    1. Transcribe audio to text
    2. Apply input guardrails
    3. Query RAG system
    4. Apply output guardrails
    5. Return response
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(
        "Processing audio request",
        request_id=request_id,
        filename=audio.filename,
    )

    try:
        # Validate file
        if not audio.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Read audio content
        audio_content = await audio.read()

        # Check file size
        size_mb = len(audio_content) / (1024 * 1024)
        if size_mb > settings.max_audio_size_mb:
            raise HTTPException(
                status_code=400,
                detail=f"Audio file too large (max {settings.max_audio_size_mb}MB)",
            )

        # Transcribe
        whisper = request.app.state.whisper
        transcript_result = whisper.transcribe(audio_content)
        transcript = transcript_result["text"]

        logger.info(
            "Transcription complete",
            request_id=request_id,
            transcript_length=len(transcript),
        )

        # Apply input guardrails
        input_guards = InputGuardrails()
        guard_result = input_guards.process(transcript)

        if not guard_result["passed"]:
            return ProcessResponse(
                success=False,
                request_id=request_id,
                transcript=transcript,
                response=guard_result["fallback_response"],
                confidence=0.0,
                guardrails=guard_result["flags"],
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        sanitized_query = guard_result["sanitized_text"]

        # Query RAG
        vectorstore = request.app.state.vectorstore
        retrieved_docs = await vectorstore.search(
            query=sanitized_query,
            top_k=settings.retrieval_top_k,
        )

        # Generate response with LLM
        ollama = request.app.state.ollama
        context = "\n\n".join([doc["content"] for doc in retrieved_docs])

        llm_response = await ollama.generate(
            query=sanitized_query,
            context=context,
        )

        # Calculate confidence from retrieval scores
        if retrieved_docs:
            avg_relevance = sum(d["relevance"] for d in retrieved_docs) / len(retrieved_docs)
        else:
            avg_relevance = 0.0

        # Apply output guardrails
        output_guards = OutputGuardrails()
        final_response = output_guards.process(
            response=llm_response,
            confidence=avg_relevance,
        )

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(
            "Request processed successfully",
            request_id=request_id,
            confidence=avg_relevance,
            processing_time_ms=processing_time,
        )

        return ProcessResponse(
            success=True,
            request_id=request_id,
            transcript=transcript,
            response=final_response["response"],
            confidence=avg_relevance,
            sources=[
                {
                    "document": doc.get("document", "unknown"),
                    "chunk_id": doc.get("chunk_id", "unknown"),
                    "relevance": doc["relevance"],
                }
                for doc in retrieved_docs
            ],
            guardrails=guard_result["flags"],
            processing_time_ms=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error processing audio",
            request_id=request_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_text(
    request: Request,
    query: QueryRequest,
) -> QueryResponse:
    """
    Query the RAG system with text directly (skip transcription).
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(
        "Processing text query",
        request_id=request_id,
        query_length=len(query.text),
    )

    try:
        # Apply input guardrails
        input_guards = InputGuardrails()
        guard_result = input_guards.process(query.text)

        if not guard_result["passed"]:
            return QueryResponse(
                success=False,
                request_id=request_id,
                response=guard_result["fallback_response"],
                confidence=0.0,
                fallback_used=True,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        sanitized_query = guard_result["sanitized_text"]

        # Query RAG
        vectorstore = request.app.state.vectorstore
        retrieved_docs = await vectorstore.search(
            query=sanitized_query,
            top_k=settings.retrieval_top_k,
        )

        # Generate response with LLM
        ollama = request.app.state.ollama
        context = "\n\n".join([doc["content"] for doc in retrieved_docs])

        llm_response = await ollama.generate(
            query=sanitized_query,
            context=context,
        )

        # Calculate confidence
        if retrieved_docs:
            avg_relevance = sum(d["relevance"] for d in retrieved_docs) / len(retrieved_docs)
        else:
            avg_relevance = 0.0

        # Apply output guardrails
        output_guards = OutputGuardrails()
        final_response = output_guards.process(
            response=llm_response,
            confidence=avg_relevance,
        )

        processing_time = int((time.time() - start_time) * 1000)

        return QueryResponse(
            success=True,
            request_id=request_id,
            response=final_response["response"],
            confidence=avg_relevance,
            sources=[
                {
                    "document": doc.get("document", "unknown"),
                    "chunk_id": doc.get("chunk_id", "unknown"),
                    "relevance": doc["relevance"],
                }
                for doc in retrieved_docs
            ],
            fallback_used=final_response.get("fallback_used", False),
            processing_time_ms=processing_time,
        )

    except Exception as e:
        logger.error(
            "Error processing query",
            request_id=request_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe", response_model=TranscribeResponse, tags=["Query"])
async def transcribe_audio(
    request: Request,
    audio: UploadFile = File(..., description="Audio file"),
) -> TranscribeResponse:
    """
    Transcribe audio file without querying the RAG system.
    Useful for testing transcription quality.
    """
    try:
        audio_content = await audio.read()
        whisper = request.app.state.whisper
        result = whisper.transcribe(audio_content)

        return TranscribeResponse(
            success=True,
            transcript=result["text"],
            segments=result.get("segments", []),
            duration=result.get("duration", 0.0),
            language=result.get("language", "en"),
        )

    except Exception as e:
        logger.error("Transcription error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Knowledge Base Endpoints
# =============================================================================


@router.get("/knowledge/stats", response_model=KnowledgeStatsResponse, tags=["Knowledge Base"])
async def knowledge_stats(request: Request) -> KnowledgeStatsResponse:
    """Get statistics about the knowledge base."""
    try:
        vectorstore = request.app.state.vectorstore
        stats = await vectorstore.get_stats()
        return KnowledgeStatsResponse(**stats)

    except Exception as e:
        logger.error("Error getting knowledge stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/search", response_model=KnowledgeSearchResponse, tags=["Knowledge Base"])
async def knowledge_search(
    request: Request,
    search_request: KnowledgeSearchRequest,
) -> KnowledgeSearchResponse:
    """Search the knowledge base directly (for debugging/testing)."""
    try:
        vectorstore = request.app.state.vectorstore
        results = await vectorstore.search(
            query=search_request.query,
            top_k=search_request.top_k,
        )

        return KnowledgeSearchResponse(results=results)

    except Exception as e:
        logger.error("Error searching knowledge base", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/ingest", response_model=IngestResponse, tags=["Knowledge Base"])
async def ingest_knowledge(
    request: Request,
    path: Optional[str] = Form(None, description="Path to knowledge base folder"),
    clear_existing: bool = Form(False, description="Clear existing documents first"),
) -> IngestResponse:
    """
    Ingest documents from a folder into the knowledge base.
    If no path is provided, uses the default /data/knowledge_base folder.
    """
    try:
        from src.rag.ingest import ingest_documents

        # Use default path if not provided
        ingest_path = path or "/data/knowledge_base"

        logger.info(
            "Starting document ingestion",
            path=ingest_path,
            clear_existing=clear_existing,
        )

        # Run ingestion
        result = await ingest_documents(
            knowledge_base_path=ingest_path,
            clear_existing=clear_existing,
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return IngestResponse(
            success=True,
            ingested=result.get("documents", []),
            total_chunks_added=result.get("total_chunks", 0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error during ingestion", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Guardrails Endpoints
# =============================================================================


@router.post("/guardrails/check", response_model=GuardrailCheckResponse, tags=["Guardrails"])
async def check_guardrails(
    check_request: GuardrailCheckRequest,
) -> GuardrailCheckResponse:
    """Check text against guardrails without processing."""
    input_guards = InputGuardrails()
    result = input_guards.process(check_request.text)

    return GuardrailCheckResponse(
        original=check_request.text,
        sanitized=result["sanitized_text"],
        flags=result["flags"],
    )
