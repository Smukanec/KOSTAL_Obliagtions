"""Placeholder API client for KOSTAL GPT."""

from typing import Dict


def ask(message: str, config: Dict) -> str:
    """Return response from KOSTAL GPT service (placeholder)."""
    # In real implementation this would call LangChain/OpenAI with provided config
    return f"ECHO: {message}"
