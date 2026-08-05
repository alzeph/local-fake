"""Génération d'adresses email à partir d'un nom et prénom."""

from __future__ import annotations

import unicodedata

from local_fake.rng import get_rng
from local_fake.utils.random_utils import pick

_DOMAINS: tuple[str, ...] = ("gmail.com", "yahoo.fr", "outlook.com", "hotmail.com")
_SEPARATORS: tuple[str, ...] = (".", "_", "")


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return "".join(char for char in normalized.lower() if char.isalnum())


def generate_email(first_name: str, last_name: str) -> str:
    rng = get_rng()
    separator = pick(_SEPARATORS)
    local_part = f"{_slugify(first_name)}{separator}{_slugify(last_name)}"
    if rng.random() < 0.3:
        local_part += str(rng.randint(1, 99))
    domain = pick(_DOMAINS)
    return f"{local_part}@{domain}"
