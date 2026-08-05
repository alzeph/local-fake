"""Génération de SVG minimalistes (un rectangle coloré), avec remplissage pour la taille cible."""

from __future__ import annotations

import string

from local_fake.exceptions import InvalidFileSizeError
from local_fake.rng import get_rng

_DEFAULT_SIDE = 200
_PADDING_OVERHEAD = len("<!---->")


def _base_svg(side: int) -> str:
    fill = f"#{get_rng().randint(0, 0xFFFFFF):06x}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{side}" height="{side}">'
        f'<rect width="{side}" height="{side}" fill="{fill}" /></svg>'
    )


def generate_svg_bytes(*, min_size: int, max_size: int) -> bytes:
    base = _base_svg(_DEFAULT_SIDE)
    content = base.encode("utf-8")
    if len(content) > max_size:
        raise InvalidFileSizeError(
            f"Impossible de générer un SVG valide sous {max_size} octets "
            f"(taille minimale obtenue : {len(content)} octets)."
        )

    if len(content) < min_size:
        needed = max(0, min_size - len(content) - _PADDING_OVERHEAD)
        padding = "".join(get_rng().choices(string.ascii_letters, k=needed))
        base = base.replace("</svg>", f"<!--{padding}--></svg>")
        content = base.encode("utf-8")

    if len(content) > max_size:
        raise InvalidFileSizeError(
            f"L'intervalle [{min_size}, {max_size}] est trop étroit pour un SVG "
            f"(taille obtenue avec remplissage minimal : {len(content)} octets)."
        )
    return content
