"""Génération de noms et d'attributs de personnes à partir des données d'un pays."""

from __future__ import annotations

from typing import Literal

from local_fake.engine.models import AddressData, PersonData
from local_fake.utils.random_utils import pick

Gender = Literal["male", "female"]

# Statuts civils génériques : pas assez de variance culturelle documentée à ce
# stade pour justifier une liste par pays plutôt qu'un pool commun.
_MARITAL_STATUSES: tuple[str, ...] = ("célibataire", "marié(e)", "divorcé(e)", "veuf(ve)")


def generate_first_name(person: PersonData, gender: Gender | None = None) -> str:
    gender = gender or pick(("male", "female"))
    pool = person.first_names_male if gender == "male" else person.first_names_female
    return pick(pool)


def generate_last_name(person: PersonData) -> str:
    return pick(person.last_names)


def generate_full_name(person: PersonData, gender: Gender | None = None) -> str:
    return f"{generate_first_name(person, gender)} {generate_last_name(person)}"


def generate_occupation(person: PersonData) -> str:
    """Choisit une profession dans `person.occupations` (liste optionnelle du pays)."""
    return pick(person.occupations)


def generate_marital_status() -> str:
    return pick(_MARITAL_STATUSES)


def generate_birth_place(address: AddressData) -> str:
    """Réutilise le pool de villes de `address` comme lieu de naissance."""
    return pick(address.cities)
