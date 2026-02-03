.PHONY: help start stop logs health test clean docs openapi

help:
	@echo "CallSage Testing Commands"
	@echo "========================="
	@echo ""
	@echo "Setup & Control:"
	@echo "  make start         - Start all Docker services"
	@echo "  make stop          - Stop all Docker services"
	@echo "  make logs          - Show Docker logs"
	@echo "  make health        - Check API health"
	@echo ""
	@echo "Database:"
	@echo "  make stats         - Show knowledge base statistics"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run general API tests"
	@echo "  make test-chat     - Quick chat test"
	@echo "  make test-audio    - Quick audio test (requires audio file)"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs          - Open Swagger UI in browser"
	@echo "  make redoc         - Open ReDoc in browser"
	@echo "  make openapi       - Download OpenAPI spec as JSON"
	@echo "  make validate      - Validate OpenAPI spec"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove document files from data/"
	@echo "  make reset         - Reset knowledge base (clear all documents)"

start:
	@echo "🚀 Starting CallSage services..."
	docker compose up -d
	@echo "✅ Services started. Waiting for health check..."
	@sleep 10
	@make health

stop:
	@echo "🛑 Stopping CallSage services..."
	docker compose down

logs:
	docker compose logs -f

health:
	@echo "🏥 Checking API health..."
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ API not responding"

stats:
	@echo "📊 Knowledge Base Statistics:"
	@curl -s http://localhost:8000/knowledge/stats | python3 -m json.tool || echo "❌ API not responding"

test:
	@echo "🧪 Running general API tests..."
	python3 test_api.py

test-chat:
	@echo "💬 Testing chat endpoint..."
	@curl -s -X POST http://localhost:8000/query \
		-H "Content-Type: application/json" \
		-d '{"text": "What does this insurance policy cover?"}' | python3 -m json.tool

test-audio:
	@echo "🎤 Testing audio endpoint..."
	@if [ -f data/audio/test.mp3 ]; then \
		curl -s -X POST http://localhost:8000/process \
			-F "audio=@data/audio/test.mp3" | python3 -m json.tool; \
	else \
		echo "❌ No audio file found at data/audio/test.mp3"; \
		echo "Create one with: make create-audio-sample"; \
	fi

create-audio-sample:
	@echo "🎙️ Creating sample audio query..."
	@say -o data/audio/test.aiff "What does my insurance policy cover?"
	@ffmpeg -y -i data/audio/test.aiff data/audio/test.mp3 2>/dev/null || \
		echo "❌ ffmpeg not installed. Install with: brew install ffmpeg"
	@rm -f data/audio/test.aiff
	@echo "✅ Created data/audio/test.mp3"

clean:
	@echo "🗑️ Cleaning document files from data/knowledge_base..."
	@find data/knowledge_base -name "*.md" ! -name "example_faq.md" -delete
	@echo "✅ Cleaned"

reset:
	@echo "⚠️  Resetting knowledge base..."
	@curl -s -X POST http://localhost:8000/knowledge/ingest \
		-F "clear_existing=true" | python3 -m json.tool
	@echo "✅ Knowledge base reset"

# Documentation commands
docs:
	@echo "📖 Opening Swagger UI..."
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "Open http://localhost:8000/docs in your browser"

redoc:
	@echo "📖 Opening ReDoc..."
	@open http://localhost:8000/redoc || xdg-open http://localhost:8000/redoc || echo "Open http://localhost:8000/redoc in your browser"

openapi:
	@echo "📥 Downloading OpenAPI spec..."
	@curl -s http://localhost:8000/openapi.json | python3 -m json.tool > openapi-generated.json
	@echo "✅ Saved to openapi-generated.json"

validate:
	@echo "✅ Validating OpenAPI spec..."
	@if command -v npx >/dev/null 2>&1; then \
		npx @apidevtools/swagger-cli validate openapi.yaml; \
	else \
		echo "⚠️  Install Node.js to use validation"; \
		echo "The YAML file should be valid - manually check at https://editor.swagger.io/"; \
	fi

# Quick workflow
quick-start: start
	@echo ""
	@echo "🎉 Services started!"
	@echo "Next: Load your documents into data/knowledge_base/"
	@echo "Then: make test-chat"
	@echo "Or view API docs: make docs"
