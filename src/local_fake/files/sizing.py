"""Aide générique pour amener un contenu généré dans un intervalle [min_size, max_size].

S'applique aux formats qu'on peut faire grossir en augmentant une quantité de
contenu de remplissage (pages, paragraphes, lignes, ...) sans casser leur
structure — jamais en tronquant les octets, ce qui produirait un fichier
corrompu. `build(n)` reconstruit le document EN ENTIER avec `n` unités de
remplissage à chaque tentative plutôt que de muter un objet partagé : certains
formats (ex. fpdf2) invalident leur état interne dès qu'ils ont été sérialisés
une première fois.
"""

from __future__ import annotations

from typing import Callable

from local_fake.exceptions import InvalidFileSizeError

_MAX_PADDING_ATTEMPTS = 200


def grow_until_in_range(
    *,
    build: Callable[[int], bytes],
    min_size: int,
    max_size: int,
    format_name: str,
) -> bytes:
    """Appelle `build(n)` avec `n` croissant jusqu'à tomber dans [min_size, max_size]."""
    content = build(0)
    if len(content) > max_size:
        raise InvalidFileSizeError(
            f"Impossible de générer un fichier {format_name} valide sous {max_size} octets "
            f"(taille minimale obtenue : {len(content)} octets)."
        )

    attempts = 0
    while len(content) < min_size:
        if attempts >= _MAX_PADDING_ATTEMPTS:
            raise InvalidFileSizeError(
                f"Impossible d'atteindre {min_size} octets pour un fichier {format_name} "
                f"après {_MAX_PADDING_ATTEMPTS} tentatives de remplissage "
                f"(dernière taille obtenue : {len(content)} octets)."
            )
        attempts += 1
        content = build(attempts)
        if len(content) > max_size:
            raise InvalidFileSizeError(
                f"Le remplissage a dépassé max_size ({max_size} octets) pour un fichier "
                f"{format_name} avant d'atteindre min_size ({min_size} octets) : "
                "l'intervalle demandé est probablement trop étroit."
            )
    return content
