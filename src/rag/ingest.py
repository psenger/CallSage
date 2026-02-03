"""
Document Ingestion Module.

Handles loading, chunking, and ingesting documents into the vector store.
Run this module directly to ingest documents from the knowledge base folder.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import structlog
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.settings import settings
from src.rag.vectorstore import VectorStore

logger = structlog.get_logger()

# Supported file extensions
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


class DocumentLoader:
    """Load documents from various file formats."""

    @staticmethod
    def load_text(file_path: Path) -> str:
        """Load plain text or markdown file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def load_pdf(file_path: Path) -> str:
        """Load PDF file."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
            return "\n\n".join(text_parts)
        except ImportError:
            logger.error("pypdf not installed, cannot load PDF")
            return ""

    @staticmethod
    def load_docx(file_path: Path) -> str:
        """Load DOCX file."""
        try:
            from docx import Document

            doc = Document(file_path)
            text_parts = []
            for para in doc.paragraphs:
                text_parts.append(para.text)
            return "\n\n".join(text_parts)
        except ImportError:
            logger.error("python-docx not installed, cannot load DOCX")
            return ""

    @classmethod
    def load(cls, file_path: Path) -> str:
        """
        Load document based on file extension.

        Args:
            file_path: Path to document

        Returns:
            Document text content
        """
        ext = file_path.suffix.lower()

        if ext in {".txt", ".md"}:
            return cls.load_text(file_path)
        elif ext == ".pdf":
            return cls.load_pdf(file_path)
        elif ext == ".docx":
            return cls.load_docx(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return ""


class DocumentChunker:
    """Split documents into chunks for embedding."""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        """
        Initialize chunker.

        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks.

        Args:
            text: Document text
            metadata: Metadata to attach to each chunk

        Returns:
            List of chunk dicts with content and metadata
        """
        metadata = metadata or {}

        # Split text
        chunks = self.splitter.split_text(text)

        # Create chunk documents
        chunk_docs = []
        for i, chunk_text in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "chunk_count": len(chunks),
            }

            chunk_docs.append({
                "content": chunk_text,
                "metadata": chunk_metadata,
                "id": f"{metadata.get('source', 'doc')}_{i}",
            })

        return chunk_docs


async def ingest_documents(
    knowledge_base_path: str = "/data/knowledge_base",
    clear_existing: bool = False,
) -> Dict[str, Any]:
    """
    Ingest all documents from the knowledge base folder.

    Args:
        knowledge_base_path: Path to knowledge base folder
        clear_existing: Whether to clear existing documents first

    Returns:
        Summary of ingestion results
    """
    logger.info("Starting document ingestion", path=knowledge_base_path)

    # Initialize components
    vectorstore = VectorStore()
    await vectorstore.initialize()

    loader = DocumentLoader()
    chunker = DocumentChunker()

    # Clear if requested
    if clear_existing:
        logger.info("Clearing existing documents")
        await vectorstore.clear()

    # Find documents
    kb_path = Path(knowledge_base_path)
    if not kb_path.exists():
        logger.error("Knowledge base path does not exist", path=knowledge_base_path)
        return {"error": "Path does not exist"}

    documents = []
    for ext in SUPPORTED_EXTENSIONS:
        documents.extend(kb_path.glob(f"*{ext}"))
        documents.extend(kb_path.glob(f"**/*{ext}"))  # Recursive

    logger.info(f"Found {len(documents)} documents")

    # Process each document
    results = {
        "total_documents": 0,
        "total_chunks": 0,
        "documents": [],
        "errors": [],
    }

    for doc_path in documents:
        try:
            logger.info(f"Processing: {doc_path.name}")

            # Load document
            text = loader.load(doc_path)
            if not text:
                logger.warning(f"Empty document: {doc_path.name}")
                continue

            # Create metadata
            metadata = {
                "source": doc_path.name,
                "file_type": doc_path.suffix,
                "ingested_at": datetime.utcnow().isoformat(),
            }

            # Chunk document
            chunks = chunker.chunk(text, metadata)
            logger.info(f"Created {len(chunks)} chunks from {doc_path.name}")

            # Add to vector store
            await vectorstore.add_documents(chunks)

            results["total_documents"] += 1
            results["total_chunks"] += len(chunks)
            results["documents"].append({
                "name": doc_path.name,
                "chunks": len(chunks),
            })

        except Exception as e:
            logger.error(f"Error processing {doc_path.name}: {e}")
            results["errors"].append({
                "document": doc_path.name,
                "error": str(e),
            })

    logger.info(
        "Ingestion complete",
        documents=results["total_documents"],
        chunks=results["total_chunks"],
    )

    return results


# Run directly for CLI ingestion
if __name__ == "__main__":
    import sys

    # Parse arguments
    clear = "--clear" in sys.argv
    path = "/data/knowledge_base"

    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            path = arg

    print(f"Ingesting documents from: {path}")
    if clear:
        print("Will clear existing documents first")

    # Run ingestion
    result = asyncio.run(ingest_documents(path, clear))

    # Print results
    print("\n" + "=" * 50)
    print("INGESTION COMPLETE")
    print("=" * 50)
    print(f"Documents processed: {result.get('total_documents', 0)}")
    print(f"Total chunks created: {result.get('total_chunks', 0)}")

    if result.get("errors"):
        print(f"\nErrors: {len(result['errors'])}")
        for err in result["errors"]:
            print(f"  - {err['document']}: {err['error']}")

    print()
