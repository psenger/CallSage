"""
Pydantic models for API request and response schemas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Health & Status Schemas
# =============================================================================


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Overall system status")
    components: Dict[str, str] = Field(..., description="Status of each component")
    version: str = Field(..., description="API version")


# =============================================================================
# Query Schemas
# =============================================================================


class QueryRequest(BaseModel):
    """Text query request."""

    text: str = Field(..., description="Query text", max_length=2000)
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")


class SourceInfo(BaseModel):
    """Information about a source document."""

    document: str = Field(..., description="Document name")
    chunk_id: str = Field(..., description="Chunk identifier")
    relevance: float = Field(..., description="Relevance score (0-1)")


class ProcessResponse(BaseModel):
    """Response from audio processing endpoint."""

    success: bool = Field(..., description="Whether processing succeeded")
    request_id: str = Field(..., description="Unique request identifier")
    transcript: Optional[str] = Field(None, description="Transcribed text from audio")
    response: str = Field(..., description="Generated response")
    confidence: float = Field(..., description="Confidence score (0-1)")
    sources: Optional[List[SourceInfo]] = Field(None, description="Source documents used")
    guardrails: Optional[Dict[str, Any]] = Field(None, description="Guardrail check results")
    processing_time_ms: int = Field(..., description="Total processing time in milliseconds")


class QueryResponse(BaseModel):
    """Response from text query endpoint."""

    success: bool = Field(..., description="Whether query succeeded")
    request_id: str = Field(..., description="Unique request identifier")
    response: str = Field(..., description="Generated response")
    confidence: float = Field(..., description="Confidence score (0-1)")
    sources: Optional[List[SourceInfo]] = Field(None, description="Source documents used")
    fallback_used: bool = Field(False, description="Whether fallback response was used")
    processing_time_ms: int = Field(..., description="Total processing time in milliseconds")


class TranscribeResponse(BaseModel):
    """Response from transcription endpoint."""

    success: bool = Field(..., description="Whether transcription succeeded")
    transcript: str = Field(..., description="Transcribed text")
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="Word-level segments")
    duration: float = Field(..., description="Audio duration in seconds")
    language: str = Field(..., description="Detected language")


# =============================================================================
# Knowledge Base Schemas
# =============================================================================


class DocumentInfo(BaseModel):
    """Information about an ingested document."""

    name: str = Field(..., description="Document filename")
    chunks: int = Field(..., description="Number of chunks")
    ingested_at: datetime = Field(..., description="Ingestion timestamp")


class KnowledgeStatsResponse(BaseModel):
    """Knowledge base statistics."""

    total_documents: int = Field(..., description="Total number of documents")
    total_chunks: int = Field(..., description="Total number of chunks")
    embedding_model: str = Field(..., description="Embedding model name")
    embedding_dimensions: int = Field(..., description="Embedding vector dimensions")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    documents: Optional[List[DocumentInfo]] = Field(None, description="List of documents")


class KnowledgeSearchRequest(BaseModel):
    """Knowledge base search request."""

    query: str = Field(..., description="Search query")
    top_k: int = Field(5, description="Number of results to return", ge=1, le=20)


class SearchResult(BaseModel):
    """Single search result."""

    content: str = Field(..., description="Chunk content")
    document: str = Field(..., description="Source document")
    chunk_id: str = Field(..., description="Chunk identifier")
    relevance: float = Field(..., description="Relevance score")


class KnowledgeSearchResponse(BaseModel):
    """Knowledge base search response."""

    results: List[SearchResult] = Field(..., description="Search results")


class IngestRequest(BaseModel):
    """Document ingestion request."""

    replace: bool = Field(False, description="Replace existing document with same name")


class IngestResponse(BaseModel):
    """Document ingestion response."""

    success: bool = Field(..., description="Whether ingestion succeeded")
    ingested: List[Dict[str, Any]] = Field(..., description="List of ingested documents")
    total_chunks_added: int = Field(..., description="Total chunks created")


# =============================================================================
# Guardrails Schemas
# =============================================================================


class GuardrailCheckRequest(BaseModel):
    """Guardrail check request."""

    text: str = Field(..., description="Text to check", max_length=5000)


class GuardrailFlags(BaseModel):
    """Guardrail flags."""

    pii_detected: bool = Field(False, description="PII was detected")
    pii_types: Optional[List[str]] = Field(None, description="Types of PII found")
    profanity_detected: bool = Field(False, description="Profanity was detected")
    in_scope: bool = Field(True, description="Query is in scope")
    injection_detected: bool = Field(False, description="Prompt injection detected")


class GuardrailCheckResponse(BaseModel):
    """Guardrail check response."""

    original: str = Field(..., description="Original text")
    sanitized: str = Field(..., description="Sanitized text")
    flags: Dict[str, Any] = Field(..., description="Guardrail flags")


# =============================================================================
# Error Schemas
# =============================================================================


class ErrorResponse(BaseModel):
    """Error response."""

    success: bool = Field(False)
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    request_id: Optional[str] = Field(None, description="Request ID if available")
