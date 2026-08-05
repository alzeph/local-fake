"""Validation de la structure minimale exigée pour un YAML de pays.

Un contributeur peut ajouter librement de nouvelles sections (adresses,
entreprises, IBAN, ...) et ses propres générateurs pour les exploiter : ce
module ne vérifie que le socle commun (`country`, `person`, `telecom`) sans
lequel `BaseProvider` ne peut pas fonctionner.
"""

from __future__ import annotations

import re
from typing import Any

from local_fake.exceptions import SchemaValidationError

# Champs requis de la section `country` et leur type attendu.
_COUNTRY_FIELDS: dict[str, type] = {
    "name": str,
    "code_alpha2": str,
    "code_alpha3": str,
    "country_code": str,
    "cni_format": str,
    "passport_format": str,
    "phone_length": int,
    "password_format": str,
}

# Champs requis de la section `person` : chacun est une liste non vide de str.
_PERSON_LIST_FIELDS: tuple[str, ...] = (
    "first_names_male",
    "first_names_female",
    "last_names",
)

# Champs optionnels de la section `person`, validés seulement s'ils sont présents.
_PERSON_OPTIONAL_LIST_FIELDS: tuple[str, ...] = ("occupations",)

# Champs requis de la section `address`, SI elle est présente (section optionnelle).
_ADDRESS_LIST_FIELDS: tuple[str, ...] = (
    "cities",
    "neighborhoods",
    "landmarks",
    "regions",
)

# Champs requis de `address.gps_bounds`, SI cette sous-section est présente.
_GPS_BOUNDS_FIELDS: tuple[str, ...] = ("min_lat", "max_lat", "min_lon", "max_lon")

# Champs requis de la section `finance`, SI elle est présente (section optionnelle).
_FINANCE_LIST_FIELDS: tuple[str, ...] = ("banks", "mobile_money_operators")

# Champs requis de la section `company`, SI elle est présente (section optionnelle).
_COMPANY_LIST_FIELDS: tuple[str, ...] = ("suffixes",)


def validate_country_schema(raw: Any, *, source: str = "<yaml>") -> None:
    """Vérifie que `raw` respecte la structure minimale d'un YAML de pays.

    Lève `SchemaValidationError` avec la liste complète des problèmes trouvés
    plutôt que de s'arrêter à la première erreur, pour faciliter la correction
    par la personne qui ajoute le pays.
    """
    errors: list[str] = []

    if not isinstance(raw, dict):
        raise SchemaValidationError(
            f"{source}: le document YAML doit être un mapping, reçu {type(raw).__name__}."
        )

    _validate_country_section(raw, errors)
    _validate_person_section(raw, errors)
    _validate_telecom_section(raw, errors)
    _validate_address_section(raw, errors)
    _validate_documents_section(raw, errors)
    _validate_finance_section(raw, errors)
    _validate_company_section(raw, errors)

    if errors:
        details = "\n".join(f"  - {error}" for error in errors)
        raise SchemaValidationError(f"Structure YAML invalide pour « {source} » :\n{details}")


def _validate_country_section(raw: dict[str, Any], errors: list[str]) -> None:
    section = raw.get("country")
    if not isinstance(section, dict):
        errors.append("section « country » manquante ou n'est pas un mapping")
        return

    for field_name, expected_type in _COUNTRY_FIELDS.items():
        if field_name not in section:
            errors.append(f"country.{field_name} est manquant")
            continue
        value = section[field_name]
        if not isinstance(value, expected_type) or isinstance(value, bool):
            errors.append(
                f"country.{field_name} doit être de type {expected_type.__name__}, "
                f"reçu {type(value).__name__}"
            )

    if "phone_length" in section and isinstance(section["phone_length"], int):
        if section["phone_length"] <= 0:
            errors.append("country.phone_length doit être un entier strictement positif")

    for regex_field in ("cni_format", "passport_format", "password_format"):
        pattern = section.get(regex_field)
        if isinstance(pattern, str):
            try:
                re.compile(pattern)
            except re.error as exc:
                errors.append(f"country.{regex_field} n'est pas une regex valide : {exc}")


def _validate_person_section(raw: dict[str, Any], errors: list[str]) -> None:
    section = raw.get("person")
    if not isinstance(section, dict):
        errors.append("section « person » manquante ou n'est pas un mapping")
        return

    for field_name in _PERSON_LIST_FIELDS:
        if field_name not in section:
            errors.append(f"person.{field_name} est manquant")
            continue
        value = section[field_name]
        if not isinstance(value, list) or not value:
            errors.append(f"person.{field_name} doit être une liste non vide")
            continue
        if not all(isinstance(item, str) and item for item in value):
            errors.append(f"person.{field_name} doit ne contenir que des chaînes non vides")

    for field_name in _PERSON_OPTIONAL_LIST_FIELDS:
        if field_name not in section:
            continue
        value = section[field_name]
        if not isinstance(value, list) or not value:
            errors.append(f"person.{field_name} doit être une liste non vide s'il est présent")
            continue
        if not all(isinstance(item, str) and item for item in value):
            errors.append(f"person.{field_name} doit ne contenir que des chaînes non vides")


