"""Modèles typés représentant les données d'un pays une fois validées.

Ces dataclasses ne portent que la structure MINIMALE garantie par
`local_fake.validators.schema`. Toute section additionnelle ajoutée par un
contributeur dans un YAML de pays reste disponible via `CountryData.raw`
et `CountryData.extra`, sans que le provider n'ait besoin de la déclarer ici.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CountryInfo:
    name: str
    code_alpha2: str
    code_alpha3: str
    country_code: str
    cni_format: str
    passport_format: str
    phone_length: int
    password_format: str


@dataclass(frozen=True, slots=True)
class PersonData:
    first_names_male: list[str]
    first_names_female: list[str]
    last_names: list[str]
    occupations: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class Operator:
    name: str
    prefixes: list[str]


@dataclass(frozen=True, slots=True)
class TelecomData:
    operators: list[Operator]
    landline_prefixes: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class GpsBounds:
    """Boîte englobante approximative du territoire d'un pays."""

    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


@dataclass(frozen=True, slots=True)
class AddressData:
    """Adresses textuelles (quartier + repère + ville), pas d'adressage postal structuré."""

    cities: list[str]
    neighborhoods: list[str]
    landmarks: list[str]
    regions: list[str]
    gps_bounds: GpsBounds | None = None


@dataclass(frozen=True, slots=True)
class FinanceData:
    currency: str
    banks: list[str]
    mobile_money_operators: list[str]


@dataclass(frozen=True, slots=True)
class CompanyData:
    suffixes: list[str]


_KNOWN_SECTIONS = {"country", "person", "telecom", "address", "documents", "finance", "company"}


@dataclass(frozen=True, slots=True)
class CountryData:
    """Vue typée + accès brut à un YAML de pays validé."""

    country: CountryInfo
    person: PersonData
    telecom: TelecomData
    raw: dict[str, Any] = field(repr=False)
    address: AddressData | None = None
    documents: dict[str, str] | None = None
    finance: FinanceData | None = None
    company: CompanyData | None = None

    @property
    def extra(self) -> dict[str, Any]:
        """Sections du YAML au-delà de la structure minimale et des sections optionnelles connues."""
        return {key: value for key, value in self.raw.items() if key not in _KNOWN_SECTIONS}

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CountryData":
        country = CountryInfo(**raw["country"])
        person = PersonData(**raw["person"])
        operators = [
            Operator(name=name, prefixes=list(op_data["prefixes"]))
            for name, op_data in raw["telecom"]["operators"].items()
        ]
        telecom = TelecomData(
            operators=operators,
            landline_prefixes=list(raw["telecom"].get("landline_prefixes", [])),
        )

        address = None
        if "address" in raw:
            raw_address = raw["address"]
            gps_bounds = None
            if "gps_bounds" in raw_address:
                gps_bounds = GpsBounds(**raw_address["gps_bounds"])
            address = AddressData(
                cities=list(raw_address["cities"]),
                neighborhoods=list(raw_address["neighborhoods"]),
                landmarks=list(raw_address["landmarks"]),
                regions=list(raw_address["regions"]),
                gps_bounds=gps_bounds,
            )

        documents = None
        if "documents" in raw:
            documents = dict(raw["documents"])

        finance = None
        if "finance" in raw:
            finance = FinanceData(
                currency=raw["finance"]["currency"],
                banks=list(raw["finance"]["banks"]),
                mobile_money_operators=list(raw["finance"]["mobile_money_operators"]),
            )

        company = None
        if "company" in raw:
            company = CompanyData(suffixes=list(raw["company"]["suffixes"]))

        return cls(
            country=country,
            person=person,
            telecom=telecom,
            raw=raw,
            address=address,
            documents=documents,
            finance=finance,
            company=company,
        )
