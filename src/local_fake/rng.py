"""Générateur aléatoire partagé par toute la librairie.

Une seule instance de `random.Random`, plutôt que le module `random` global
utilisé directement : `seed()` rend les données reproductibles sans modifier
l'état aléatoire du reste du programme qui utilise local-fake (contrairement
à `random.seed()`, qui affecterait tout le process, y compris du code sans
rapport avec cette librairie).

Le générateur est partagé entre toutes les instances de `LocalFake`, comme
dans la librairie Faker : `seed()` a un effet global à tout le process pour
CE générateur précis, afin qu'un seul appel rende déterministe l'intégralité
d'une suite de tests, quel que soit le nombre d'instances créées.
"""

from __future__ import annotations

import random

_rng = random.Random()


def seed(value: int | float | str | bytes | None = None) -> None:
    """Fixe la graine : deux exécutions avec la même graine produisent les mêmes données."""
    _rng.seed(value)


def get_rng() -> random.Random:
    return _rng
