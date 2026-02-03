"""
Input Guardrails Service.

Processes incoming queries to detect and handle:
- PII (Personally Identifiable Information)
- Profanity and abusive language
- Prompt injection attempts
- Out-of-scope queries
"""

import re
from typing import Any, Dict, List

import structlog
from better_profanity import profanity

from config.settings import settings

logger = structlog.get_logger()


class InputGuardrails:
    """
    Input validation and sanitization service.

    Applies multiple guardrails to incoming text to ensure
    safe and appropriate processing.
    """

    # PII Detection Patterns
    PII_PATTERNS = {
        "phone": r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "ssn": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
        "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    }

    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore (?:all )?(?:previous |prior )?instructions",
        r"disregard (?:all )?(?:previous |prior )?instructions",
        r"forget (?:all )?(?:previous |prior )?instructions",
        r"you are now",
        r"act as",
        r"pretend (?:to be|you are)",
        r"new persona",
        r"system prompt",
        r"<\|.*?\|>",  # Token markers
        r"\[INST\]",
        r"\[/INST\]",
    ]

    # Fallback responses
    FALLBACK_RESPONSES = {
        "pii_blocked": (
            "I noticed your message might contain personal information. "
            "For your security, I've removed that information. "
            "Could you please rephrase your question without including "
            "personal details like phone numbers or email addresses?"
        ),
        "profanity_blocked": (
            "I'm here to help, but I noticed some strong language in your message. "
            "Could you please rephrase your question? I want to make sure "
            "I can assist you effectively."
        ),
        "injection_blocked": (
            "I'm sorry, but I couldn't process that request. "
            "Could you please rephrase your question in a different way?"
        ),
        "too_long": (
            "Your message is quite long. Could you please summarize your "
            "main question? I'll be happy to help once I understand "
            "what you're looking for."
        ),
        "out_of_scope": (
            "That's an interesting question! However, it's outside the "
            "areas I can help with. Is there something else I can assist "
            "you with today?"
        ),
    }

    def __init__(self):
        """Initialize guardrails."""
        # Load profanity filter
        profanity.load_censor_words()

        # Compile regex patterns
        self.pii_compiled = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.PII_PATTERNS.items()
        }

        self.injection_compiled = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.INJECTION_PATTERNS
        ]

        logger.info("Input guardrails initialized")

    def process(self, text: str) -> Dict[str, Any]:
        """
        Process text through all input guardrails.

        Args:
            text: Input text to process

        Returns:
            Dict containing:
                - passed: Whether text passed all guardrails
                - sanitized_text: Cleaned text (if passed)
                - flags: Dict of what was detected
                - fallback_response: Response to use if blocked
        """
        result = {
            "passed": True,
            "sanitized_text": text,
            "flags": {
                "pii_detected": False,
                "pii_types": [],
                "profanity_detected": False,
                "injection_detected": False,
                "in_scope": True,
                "length_exceeded": False,
            },
            "fallback_response": None,
        }

        # Check length
        if len(text) > settings.max_input_length:
            result["flags"]["length_exceeded"] = True
            if settings.pii_action == "reject":
                result["passed"] = False
                result["fallback_response"] = self.FALLBACK_RESPONSES["too_long"]
                return result
            else:
                # Truncate
                text = text[: settings.max_input_length]
                result["sanitized_text"] = text

        # Check for PII
        if settings.enable_pii_detection:
            pii_result = self._detect_pii(text)
            if pii_result["detected"]:
                result["flags"]["pii_detected"] = True
                result["flags"]["pii_types"] = pii_result["types"]

                if settings.pii_action == "reject":
                    result["passed"] = False
                    result["fallback_response"] = self.FALLBACK_RESPONSES["pii_blocked"]
                    return result
                elif settings.pii_action == "redact":
                    text = pii_result["sanitized"]
                    result["sanitized_text"] = text

        # Check for profanity
        if settings.enable_profanity_filter:
            if profanity.contains_profanity(text):
                result["flags"]["profanity_detected"] = True
                # Censor profanity but continue
                text = profanity.censor(text)
                result["sanitized_text"] = text

        # Check for prompt injection
        if settings.enable_injection_detection:
            if self._detect_injection(text):
                result["flags"]["injection_detected"] = True
                result["passed"] = False
                result["fallback_response"] = self.FALLBACK_RESPONSES["injection_blocked"]
                return result

        logger.info(
            "Input guardrails processed",
            passed=result["passed"],
            flags=result["flags"],
        )

        return result

    def _detect_pii(self, text: str) -> Dict[str, Any]:
        """
        Detect and optionally redact PII from text.

        Returns:
            Dict with detected flag, types found, and sanitized text
        """
        detected_types = []
        sanitized = text

        for pii_type, pattern in self.pii_compiled.items():
            matches = pattern.findall(text)
            if matches:
                detected_types.append(pii_type)
                # Redact
                redaction = f"[{pii_type.upper()}_REDACTED]"
                sanitized = pattern.sub(redaction, sanitized)

        return {
            "detected": len(detected_types) > 0,
            "types": detected_types,
            "sanitized": sanitized,
        }

    def _detect_injection(self, text: str) -> bool:
        """
        Detect potential prompt injection attempts.

        Returns:
            True if injection pattern detected
        """
        text_lower = text.lower()

        for pattern in self.injection_compiled:
            if pattern.search(text_lower):
                logger.warning(
                    "Prompt injection detected",
                    pattern=pattern.pattern,
                )
                return True

        return False

    def _check_scope(self, text: str) -> bool:
        """
        Check if query is in scope for the knowledge base.

        This is a placeholder - implement based on your specific
        use case (e.g., topic classification model).

        Returns:
            True if query is in scope
        """
        # TODO: Implement topic classification
        # For now, assume all queries are in scope
        return True
