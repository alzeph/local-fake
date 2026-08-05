"""Proxy transparent qui rend n'importe quel provider "unique"."""

from __future__ import annotations

from typing import Any

from local_fake.cache import UniqueCache
from local_fake.exceptions import UniquenessExhaustedError
from local_fake.providers.base import BaseProvider

_MAX_ATTEMPTS = 1000


class UniqueProxy:
    """Reflète la surface d'un provider en garantissant l'unicité des valeurs.

    `LocalFake.unique` enveloppe `LocalFake` lui-même ; accéder à
    `local.unique.ci` renvoie récursivement un `UniqueProxy` autour de
    `local.ci`. Ainsi `local.unique.first_name()` et
    `local.unique.ci.first_name()` utilisent exactement la même syntaxe que
    leurs équivalents non uniques.
    """

    def __init__(self, target: BaseProvider, cache: UniqueCache, namespace: str = "root") -> None:
        self._target = target
        self._cache = cache
        self._namespace = namespace

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._target, name)

        if isinstance(attr, BaseProvider):
            return UniqueProxy(attr, self._cache, namespace=name)

        if callable(attr):
            return self._wrap(name, attr)

        return attr

    def _wrap(self, name: str, func):
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (self._namespace, name, args, tuple(sorted(kwargs.items())))
            for _ in range(_MAX_ATTEMPTS):
                value = func(*args, **kwargs)
                if self._cache.add(key, value):
                    return value
            raise UniquenessExhaustedError(
                f"Impossible d'obtenir une nouvelle valeur unique pour "
                f"« {self._namespace}.{name} » après {_MAX_ATTEMPTS} tentatives : "
                "le pool de valeurs disponibles est probablement épuisé."
            )

        return wrapper
