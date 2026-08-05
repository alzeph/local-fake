"""Point d'entrée public de la librairie."""

from __future__ import annotations

from local_fake.cache import UniqueCache
from local_fake.files.provider import FileProvider
from local_fake.providers.base import BaseProvider
from local_fake.providers.supra import SupraProvider
from local_fake.proxy import UniqueProxy
from local_fake.rng import seed as _seed


class LocalFake(BaseProvider, SupraProvider):
    """Générateur de fausses données localisées pour l'Afrique.

    - `LocalFake().first_name()` — une valeur générique : `BaseProvider`
      n'a pas de données propres, donc il tire un pays au hasard parmi
      ceux enregistrés dans `SupraProvider` et lui délègue l'appel.
    - `LocalFake().ci.first_name()` — une valeur spécifique à un pays, via
      l'attribut `ci` fourni par `SupraProvider`.
    - `LocalFake().unique.first_name()` / `.unique.ci.first_name()` — les
      mêmes méthodes, garanties uniques pour la durée de vie de l'instance.
    - `LocalFake().file.pdf()` / `.word()` / `.png()` / `.svg()` / `.excel()`
      — génération de fichiers de test, indépendante de tout pays.
    - `LocalFake(seed=42)` (équivalent à `local_fake.seed(42)` avant la
      construction) — deux exécutions avec la même graine produisent la
      même séquence de données. La graine est partagée par TOUTES les
      instances du process (comme `Faker.seed()`) : elle n'affecte que le
      générateur interne de local-fake, jamais le module `random` global.
    """

    def __init__(self, seed: int | float | str | bytes | None = None) -> None:
        if seed is not None:
            _seed(seed)
        SupraProvider.__init__(self)
        BaseProvider.__init__(self, registry=self)
        self._cache = UniqueCache()
        self.unique = UniqueProxy(self, self._cache)
        self.file = FileProvider()
