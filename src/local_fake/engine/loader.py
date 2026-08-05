"""Chargement des fichiers YAML de pays.

Chaque provider pays déclare simplement le nom de son fichier
(`yaml_file = "ci.yaml"`) ; ce module se charge de le localiser dans
`local_fake/data/countries/`, de le parser, de le valider contre la
structure minimale, puis de le transformer en `CountryData` typé.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from local_fake.engine.models import CountryData
from local_fake.exceptions import DataFileNotFoundError
from local_fake.validators.schema import validate_country_schema

COUNTRIES_DIR = Path(__file__).resolve().parent.parent / "data" / "countries"


@lru_cache(maxsize=None)
def load_country_data(yaml_file: str) -> CountryData:
    """Charge, valide et met en cache le YAML `yaml_file` (ex: "ci.yaml")."""
    path = COUNTRIES_DIR / yaml_file
    if not path.is_file():
        raise DataFileNotFoundError(
            f"Fichier de données introuvable pour ce provider : {path}"
        )

    with path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    validate_country_schema(raw, source=yaml_file)
    return CountryData.from_dict(raw)
