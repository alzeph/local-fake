"""Génération de documents PDF (.pdf) de remplissage."""

from __future__ import annotations

from local_fake.files._determinism import FIXED_TIMESTAMP
from local_fake.files._lorem import filler_paragraph
from local_fake.files._optional import optional_import
from local_fake.files.sizing import grow_until_in_range


def generate_pdf_bytes(*, min_size: int, max_size: int) -> bytes:
    FPDF = optional_import("fpdf", feature="pdf").FPDF

    def build(extra_pages: int) -> bytes:
        pdf = FPDF()
        pdf.set_creation_date(FIXED_TIMESTAMP)
        pdf.set_font("Helvetica", size=12)
        for _ in range(extra_pages + 1):
            pdf.add_page()
            pdf.multi_cell(0, 10, filler_paragraph())
        return bytes(pdf.output())

    return grow_until_in_range(build=build, min_size=min_size, max_size=max_size, format_name="PDF")
