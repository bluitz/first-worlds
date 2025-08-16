"""commands.py

Tiny, forgiving text command mapping for material generation.

Example commands:
- make the floor wet cobblestone at night
- make selection stone
- make object cube metal

We don't do NLP here; we perform keyword matching to choose a style.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


STYLE_KEYWORDS = {
    "checker": ["checker", "grid"],
    "stone": ["stone", "rock", "cobble", "cobblestone"],
    "metal": ["metal", "steel", "chrome"],
}


def infer_style_from_prompt(prompt: str, default: str = "checker") -> str:
    text = prompt.lower()
    for style, keywords in STYLE_KEYWORDS.items():
        if any(k in text for k in keywords):
            return style
    # fallback by simple adjectives
    if "wet" in text and ("stone" in text or "cobble" in text):
        return "stone"
    if "shiny" in text or "chrome" in text:
        return "metal"
    return default
