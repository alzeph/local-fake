"""Génération d'images PNG de bruit aléatoire, dimensionnées pour une taille cible.

Le bruit RGB est volontairement incompressible : contrairement à une image
unie, sa taille finale suit à peu près sa surface en pixels, ce qui permet
une recherche par dimensions plutôt qu'un remplissage "élément par élément"
comme pour les autres formats. Généré via le générateur partagé de
`local_fake.rng` (et non `os.urandom`) pour rester reproductible sous
`local_fake.seed(...)`.
"""

from __future__ import annotations

import io

from local_fake.exceptions import InvalidFileSizeError
from local_fake.files._optional import optional_import
from local_fake.rng import get_rng

_MAX_SEARCH_ATTEMPTS = 30
_INITIAL_SIDE = 16
_GROWTH_FACTOR = 1.3


def _render_noise_png(width: int, height: int) -> bytes:
    pil_image = optional_import("PIL.Image", feature="png")
    raw = get_rng().randbytes(width * height * 3)
    image = pil_image.frombytes("RGB", (width, height), raw)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_png_bytes(
    *, min_size: int, max_size: int, width: int | None = None, height: int | None = None
) -> bytes:
    if width is not None and height is not None:
        content = _render_noise_png(width, height)
        if not (min_size <= len(content) <= max_size):
            raise InvalidFileSizeError(
                f"L'image {width}x{height} pèse {len(content)} octets, hors de l'intervalle "
                f"demandé [{min_size}, {max_size}]. Ajustez width/height, ou omettez-les pour "
                "laisser local-fake chercher des dimensions adaptées."
            )
        return content

    side = _INITIAL_SIDE
    content = _render_noise_png(side, side)
    attempts = 0
    while len(content) < min_size:
        if attempts >= _MAX_SEARCH_ATTEMPTS:
            raise InvalidFileSizeError(
                f"Impossible de trouver des dimensions produisant une image PNG d'au moins "
                f"{min_size} octets après {_MAX_SEARCH_ATTEMPTS} essais "
                f"(dernier essai : {side}x{side} = {len(content)} octets)."
            )
        side = int(side * _GROWTH_FACTOR) + 1
        content = _render_noise_png(side, side)
        attempts += 1

    if len(content) > max_size:
        raise InvalidFileSizeError(
            f"Aucune dimension trouvée pour une image PNG entre {min_size} et {max_size} octets "
            f"(dernier essai : {side}x{side} = {len(content)} octets). Passez width/height "
            "explicitement pour un contrôle plus fin."
        )
    return content
