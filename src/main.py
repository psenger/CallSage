"""
IVR RAG System - Main Application Entry Point

This module initializes the FastAPI application and sets up all routes,
middleware, and event handlers.
"""

import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from src.api.routes import router
from src.llm.ollama_client import OllamaClient
from src.rag.vectorstore import VectorStore
from src.transcription.whisper_service import WhisperService

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
        if settings.log_format == "json"
        else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logging.basicConfig(
    format="%(message)s",
    level=getattr(logging, settings.log_level.upper()),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes services on startup and cleans up on shutdown.
    """
    logger.info("Starting IVR RAG System...")

    # Initialize services
    try:
        # Initialize Whisper
        logger.info("Loading Whisper model...", model=settings.whisper_model)
        app.state.whisper = WhisperService()
        logger.info("Whisper model loaded successfully")

        # Initialize Vector Store
        logger.info("Connecting to ChromaDB...")
        app.state.vectorstore = VectorStore()
        await app.state.vectorstore.initialize()
        logger.info("ChromaDB connected successfully")

        # Initialize Ollama Client
        logger.info("Connecting to Ollama...", host=settings.ollama_host)
        app.state.ollama = OllamaClient()
        await app.state.ollama.verify_connection()
        logger.info("Ollama connected successfully", model=settings.ollama_model)

        logger.info("IVR RAG System started successfully!")

    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise

    yield

    # Cleanup on shutdown
    logger.info("Shutting down IVR RAG System...")
    # Add cleanup logic here if needed


# Create FastAPI application
app = FastAPI(
    title="IVR RAG System",
    description="Process IVR recordings and answer questions using RAG",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint - redirect to docs."""
    return {
        "message": "IVR RAG System API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
