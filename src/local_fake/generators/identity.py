"""Génération de pièces d'identité (CNI, ...) à partir du format d'un pays."""

from __future__ import annotations

from local_fake.engine.models import CountryInfo
from local_fake.generators.pattern import generate_from_pattern
from local_fake.utils.random_utils import pick

# Niveaux KYC génériques (BCEAO/UEMOA et la plupart des régulateurs Mobile
# Money distinguent 3 paliers selon le plafond de transaction autorisé) :
# pas de variance par pays justifiant une liste dédiée dans le YAML.
_KYC_TIERS: tuple[str, ...] = ("tier1", "tier2", "tier3")


def generate_cni_number(country: CountryInfo) -> str:
    """Génère un numéro de CNI conforme à `country.cni_format`."""
    return generate_from_pattern(country.cni_format)


def generate_passport_number(country: CountryInfo) -> str:
    """Génère un numéro de passeport conforme à `country.passport_format`."""
    return generate_from_pattern(country.passport_format)


def generate_document_number(pattern: str) -> str:
    """Génère un numéro de document conforme à `pattern` (section `documents` du YAML)."""
    return generate_from_pattern(pattern)


def generate_kyc_tier() -> str:
    return pick(_KYC_TIERS)
