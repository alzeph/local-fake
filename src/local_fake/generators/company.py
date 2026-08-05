"""Génération de noms d'entreprises et de secteurs d'activité."""

from __future__ import annotations

from local_fake.engine.models import CompanyData, PersonData
from local_fake.generators.person import generate_last_name
from local_fake.utils.random_utils import pick

# Secteurs génériques : pas assez de variance documentée par pays pour
# justifier une liste dédiée dans chaque YAML plutôt qu'un pool commun.
_BUSINESS_SECTORS: tuple[str, ...] = (
    "Commerce général",
    "Agriculture",
    "BTP",
    "Transport",
    "Télécommunications",
    "Services financiers",
    "Santé",
    "Éducation",
    "Industrie agroalimentaire",
    "Artisanat",
)

_NAME_TEMPLATES: tuple[str, ...] = (
    "Établissements {name} {suffix}",
    "Groupe {name} {suffix}",
    "{name} & Fils",
    "Ets {name} {suffix}",
)


def generate_company_name(person: PersonData, company: CompanyData) -> str:
    """Compose un nom d'entreprise plausible à partir d'un nom de famille local."""
    name = generate_last_name(person)
    suffix = pick(company.suffixes)
    template = pick(_NAME_TEMPLATES)
    return template.format(name=name, suffix=suffix)


def generate_business_sector() -> str:
    return pick(_BUSINESS_SECTORS)
