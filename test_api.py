#!/usr/bin/env python3
"""
Test script for CallSage API - Tests both audio and chat endpoints.
"""

import json
import requests
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health():
    """Test the health endpoint."""
    print_section("Testing Health Endpoint")

    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nSystem Status: {data['status']}")
        print("\nComponents:")
        for component, status in data['components'].items():
            print(f"  - {component}: {status}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_chat(query: str):
    """Test the chat/query endpoint."""
    print_section(f"Testing Chat Endpoint")
    print(f"Query: '{query}'")

    response = requests.post(
        f"{API_BASE_URL}/query",
        json={"text": query}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nSuccess: {data['success']}")
        print(f"Confidence: {data['confidence']:.2f}")
        print(f"\nResponse:\n{data['response']}")

        if data.get('sources'):
            print("\nSources:")
            for i, source in enumerate(data['sources'], 1):
                print(f"  {i}. {source['document']} (relevance: {source['relevance']:.2f})")

        print(f"\nProcessing Time: {data['processing_time_ms']}ms")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_audio(audio_file_path: str):
    """Test the audio processing endpoint."""
    print_section(f"Testing Audio Endpoint")

    audio_path = Path(audio_file_path)
    if not audio_path.exists():
        print(f"Error: Audio file not found: {audio_file_path}")
        return False

    print(f"Audio File: {audio_path.name}")

    with open(audio_path, 'rb') as f:
        files = {'audio': (audio_path.name, f, 'audio/mpeg')}
        response = requests.post(
            f"{API_BASE_URL}/process",
            files=files
        )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nSuccess: {data['success']}")
        print(f"\nTranscript: {data.get('transcript', 'N/A')}")
        print(f"\nConfidence: {data['confidence']:.2f}")
        print(f"\nResponse:\n{data['response']}")

        if data.get('sources'):
            print("\nSources:")
            for i, source in enumerate(data['sources'], 1):
                print(f"  {i}. {source['document']} (relevance: {source['relevance']:.2f})")

        print(f"\nProcessing Time: {data['processing_time_ms']}ms")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_knowledge_stats():
    """Test the knowledge base statistics endpoint."""
    print_section("Testing Knowledge Base Statistics")

    response = requests.get(f"{API_BASE_URL}/knowledge/stats")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal Documents: {data['total_documents']}")
        print(f"Total Chunks: {data['total_chunks']}")
        print(f"Embedding Model: {data['embedding_model']}")
        print(f"Embedding Dimensions: {data['embedding_dimensions']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_ingestion(path: str = None, clear: bool = False):
    """Test the document ingestion endpoint."""
    print_section("Testing Document Ingestion")

    data = {}
    if path:
        data['path'] = path
    if clear:
        data['clear_existing'] = clear

    print(f"Path: {path or '/data/knowledge_base (default)'}")
    print(f"Clear Existing: {clear}")

    response = requests.post(
        f"{API_BASE_URL}/knowledge/ingest",
        data=data
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\nSuccess: {result['success']}")
        print(f"Total Chunks Added: {result['total_chunks_added']}")
        print(f"\nIngested Documents:")
        for doc in result['ingested']:
            print(f"  - {doc['name']}: {doc['chunks']} chunks")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def main():
    """Run all tests."""
    print("\n" + "🚀" * 30)
    print("CallSage API Test Suite")
    print("🚀" * 30)

    # Test 1: Health Check
    if not test_health():
        print("\n❌ Health check failed. Make sure the API is running.")
        return

    # Test 2: Knowledge Base Stats (before ingestion)
    test_knowledge_stats()

    # Test 3: Chat/Text Query
    test_queries = [
        "What is your return policy?",
        "How long does shipping take?",
        "What payment methods do you accept?",
    ]

    for query in test_queries:
        test_chat(query)

    # Test 4: Audio Processing (if audio file exists)
    audio_files = list(Path("data/audio").glob("*.mp3"))
    if audio_files:
        test_audio(str(audio_files[0]))
    else:
        print_section("Audio Test Skipped")
        print("No audio files found in /data/audio/")
        print("Place an MP3 file there to test audio processing.")

    # Final Summary
    print_section("Test Suite Complete")
    print("\n✅ All available tests completed!")
    print("\nNext steps:")
    print("  1. Load documents into data/knowledge_base/")
    print("  2. Ingest with: docker compose exec app python -m src.rag.ingest /data/knowledge_base")
    print("  3. Test queries with: make test-chat")


if __name__ == "__main__":
    main()