def _validate_address_section(raw: dict[str, Any], errors: list[str]) -> None:
    """La section `address` est optionnelle : elle n'est validée que si présente."""
    if "address" not in raw:
        return

    section = raw["address"]
    if not isinstance(section, dict):
        errors.append("section « address » doit être un mapping")
        return

    for field_name in _ADDRESS_LIST_FIELDS:
        if field_name not in section:
            errors.append(f"address.{field_name} est manquant")
            continue
        value = section[field_name]
        if not isinstance(value, list) or not value:
            errors.append(f"address.{field_name} doit être une liste non vide")
            continue
        if not all(isinstance(item, str) and item for item in value):
            errors.append(f"address.{field_name} doit ne contenir que des chaînes non vides")

    if "gps_bounds" in section:
        bounds = section["gps_bounds"]
        if not isinstance(bounds, dict):
            errors.append("address.gps_bounds doit être un mapping {min_lat, max_lat, min_lon, max_lon}")
        else:
            for field_name in _GPS_BOUNDS_FIELDS:
                value = bounds.get(field_name)
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    errors.append(f"address.gps_bounds.{field_name} doit être un nombre")
            if isinstance(bounds.get("min_lat"), (int, float)) and isinstance(bounds.get("max_lat"), (int, float)):
                if bounds["min_lat"] >= bounds["max_lat"]:
                    errors.append("address.gps_bounds.min_lat doit être strictement inférieur à max_lat")
            if isinstance(bounds.get("min_lon"), (int, float)) and isinstance(bounds.get("max_lon"), (int, float)):
                if bounds["min_lon"] >= bounds["max_lon"]:
                    errors.append("address.gps_bounds.min_lon doit être strictement inférieur à max_lon")


def _validate_documents_section(raw: dict[str, Any], errors: list[str]) -> None:
    """La section `documents` est optionnelle : mapping libre {nom_document: regex}."""
    if "documents" not in raw:
        return

    section = raw["documents"]
    if not isinstance(section, dict) or not section:
        errors.append("section « documents » doit être un mapping non vide {nom: regex}")
        return

    for name, pattern in section.items():
        if not isinstance(pattern, str) or not pattern:
            errors.append(f"documents.{name} doit être une chaîne (regex) non vide")
            continue
        try:
            re.compile(pattern)
        except re.error as exc:
            errors.append(f"documents.{name} n'est pas une regex valide : {exc}")


def _validate_finance_section(raw: dict[str, Any], errors: list[str]) -> None:
    """La section `finance` est optionnelle : elle n'est validée que si présente."""
    if "finance" not in raw:
        return

    section = raw["finance"]
    if not isinstance(section, dict):
        errors.append("section « finance » doit être un mapping")
        return

    currency = section.get("currency")
    if not isinstance(currency, str) or not currency:
        errors.append("finance.currency doit être une chaîne non vide")

    for field_name in _FINANCE_LIST_FIELDS:
        if field_name not in section:
            errors.append(f"finance.{field_name} est manquant")
            continue
        value = section[field_name]
        if not isinstance(value, list) or not value:
            errors.append(f"finance.{field_name} doit être une liste non vide")
            continue
        if not all(isinstance(item, str) and item for item in value):
            errors.append(f"finance.{field_name} doit ne contenir que des chaînes non vides")


def _validate_company_section(raw: dict[str, Any], errors: list[str]) -> None:
    """La section `company` est optionnelle : elle n'est validée que si présente."""
    if "company" not in raw:
        return

    section = raw["company"]
    if not isinstance(section, dict):
        errors.append("section « company » doit être un mapping")
        return

    for field_name in _COMPANY_LIST_FIELDS:
        if field_name not in section:
            errors.append(f"company.{field_name} est manquant")
            continue
        value = section[field_name]
        if not isinstance(value, list) or not value:
            errors.append(f"company.{field_name} doit être une liste non vide")
            continue
        if not all(isinstance(item, str) and item for item in value):
            errors.append(f"company.{field_name} doit ne contenir que des chaînes non vides")


def _validate_telecom_section(raw: dict[str, Any], errors: list[str]) -> None:
    section = raw.get("telecom")
    if not isinstance(section, dict):
        errors.append("section « telecom » manquante ou n'est pas un mapping")
        return

    operators = section.get("operators")
    if not isinstance(operators, dict) or not operators:
        errors.append("telecom.operators doit être un mapping non vide {opérateur: {prefixes: [...]}}")
        return

    for operator_name, operator_data in operators.items():
        if not isinstance(operator_data, dict):
            errors.append(f"telecom.operators.{operator_name} doit être un mapping")
            continue
        prefixes = operator_data.get("prefixes")
        if not isinstance(prefixes, list) or not prefixes:
            errors.append(f"telecom.operators.{operator_name}.prefixes doit être une liste non vide")
            continue
        if not all(isinstance(prefix, str) and prefix for prefix in prefixes):
            errors.append(f"telecom.operators.{operator_name}.prefixes doit ne contenir que des chaînes non vides")

    if "landline_prefixes" in section:
        landline_prefixes = section["landline_prefixes"]
        if not isinstance(landline_prefixes, list) or not landline_prefixes:
            errors.append("telecom.landline_prefixes doit être une liste non vide s'il est présent")
        elif not all(isinstance(prefix, str) and prefix for prefix in landline_prefixes):
            errors.append("telecom.landline_prefixes doit ne contenir que des chaînes non vides")
