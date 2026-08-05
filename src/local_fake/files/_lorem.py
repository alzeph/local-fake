"""Texte de remplissage générique (Word, PDF) pour atteindre une taille de fichier cible."""

from __future__ import annotations

from local_fake.rng import get_rng

_WORDS: tuple[str, ...] = (
    "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
    "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
    "magna", "aliqua", "enim", "minim", "veniam", "quis", "nostrud", "exercitation",
)  # fmt: skip


def filler_paragraph(word_count: int = 80) -> str:
    rng = get_rng()
    return " ".join(rng.choice(_WORDS) for _ in range(word_count))
