"""Provider Côte d'Ivoire."""

from __future__ import annotations

from local_fake.providers.base import BaseProvider


class ProviderCI(BaseProvider):
    """Données ivoiriennes, chargées depuis `data/countries/ci.yaml`.

    Ne surcharge aucune méthode pour l'instant : le YAML de base suffit aux
    générateurs génériques de `BaseProvider`. Une particularité locale (ex.
    format d'adresse propre à la Côte d'Ivoire) s'ajouterait ici en
    surchargeant uniquement la méthode concernée.
    """

    yaml_file = "ci.yaml"
    country_code = "CI"
