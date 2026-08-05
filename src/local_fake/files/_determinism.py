"""Neutralise les sources de non-déterminisme indépendantes de `local_fake.rng`.

`openpyxl` et `python-docx` horodatent chaque entrée de l'archive zip (xlsx,
docx sont des zips) à l'heure courante (`datetime.now()`) : sans correction,
deux appels avec la même graine produiraient des fichiers différents à
l'octet près malgré des données strictement identiques.
"""

from __future__ import annotations

import datetime
import io
import zipfile

FIXED_TIMESTAMP = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
_FIXED_ZIP_DATE_TIME = (2000, 1, 1, 0, 0, 0)


def freeze_zip_timestamps(content: bytes) -> bytes:
    """Réécrit l'horodatage de chaque entrée d'une archive zip (xlsx/docx) à une date fixe."""
    source = zipfile.ZipFile(io.BytesIO(content))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            item.date_time = _FIXED_ZIP_DATE_TIME
            target.writestr(item, source.read(item.filename))
    return buffer.getvalue()
