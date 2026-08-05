"""Génération de dates génériques (naissance, délivrance/expiration de documents).

Ces dates ne dépendent d'aucune donnée de pays : l'âge légal, la durée de
validité d'un document, etc. sont des paramètres passés par l'appelant.
"""

from __future__ import annotations

import datetime

from local_fake.rng import get_rng


def generate_birth_date(*, min_age: int = 18, max_age: int = 90) -> datetime.date:
    """Génère une date de naissance correspondant à un âge entre `min_age` et `max_age`."""
    rng = get_rng()
    today = datetime.date.today()
    age = rng.randint(min_age, max_age)
    birth_year = today.year - age
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)  # évite les problèmes de jours invalides (février, ...)
    return datetime.date(birth_year, month, day)


def generate_issue_date(*, years_ago_max: int = 10) -> datetime.date:
    """Génère une date de délivrance dans les `years_ago_max` dernières années."""
    today = datetime.date.today()
    days_ago = get_rng().randint(0, years_ago_max * 365)
    return today - datetime.timedelta(days=days_ago)


def generate_expiry_date(issue_date: datetime.date, *, validity_years: int = 10) -> datetime.date:
    """Calcule une date d'expiration à `validity_years` après `issue_date`."""
    try:
        return issue_date.replace(year=issue_date.year + validity_years)
    except ValueError:
        # 29 février sur une année non bissextile.
        return issue_date.replace(year=issue_date.year + validity_years, day=28)
