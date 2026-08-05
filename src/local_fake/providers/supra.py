"""SupraProvider : découvre et enregistre automatiquement tous les providers pays.

Ajouter un pays au projet se résume à :

1. déposer son YAML dans `data/countries/<code>.yaml` — c'est **suffisant**
   si aucune règle spécifique au pays n'est nécessaire : un provider
   générique (`BaseProvider` avec `yaml_file`/`country_code` déduits du nom
   de fichier) est créé automatiquement ;
2. optionnellement, déposer `providers/countries/<code>.py` avec
   `class Provider<Code>(BaseProvider)` pour surcharger une ou plusieurs
   méthodes — il est détecté et utilisé à la place du générique.

`<code>` (le nom du fichier YAML, sans extension) devient à la fois le nom
d'attribut (`local.<code>`) et le `country_code` par défaut. Aucune
déclaration manuelle n'est nécessaire ici.
"""

from __future__ import annotations

import importlib
import inspect

from local_fake.engine.loader import COUNTRIES_DIR
from local_fake.exceptions import InvalidProviderModuleError, UnknownProviderError
from local_fake.providers.base import BaseProvider
from local_fake.rng import get_rng


class SupraProvider:
    """Registre de tous les providers pays, peuplé par découverte automatique.

    Les providers découverts sont suivis explicitement dans `_country_providers`
    plutôt que retrouvés en scannant `vars(self)` : `LocalFake` hérite à la
    fois de `SupraProvider` ET de `BaseProvider`, et stocke `self._registry =
    self` — un scan naïf de `vars(self)` inclurait alors `self` lui-même
    (un `BaseProvider` valide, `country_code=None`) parmi les "pays"
    disponibles pour la délégation générique, avec un risque de récursion.
    """

    def __init__(self) -> None:
        self._country_providers: dict[str, BaseProvider] = {}
        for yaml_path in sorted(COUNTRIES_DIR.glob("*.yaml")):
            code = yaml_path.stem
            provider_cls = self._resolve_provider_class(code)
            provider = provider_cls(registry=self)
            setattr(self, code, provider)
            self._country_providers[code] = provider

    @staticmethod
    def _resolve_provider_class(code: str) -> type[BaseProvider]:
        """Retourne la classe provider à utiliser pour `code` (ex: "bf")."""
        module_name = f"local_fake.providers.countries.{code}"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            return type(
                f"Provider{code.upper()}",
                (BaseProvider,),
                {"yaml_file": f"{code}.yaml", "country_code": code.upper()},
            )

        candidates = [
            obj
            for _, obj in inspect.getmembers(module, inspect.isclass)
            if issubclass(obj, BaseProvider) and obj is not BaseProvider and obj.__module__ == module_name
        ]
        if not candidates:
            raise InvalidProviderModuleError(
                f"{module_name} existe mais ne définit aucune classe héritant de BaseProvider."
            )
        if len(candidates) > 1:
            names = ", ".join(cls.__name__ for cls in candidates)
            raise InvalidProviderModuleError(
                f"{module_name} définit plusieurs classes BaseProvider ({names}) : "
                "une seule est attendue par fichier."
            )
        return candidates[0]

    def all_providers(self) -> list[BaseProvider]:
        return list(self._country_providers.values())

    def random_provider(self) -> BaseProvider:
        providers = self.all_providers()
        if not providers:
            raise UnknownProviderError("Aucun provider pays n'est enregistré dans SupraProvider.")
        return get_rng().choice(providers)

    def get_provider(self, country_code: str) -> BaseProvider:
        provider = self._country_providers.get(country_code.lower())
        if provider is None:
            raise UnknownProviderError(f"Aucun provider enregistré pour le pays « {country_code} ».")
        return provider
