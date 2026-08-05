"""Exceptions personnalisées de local_fake."""

from __future__ import annotations


class LocalFakeError(Exception):
    """Racine de toutes les exceptions levées par local_fake."""


class DataFileNotFoundError(LocalFakeError):
    """Le fichier YAML d'un pays est introuvable."""


class SchemaValidationError(LocalFakeError):
    """Le YAML d'un pays ne respecte pas la structure minimale exigée."""


class PatternGenerationError(LocalFakeError):
    """Impossible de générer une valeur conforme à un motif regex."""


class UnknownProviderError(LocalFakeError):
    """Le provider ou le pays demandé n'existe pas."""


class MissingCountryDataError(LocalFakeError):
    """Le pays n'a pas de données pour une section optionnelle (ex: address)."""


class InvalidProviderModuleError(LocalFakeError):
    """Un module providers/countries/<code>.py ne respecte pas la convention attendue."""


class UniquenessExhaustedError(LocalFakeError):
    """Le nombre maximal de tentatives pour obtenir une valeur unique est dépassé."""


class InvalidFileSizeError(LocalFakeError):
    """L'intervalle [min_size, max_size] demandé est irréalisable pour ce type de fichier."""


class MissingOptionalDependencyError(LocalFakeError):
    """Une dépendance optionnelle (extra `files`) requise pour cet appel n'est pas installée."""
