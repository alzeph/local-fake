"""Cache interne utilisé par `LocalFake.unique` pour garantir l'unicité."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Hashable


class UniqueCache:
    """Mémorise les valeurs déjà servies, par espace de noms.

    Chaque combinaison (provider, méthode, arguments) a son propre espace :
    un prénom masculin unique et un prénom féminin unique peuvent coïncider
    sans être considérés comme un doublon, de même que deux pays différents.
    """

    def __init__(self) -> None:
        self._seen: dict[Hashable, set[Any]] = defaultdict(set)

    def add(self, key: Hashable, value: Any) -> bool:
        """Enregistre `value` sous `key`. Retourne False si déjà vue."""
        bucket = self._seen[key]
        if value in bucket:
            return False
        bucket.add(value)
        return True

    def reset(self, key: Hashable | None = None) -> None:
        """Vide le cache entièrement, ou seulement pour `key`."""
        if key is None:
            self._seen.clear()
        else:
            self._seen.pop(key, None)
