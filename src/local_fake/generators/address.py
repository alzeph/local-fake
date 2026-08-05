"""Génération d'adresses textuelles et de données géographiques d'un pays."""

from __future__ import annotations

from local_fake.engine.models import AddressData
from local_fake.rng import get_rng
from local_fake.utils.random_utils import pick

_AREA_TYPES: tuple[str, ...] = ("urbain", "rural")


def generate_address(address: AddressData) -> str:
    """Génère une adresse textuelle "quartier, repère, ville".

    Beaucoup de pays africains n'ont pas d'adressage postal structuré
    (numéro + nom de rue) : l'usage courant est une description textuelle
    combinant quartier, point de repère et ville — d'où ce format plutôt
    qu'un générateur "numéro + rue" calqué sur les formats occidentaux.
    """
    neighborhood = pick(address.neighborhoods)
    landmark = pick(address.landmarks)
    city = pick(address.cities)
    return f"{neighborhood}, {landmark}, {city}"


def generate_region(address: AddressData) -> str:
    return pick(address.regions)


def generate_gps_coordinates(address: AddressData) -> tuple[float, float]:
    """Génère des coordonnées GPS dans la boîte englobante `address.gps_bounds`."""
    bounds = address.gps_bounds
    rng = get_rng()
    latitude = round(rng.uniform(bounds.min_lat, bounds.max_lat), 6)
    longitude = round(rng.uniform(bounds.min_lon, bounds.max_lon), 6)
    return latitude, longitude


def generate_area_type() -> str:
    return pick(_AREA_TYPES)
