"""Génération de numéros de téléphone à partir des opérateurs d'un pays."""

from __future__ import annotations

from local_fake.engine.models import Operator, TelecomData
from local_fake.utils.random_utils import digits, pick


def pick_operator(telecom: TelecomData, operator: str | None = None) -> Operator:
    if operator is None:
        return pick(telecom.operators)
    for candidate in telecom.operators:
        if candidate.name == operator:
            return candidate
    known = ", ".join(candidate.name for candidate in telecom.operators)
    raise ValueError(f"Opérateur inconnu « {operator} », opérateurs disponibles : {known}")


def generate_phone_number(
    telecom: TelecomData,
    phone_length: int,
    *,
    operator: str | None = None,
    international: bool = False,
    country_code: str | None = None,
) -> str:
    """Génère un numéro national de `phone_length` chiffres pour un opérateur donné.

    Si `international` est vrai, préfixe le résultat avec `country_code`
    (ex: "+225").
    """
    op = pick_operator(telecom, operator)
    prefix = pick(op.prefixes)
    remaining = phone_length - len(prefix)
    if remaining < 0:
        raise ValueError(
            f"phone_length ({phone_length}) est plus court que le préfixe « {prefix} » de {op.name}"
        )
    number = prefix + digits(remaining)
    if international:
        if not country_code:
            raise ValueError("country_code est requis pour générer un numéro international")
        return f"{country_code}{number}"
    return number


def generate_landline_number(telecom: TelecomData, phone_length: int) -> str:
    """Génère un numéro de ligne fixe à partir de `telecom.landline_prefixes`."""
    prefix = pick(telecom.landline_prefixes)
    remaining = phone_length - len(prefix)
    if remaining < 0:
        raise ValueError(f"phone_length ({phone_length}) est plus court que le préfixe fixe « {prefix} »")
    return prefix + digits(remaining)


def generate_imei() -> str:
    """Génère un IMEI (15 chiffres) valide au sens de l'algorithme de Luhn.

    Ne dépend d'aucune donnée de pays : la structure TAC/numéro de série est
    normalisée par la GSMA au niveau mondial.
    """
    body = digits(14)
    total = 0
    for index, char in enumerate(reversed(body)):
        value = int(char)
        if index % 2 == 0:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    check_digit = (10 - total % 10) % 10
    return f"{body}{check_digit}"
