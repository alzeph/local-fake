"""Génération de documents Word (.docx) de remplissage."""

from __future__ import annotations

import io

from local_fake.files._determinism import freeze_zip_timestamps
from local_fake.files._lorem import filler_paragraph
from local_fake.files._optional import optional_import
from local_fake.files.sizing import grow_until_in_range


def generate_word_bytes(*, min_size: int, max_size: int) -> bytes:
    Document = optional_import("docx", feature="word").Document

    def build(extra_paragraphs: int) -> bytes:
        document = Document()
        document.add_heading("Document généré", level=1)
        for _ in range(extra_paragraphs + 1):
            document.add_paragraph(filler_paragraph())
        buffer = io.BytesIO()
        document.save(buffer)
        return freeze_zip_timestamps(buffer.getvalue())

    return grow_until_in_range(build=build, min_size=min_size, max_size=max_size, format_name="Word")
