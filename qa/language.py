"""Language detection and translation utilities.

Playwright-independent — strings in, strings out.
"""

from __future__ import annotations
import langdetect


def detect_language(text: str) -> str:
    try:
        return langdetect.detect(text.strip()) if text.strip() else "unknown"
    except Exception:
        return "unknown"


def translate_to_english(text: str) -> str:
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="auto", target="en").translate(text) or text
    except Exception:
        return text


def is_english(text: str) -> bool:
    return detect_language(text) == "en"