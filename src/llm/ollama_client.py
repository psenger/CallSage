"""
Ollama LLM Client.

Handles communication with Ollama for text generation.
"""

from typing import Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings

logger = structlog.get_logger()


# System prompt template for RAG
SYSTEM_PROMPT = """You are a helpful and friendly customer service assistant. Your role is to answer questions based on the provided context from our documentation.

IMPORTANT RULES:
1. ONLY use information from the provided context to answer questions
2. If the context doesn't contain the answer, politely say you don't have that information
3. NEVER make up or guess at information
4. Be concise but complete in your answers
5. Maintain a warm, professional, and helpful tone
6. If you're unsure, it's better to say so than to provide incorrect information
7. Offer to connect the customer with a human agent if the question is outside your knowledge

Remember: The customer is calling for help. Be patient and understanding."""


class OllamaClient:
    """
    Client for interacting with Ollama LLM service.

    Handles prompt construction, API communication, and
    response generation for RAG queries.
    """

    def __init__(self):
        """Initialize Ollama client."""
        self.base_url = settings.ollama_host
        self.model = settings.ollama_model
        self.client = httpx.AsyncClient(timeout=60.0)

        logger.info(
            "Ollama client initialized",
            base_url=self.base_url,
            model=self.model,
        )

    async def verify_connection(self) -> bool:
        """
        Verify connection to Ollama and model availability.

        Returns:
            True if connected and model is available

        Raises:
            Exception if connection fails
        """
        try:
            # Check Ollama is running
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()

            # Check model is available
            data = response.json()
            available_models = [m["name"] for m in data.get("models", [])]

            # Model name might include tag
            model_available = any(
                self.model in m or m.startswith(self.model)
                for m in available_models
            )

            if not model_available:
                logger.warning(
                    "Model not found locally, will be pulled on first use",
                    model=self.model,
                    available=available_models,
                )

            return True

        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama", url=self.base_url)
            raise Exception(f"Cannot connect to Ollama at {self.base_url}")
        except Exception as e:
            logger.error("Ollama verification failed", error=str(e))
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate a response using the LLM.

        Args:
            query: User's question
            context: Retrieved context from knowledge base
            system_prompt: Optional custom system prompt

        Returns:
            Generated response text
        """
        logger.info(
            "Generating response",
            query_length=len(query),
            context_length=len(context),
        )

        # Build the prompt
        system = system_prompt or SYSTEM_PROMPT

        # Construct the full prompt with context
        prompt = f"""Context from our documentation:
---
{context}
---

Customer question: {query}

Please provide a helpful response based on the context above. If the context doesn't contain relevant information, let the customer know politely."""

        # Make API request
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {
                        "temperature": settings.llm_temperature,
                        "num_predict": settings.llm_max_tokens,
                        "top_p": settings.llm_top_p,
                        "repeat_penalty": settings.llm_repeat_penalty,
                    },
                },
            )
            response.raise_for_status()

            data = response.json()
            generated_text = data.get("response", "")

            logger.info(
                "Response generated",
                response_length=len(generated_text),
                eval_count=data.get("eval_count"),
            )

            return generated_text.strip()

        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise Exception("Request timed out. Please try again.")
        except httpx.HTTPError as e:
            logger.error("Ollama HTTP error", error=str(e))
            raise
        except Exception as e:
            logger.error("Generation failed", error=str(e))
            raise

    async def generate_with_chat(
        self,
        query: str,
        context: str,
        chat_history: Optional[list] = None,
    ) -> str:
        """
        Generate response using chat format (for multi-turn conversations).

        Args:
            query: User's question
            context: Retrieved context
            chat_history: Optional list of previous messages

        Returns:
            Generated response text
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)

        # Add context and current query
        user_message = f"""Based on this context from our documentation:

{context}

Please answer: {query}"""

        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": settings.llm_temperature,
                        "num_predict": settings.llm_max_tokens,
                    },
                },
            )
            response.raise_for_status()

            data = response.json()
            return data.get("message", {}).get("content", "").strip()

        except Exception as e:
            logger.error("Chat generation failed", error=str(e))
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
