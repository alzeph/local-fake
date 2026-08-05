"""FileProvider : génération de fichiers binaires de test (PDF, Word, PNG, SVG, Excel).

Contrairement aux providers pays, cette classe ne dépend d'aucune donnée de
localisation : elle est exposée une seule fois, au niveau racine de
`LocalFake`, via `local.file.*`, et se combine librement avec les
générateurs pays existants (ex: `local.file.excel(data={"Nom": [local.ci.first_name() for _ in range(10)]})`).
"""

from __future__ import annotations

from pathlib import Path

from local_fake.files.excel import ExcelData, generate_excel_bytes
from local_fake.files.image import generate_png_bytes
from local_fake.files.pdf import generate_pdf_bytes
from local_fake.files.svg import generate_svg_bytes
from local_fake.files.word import generate_word_bytes

# (min, max) par défaut quand ni min_size ni max_size ne sont fournis.
# Chaque plancher tient compte du poids incompressible du format vide côté
# lib utilisée (ex: le template par défaut de python-docx pèse ~36 Ko à lui
# seul, bien avant tout contenu de remplissage).
_DEFAULT_SIZE_RANGES: dict[str, tuple[int, int]] = {
    "svg": (1_000, 3_000),
    "png": (20_000, 80_000),
    "pdf": (10_000, 30_000),
    "word": (40_000, 60_000),
    "excel": (6_000, 20_000),
}


def _resolve_range(kind: str, min_size: int | None, max_size: int | None) -> tuple[int, int]:
    default_min, default_max = _DEFAULT_SIZE_RANGES[kind]
    resolved_min = default_min if min_size is None else min_size
    resolved_max = default_max if max_size is None else max_size
    if resolved_min > resolved_max:
        raise ValueError(f"min_size ({resolved_min}) ne peut pas dépasser max_size ({resolved_max})")
    return resolved_min, resolved_max


class FileProvider:
    """Générateurs de fichiers, indépendants de tout pays."""

    @staticmethod
    def _write(content: bytes, path: str | Path | None) -> bytes:
        if path is not None:
            Path(path).write_bytes(content)
        return content

    def svg(
        self, *, min_size: int | None = None, max_size: int | None = None, path: str | Path | None = None
    ) -> bytes:
        lo, hi = _resolve_range("svg", min_size, max_size)
        return self._write(generate_svg_bytes(min_size=lo, max_size=hi), path)

    def png(
        self,
        *,
        min_size: int | None = None,
        max_size: int | None = None,
        width: int | None = None,
        height: int | None = None,
        path: str | Path | None = None,
    ) -> bytes:
        lo, hi = _resolve_range("png", min_size, max_size)
        return self._write(generate_png_bytes(min_size=lo, max_size=hi, width=width, height=height), path)

    def pdf(
        self, *, min_size: int | None = None, max_size: int | None = None, path: str | Path | None = None
    ) -> bytes:
        lo, hi = _resolve_range("pdf", min_size, max_size)
        return self._write(generate_pdf_bytes(min_size=lo, max_size=hi), path)

    def word(
        self, *, min_size: int | None = None, max_size: int | None = None, path: str | Path | None = None
    ) -> bytes:
        lo, hi = _resolve_range("word", min_size, max_size)
        return self._write(generate_word_bytes(min_size=lo, max_size=hi), path)

    def excel(
        self,
        data: ExcelData = None,
        *,
        min_size: int | None = None,
        max_size: int | None = None,
        path: str | Path | None = None,
    ) -> bytes:
        lo, hi = _resolve_range("excel", min_size, max_size)
        return self._write(generate_excel_bytes(data, min_size=lo, max_size=hi), path)
