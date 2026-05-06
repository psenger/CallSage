"""
Output Guardrails Service.

Processes LLM responses to ensure:
- Appropriate confidence-based responses
- Friendly and professional tone
- Graceful fallbacks when uncertain
"""

from typing import Any, Dict

import structlog

from config.settings import settings

logger = structlog.get_logger()


class OutputGuardrails:
    """
    Output validation and response adjustment service.

    Ensures LLM responses are appropriate, well-calibrated
    to confidence levels, and maintain a friendly tone.
    """

    # Fallback responses based on confidence level
    FALLBACK_RESPONSES = {
        "no_confidence": (
            "I want to make sure I give you accurate information. "
            "I couldn't find specific details about that in our documentation. "
            "Would you like me to connect you with someone who can help with this?"
        ),
        "low_confidence": (
            "I found some related information, but I want to make sure "
            "you get the most accurate answer. You may want to verify this "
            "with our team. Here's what I found:\n\n{response}\n\n"
            "Would you like me to connect you with someone for more details?"
        ),
        "medium_confidence": (
            "Based on our documentation, {response}\n\n"
            "If you need more specific information, I'd be happy to help "
            "you connect with our team."
        ),
    }

    # Phrases that indicate uncertainty in LLM response
    UNCERTAINTY_PHRASES = [
        "i don't know",
        "i'm not sure",
        "i cannot find",
        "there is no information",
        "i don't have information",
        "i'm unable to",
        "i cannot determine",
        "it's unclear",
        "the documentation doesn't",
    ]

    def __init__(self):
        """Initialize output guardrails."""
        logger.info("Output guardrails initialized")

    def process(
        self,
        response: str,
        confidence: float,
    ) -> Dict[str, Any]:
        """
        Process LLM response through output guardrails.

        Args:
            response: Raw LLM response
            confidence: Retrieval confidence score (0-1)

        Returns:
            Dict containing:
                - response: Final response to return
                - confidence_level: Category (high/medium/low/none)
                - fallback_used: Whether fallback was used
                - adjustments: List of adjustments made
        """
        result = {
            "response": response,
            "confidence_level": "high",
            "fallback_used": False,
            "adjustments": [],
        }

        # Check for uncertainty phrases in response
        contains_uncertainty = self._check_uncertainty(response)
        if contains_uncertainty:
            # Override confidence if LLM expresses uncertainty
            confidence = min(confidence, settings.confidence_low - 0.1)
            result["adjustments"].append("uncertainty_detected")

        # Apply confidence-based response strategy
        if confidence >= settings.confidence_high:
            # High confidence - return response as-is
            result["confidence_level"] = "high"
            result["response"] = self._ensure_friendly_tone(response)

        elif confidence >= settings.confidence_medium:
            # Medium confidence - add caveat
            result["confidence_level"] = "medium"
            result["response"] = self.FALLBACK_RESPONSES["medium_confidence"].format(
                response=response
            )
            result["adjustments"].append("caveat_added")

        elif confidence >= settings.confidence_low:
            # Low confidence - suggest verification
            result["confidence_level"] = "low"
            result["response"] = self.FALLBACK_RESPONSES["low_confidence"].format(
                response=response
            )
            result["fallback_used"] = True
            result["adjustments"].append("verification_suggested")

        else:
            # No confidence - use full fallback
            result["confidence_level"] = "none"
            result["response"] = self.FALLBACK_RESPONSES["no_confidence"]
            result["fallback_used"] = True
            result["adjustments"].append("full_fallback")

        # Final tone check
        result["response"] = self._ensure_friendly_tone(result["response"])

        logger.info(
            "Output guardrails processed",
            confidence=confidence,
            confidence_level=result["confidence_level"],
            fallback_used=result["fallback_used"],
        )

        return result

    def _check_uncertainty(self, response: str) -> bool:
        """
        Check if response contains uncertainty phrases.

        Returns:
            True if uncertainty detected
        """
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in self.UNCERTAINTY_PHRASES)

    def _ensure_friendly_tone(self, response: str) -> str:
        """
        Ensure response maintains a friendly, professional tone.

        Args:
            response: Response text

        Returns:
            Adjusted response with friendly tone
        """
        # Remove any harsh or robotic phrases
        replacements = {
            "I cannot help with that": "I'd like to help you find the right answer",
            "That is incorrect": "Let me clarify that",
            "You are wrong": "I understand the confusion",
            "No.": "Not quite, but ",
            "ERROR:": "I encountered an issue:",
        }

        for old, new in replacements.items():
            if old.lower() in response.lower():
                response = response.replace(old, new)
                response = response.replace(old.lower(), new)

        return response

    def format_with_sources(
        self,
        response: str,
        sources: list,
        include_sources: bool = False,
    ) -> str:
        """
        Optionally format response with source attribution.

        Args:
            response: Response text
            sources: List of source documents used
            include_sources: Whether to include source info

        Returns:
            Formatted response
        """
        if not include_sources or not sources:
            return response

        source_text = "\n\nSources consulted:\n"
        for i, source in enumerate(sources[:3], 1):  # Limit to 3 sources
            source_text += f"- {source.get('document', 'Document')}\n"

        return response + source_text
