"""
Vector Store Service.

Manages ChromaDB operations for document storage and retrieval.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import chromadb
import structlog
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from config.settings import settings

logger = structlog.get_logger()


class VectorStore:
    """
    ChromaDB vector store for document embeddings.

    Handles document storage, embedding generation, and
    similarity search for RAG retrieval.
    """

    def __init__(self):
        """Initialize vector store connection."""
        self.client: Optional[chromadb.HttpClient] = None
        self.collection = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self._initialized = False

    async def initialize(self):
        """
        Initialize connection to ChromaDB and load embedding model.
        """
        if self._initialized:
            return

        logger.info(
            "Initializing vector store",
            host=settings.chroma_host,
            port=settings.chroma_port,
        )

        # Connect to ChromaDB
        self.client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            ),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )

        # Load embedding model
        logger.info("Loading embedding model", model=settings.embedding_model)
        self.embedding_model = SentenceTransformer(settings.embedding_model)

        self._initialized = True
        logger.info(
            "Vector store initialized",
            collection=settings.chroma_collection,
            embedding_dimensions=self.embedding_model.get_sentence_embedding_dimension(),
        )

    async def health_check(self) -> bool:
        """
        Check if ChromaDB is healthy.

        Returns:
            True if healthy
        """
        if not self.client:
            raise Exception("Vector store not initialized")

        # Attempt to heartbeat
        self.client.heartbeat()
        return True

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
    ) -> int:
        """
        Add documents to the vector store.

        Args:
            documents: List of dicts with 'content', 'metadata', and optional 'id'

        Returns:
            Number of documents added
        """
        if not self._initialized:
            await self.initialize()

        logger.info("Adding documents to vector store", count=len(documents))

        # Prepare data
        ids = []
        contents = []
        metadatas = []

        for i, doc in enumerate(documents):
            doc_id = doc.get("id", f"doc_{datetime.utcnow().timestamp()}_{i}")
            ids.append(doc_id)
            contents.append(doc["content"])
            metadatas.append(doc.get("metadata", {}))

        # Generate embeddings
        embeddings = self.embedding_model.encode(contents).tolist()

        # Add to collection
        self.collection.add(
            ids=ids,
            documents=contents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info("Documents added successfully", count=len(documents))
        return len(documents)

    async def search(
        self,
        query: str,
        top_k: int = 4,
        filter_metadata: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of matching documents with relevance scores
        """
        if not self._initialized:
            await self.initialize()

        logger.info("Searching vector store", query_length=len(query), top_k=top_k)

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                # Convert distance to relevance (cosine distance to similarity)
                distance = results["distances"][0][i] if results["distances"] else 0
                relevance = 1 - distance  # Cosine similarity

                formatted_results.append({
                    "content": doc,
                    "document": results["metadatas"][0][i].get("source", "unknown")
                    if results["metadatas"]
                    else "unknown",
                    "chunk_id": results["ids"][0][i] if results["ids"] else f"chunk_{i}",
                    "relevance": round(relevance, 4),
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                })

        logger.info(
            "Search complete",
            results_count=len(formatted_results),
            top_relevance=formatted_results[0]["relevance"] if formatted_results else 0,
        )

        return formatted_results

    async def delete_document(self, document_name: str) -> int:
        """
        Delete a document and all its chunks.

        Args:
            document_name: Name of document to delete

        Returns:
            Number of chunks deleted
        """
        if not self._initialized:
            await self.initialize()

        # Get all chunks for this document
        results = self.collection.get(
            where={"source": document_name},
            include=["metadatas"],
        )

        if not results["ids"]:
            return 0

        # Delete chunks
        self.collection.delete(ids=results["ids"])

        logger.info(
            "Document deleted",
            document=document_name,
            chunks_deleted=len(results["ids"]),
        )

        return len(results["ids"])

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dict with stats
        """
        if not self._initialized:
            await self.initialize()

        # Get collection count
        count = self.collection.count()

        # Get unique documents
        results = self.collection.get(include=["metadatas"])
        unique_docs = set()
        doc_info = {}

        for i, metadata in enumerate(results["metadatas"] or []):
            source = metadata.get("source", "unknown")
            unique_docs.add(source)

            if source not in doc_info:
                doc_info[source] = {
                    "name": source,
                    "chunks": 0,
                    "ingested_at": metadata.get("ingested_at", None),
                }
            doc_info[source]["chunks"] += 1

        return {
            "total_documents": len(unique_docs),
            "total_chunks": count,
            "embedding_model": settings.embedding_model,
            "embedding_dimensions": self.embedding_model.get_sentence_embedding_dimension()
            if self.embedding_model
            else 384,
            "last_updated": datetime.utcnow().isoformat(),
            "documents": list(doc_info.values()),
        }

    async def clear(self):
        """Clear all documents from the collection."""
        if not self._initialized:
            await self.initialize()

        # Delete and recreate collection
        self.client.delete_collection(settings.chroma_collection)
        self.collection = self.client.create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )

        logger.info("Vector store cleared")
