"""Petites fonctions aléatoires réutilisées par tous les générateurs.

Passent toutes par le générateur partagé de `local_fake.rng` plutôt que par
le module `random` directement, pour que `local_fake.seed(...)` les rende
reproductibles.
"""

from __future__ import annotations

import string
from collections.abc import Sequence
from typing import TypeVar

from local_fake.rng import get_rng

T = TypeVar("T")


def pick(seq: Sequence[T]) -> T:
    """Choisit un élément au hasard dans une séquence non vide."""
    return get_rng().choice(seq)


def digits(length: int) -> str:
    """Génère une suite de `length` chiffres (des zéros initiaux possibles)."""
    rng = get_rng()
    return "".join(rng.choice(string.digits) for _ in range(length))


def shuffled(value: str) -> str:
    """Retourne une permutation aléatoire des caractères de `value`."""
    chars = list(value)
    get_rng().shuffle(chars)
    return "".join(chars)
