"""Validation d'une valeur générée contre un motif regex issu du YAML."""

from __future__ import annotations

import re


def matches_pattern(value: str, pattern: str) -> bool:
    """Retourne True si `value` correspond entièrement à `pattern`."""
    return re.fullmatch(pattern, value) is not None
