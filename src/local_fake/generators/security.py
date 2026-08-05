"""Génération de mots de passe conformes au format d'un pays.

`password_format` s'appuie en général sur des lookaheads
(`(?=.*[A-Z])...`) qui décrivent des contraintes plutôt qu'un motif
séquentiel : on ne peut donc pas les "dérouler" comme `cni_format` (voir
`local_fake.generators.pattern`). On construit à la place un candidat qui
respecte les exigences usuelles (majuscule, minuscule, chiffre, caractère
spécial, longueur minimale), puis on le valide contre la regex du pays en
réessayant si besoin.
"""

from __future__ import annotations

import string

from local_fake.exceptions import PatternGenerationError
from local_fake.rng import get_rng
from local_fake.validators.pattern import matches_pattern

_LOWER = string.ascii_lowercase
_UPPER = string.ascii_uppercase
_DIGITS = string.digits
_SPECIALS = "!@#$%^&*()_+"
_DEFAULT_LENGTH = 8
_MAX_ATTEMPTS = 50


def _build_candidate(length: int) -> str:
    rng = get_rng()
    required = [
        rng.choice(_UPPER),
        rng.choice(_LOWER),
        rng.choice(_DIGITS),
        rng.choice(_SPECIALS),
    ]
    pool = _LOWER + _UPPER + _DIGITS + _SPECIALS
    filler = [rng.choice(pool) for _ in range(max(length - len(required), 0))]
    chars = required + filler
    rng.shuffle(chars)
    return "".join(chars)


def generate_password(password_format: str, *, length: int = _DEFAULT_LENGTH) -> str:
    length = max(length, _DEFAULT_LENGTH)
    for _ in range(_MAX_ATTEMPTS):
        candidate = _build_candidate(length)
        if matches_pattern(candidate, password_format):
            return candidate
    raise PatternGenerationError(
        f"Impossible de générer un mot de passe conforme à « {password_format} » "
        f"après {_MAX_ATTEMPTS} tentatives. Ce format est peut-être trop spécifique : "
        "surchargez password() dans le provider de ce pays."
    )
