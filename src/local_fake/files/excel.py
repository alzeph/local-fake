"""Génération de classeurs Excel (.xlsx), avec en-têtes/données optionnelles.

`data` peut être :
- `None` : classeur avec une feuille vide (taille atteinte par remplissage) ;
- une `list[str]` : utilisée telle quelle comme ligne d'en-tête, sans données ;
- un `dict[str, list]` : les clés deviennent les en-têtes de colonnes, chaque
  valeur la liste des cellules de cette colonne. Les colonnes plus courtes
  que la plus longue sont complétées par des cellules vides.
"""

from __future__ import annotations

import io
import string
from typing import Any

from local_fake.files._determinism import FIXED_TIMESTAMP, freeze_zip_timestamps
from local_fake.files._optional import optional_import
from local_fake.files.sizing import grow_until_in_range
from local_fake.rng import get_rng

ExcelData = list[str] | dict[str, list[Any]] | None

_FILLER_ROWS_PER_UNIT = 20
_FILLER_TEXT_LENGTH = 100


def _fill_sheet(sheet, data: ExcelData) -> None:
    if data is None:
        return
    if isinstance(data, dict):
        headers = list(data.keys())
        sheet.append(headers)
        columns = list(data.values())
        row_count = max((len(column) for column in columns), default=0)
        for row_index in range(row_count):
            sheet.append([column[row_index] if row_index < len(column) else None for column in columns])
    elif isinstance(data, list):
        sheet.append(list(data))
    else:
        raise TypeError("data doit être None, une list (en-têtes) ou un dict {colonne: [valeurs]}")


def generate_excel_bytes(data: ExcelData, *, min_size: int, max_size: int) -> bytes:
    Workbook = optional_import("openpyxl", feature="excel").Workbook

    def build(padding_units: int) -> bytes:
        workbook = Workbook()
        workbook.properties.created = FIXED_TIMESTAMP
        workbook.properties.modified = FIXED_TIMESTAMP
        sheet = workbook.active
        sheet.title = "Data"
        _fill_sheet(sheet, data)

        if padding_units > 0:
            filler_sheet = workbook.create_sheet("_padding")
            filler_sheet.sheet_state = "hidden"
            rng = get_rng()
            for _ in range(padding_units * _FILLER_ROWS_PER_UNIT):
                text = "".join(rng.choices(string.ascii_letters, k=_FILLER_TEXT_LENGTH))
                filler_sheet.append([text])

        buffer = io.BytesIO()
        workbook.save(buffer)
        return freeze_zip_timestamps(buffer.getvalue())

    return grow_until_in_range(build=build, min_size=min_size, max_size=max_size, format_name="Excel")
