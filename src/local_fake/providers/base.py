"""Provider de base : socle commun à tous les providers pays et à `LocalFake`."""

from __future__ import annotations

import datetime
from typing import ClassVar, Protocol

from local_fake.engine.loader import load_country_data
from local_fake.engine.models import CountryData
from local_fake.exceptions import MissingCountryDataError
from local_fake.generators.address import (
    generate_address,
    generate_area_type,
    generate_gps_coordinates,
    generate_region,
)
from local_fake.generators.company import generate_business_sector, generate_company_name
from local_fake.generators.contact import generate_email
from local_fake.generators.dates import generate_birth_date, generate_expiry_date, generate_issue_date
from local_fake.generators.finance import (
    generate_amount,
    generate_bank_account_number,
    generate_bank_name,
    generate_mobile_money_operator,
    generate_transaction_id,
)
from local_fake.generators.identity import (
    generate_cni_number,
    generate_document_number,
    generate_kyc_tier,
    generate_passport_number,
)
from local_fake.generators.person import (
    Gender,
    generate_birth_place,
    generate_first_name,
    generate_full_name,
    generate_last_name,
    generate_marital_status,
    generate_occupation,
)
from local_fake.generators.security import generate_password
from local_fake.generators.telecom import generate_imei, generate_landline_number, generate_phone_number, pick_operator


class ProviderRegistry(Protocol):
    def random_provider(self) -> "BaseProvider": ...


class BaseProvider:
    """Générateurs génériques, indépendants de tout pays.

    Un provider pays (ex: `ProviderCI`) hérite de cette classe et déclare
    uniquement `yaml_file` (le nom du fichier dans `data/countries/`) : les
    méthodes ci-dessous chargent alors ses données et génèrent des valeurs
    conformes. Il peut surcharger individuellement n'importe laquelle de ces
    méthodes si les réalités du pays le demandent.

    Quand cette classe est instanciée SANS `yaml_file` — c'est le cas de
    `LocalFake` lui-même — `self.data` reste `None` et chaque méthode
    délègue à un provider pays tiré au hasard dans le registre fourni
    (`local.first_name()` == "un nom, peu importe le pays"). Les méthodes
    qui ne dépendent d'aucune donnée de pays (dates, IMEI, montant, ...)
    n'ont pas besoin de déléguer : elles produisent le même résultat quel
    que soit le provider.
    """

    yaml_file: ClassVar[str | None] = None
    country_code: ClassVar[str | None] = None

    def __init__(self, registry: ProviderRegistry | None = None) -> None:
        self._registry = registry
        self.data: CountryData | None = load_country_data(self.yaml_file) if self.yaml_file else None

    def _delegate(self, method_name: str, /, **kwargs):
        if self._registry is None:
            raise RuntimeError(
                f"{type(self).__name__} n'a pas de données de pays et aucun registre "
                "n'est configuré pour déléguer cet appel."
            )
        provider = self._registry.random_provider()
        return getattr(provider, method_name)(**kwargs)

    def _require(self, section: object, name: str) -> None:
        if section is None:
            raise MissingCountryDataError(
                f"{type(self).__name__} n'a pas de section « {name} » dans son YAML."
            )

    # -- Identité -----------------------------------------------------------

    def first_name(self, gender: Gender | None = None) -> str:
        if self.data is None:
            return self._delegate("first_name", gender=gender)
        return generate_first_name(self.data.person, gender)

    def last_name(self) -> str:
        if self.data is None:
            return self._delegate("last_name")
        return generate_last_name(self.data.person)

    def full_name(self, gender: Gender | None = None) -> str:
        if self.data is None:
            return self._delegate("full_name", gender=gender)
        return generate_full_name(self.data.person, gender)

    def birth_date(self, *, min_age: int = 18, max_age: int = 90) -> datetime.date:
        return generate_birth_date(min_age=min_age, max_age=max_age)

    def birth_place(self) -> str:
        if self.data is None:
            return self._delegate("birth_place")
        self._require(self.data.address, "address")
        return generate_birth_place(self.data.address)

    def occupation(self) -> str:
        if self.data is None:
            return self._delegate("occupation")
        if not self.data.person.occupations:
            raise MissingCountryDataError(
                f"{type(self).__name__} n'a pas de liste « person.occupations » dans son YAML."
            )
        return generate_occupation(self.data.person)

    def marital_status(self) -> str:
        return generate_marital_status()

    def cni_number(self) -> str:
        if self.data is None:
            return self._delegate("cni_number")
        return generate_cni_number(self.data.country)

    def passport_number(self) -> str:
        if self.data is None:
            return self._delegate("passport_number")
        return generate_passport_number(self.data.country)

    def password(self, length: int | None = None) -> str:
        if self.data is None:
            return self._delegate("password", length=length)
        kwargs = {} if length is None else {"length": length}
        return generate_password(self.data.country.password_format, **kwargs)

    # -- Documents (KYC) ------------------------------------------------------

    def document_number(self, kind: str) -> str:
        """Génère un numéro conforme au format `kind` déclaré dans `documents` (YAML)."""
        if self.data is None:
            return self._delegate("document_number", kind=kind)
        if not self.data.documents or kind not in self.data.documents:
            raise MissingCountryDataError(
                f"{type(self).__name__} n'a pas de format de document « {kind} » "
                "dans la section « documents » de son YAML."
            )
        return generate_document_number(self.data.documents[kind])

    def nif_number(self) -> str:
        return self.document_number("nif")

    def cnps_number(self) -> str:
        return self.document_number("cnps")

    def driver_license_number(self) -> str:
        return self.document_number("driver_license")

    def birth_certificate_number(self) -> str:
        return self.document_number("birth_certificate")

    def kyc_tier(self) -> str:
        return generate_kyc_tier()

    def document_issue_date(self, *, years_ago_max: int = 10) -> datetime.date:
        return generate_issue_date(years_ago_max=years_ago_max)

    def document_expiry_date(
        self, issue_date: datetime.date | None = None, *, validity_years: int = 10
    ) -> datetime.date:
        """Expiration à `validity_years` après `issue_date` (généré si omis)."""
        if issue_date is None:
            issue_date = self.document_issue_date()
        return generate_expiry_date(issue_date, validity_years=validity_years)

    # -- Adresse / géographie -------------------------------------------------

    def address(self) -> str:
        if self.data is None:
            return self._delegate("address")
        self._require(self.data.address, "address")
        return generate_address(self.data.address)

    def region(self) -> str:
        if self.data is None:
            return self._delegate("region")
        self._require(self.data.address, "address")
        return generate_region(self.data.address)

    def gps_coordinates(self) -> tuple[float, float]:
        if self.data is None:
            return self._delegate("gps_coordinates")
        self._require(self.data.address, "address")
        if self.data.address.gps_bounds is None:
            raise MissingCountryDataError(
                f"{type(self).__name__} n'a pas de « address.gps_bounds » dans son YAML."
            )
        return generate_gps_coordinates(self.data.address)

    def area_type(self) -> str:
        return generate_area_type()

    # -- Télécom --------------------------------------------------------------

    def phone_number(self, operator: str | None = None, *, international: bool = False) -> str:
        if self.data is None:
            return self._delegate("phone_number", operator=operator, international=international)
        return generate_phone_number(
            self.data.telecom,
            self.data.country.phone_length,
            operator=operator,
            international=international,
            country_code=self.data.country.country_code,
        )

    def operator_name(self) -> str:
        if self.data is None:
            return self._delegate("operator_name")
        return pick_operator(self.data.telecom).name

    def landline_number(self) -> str:
        if self.data is None:
            return self._delegate("landline_number")
        if not self.data.telecom.landline_prefixes:
            raise MissingCountryDataError(
                f"{type(self).__name__} n'a pas de « telecom.landline_prefixes » dans son YAML."
            )
        return generate_landline_number(self.data.telecom, self.data.country.phone_length)

    def imei(self) -> str:
        return generate_imei()

    def email(self, first_name: str | None = None, last_name: str | None = None) -> str:
        first = first_name or self.first_name()
        last = last_name or self.last_name()
        return generate_email(first, last)

    # -- Finance / Mobile Money -------------------------------------------------

    def mobile_money_account(self) -> str:
        """Le compte Mobile Money est, en pratique, le numéro de téléphone lui-même."""
        return self.phone_number()

    def mobile_money_operator(self) -> str:
        if self.data is None:
            return self._delegate("mobile_money_operator")
        self._require(self.data.finance, "finance")
        return generate_mobile_money_operator(self.data.finance)

    def bank_name(self) -> str:
        if self.data is None:
            return self._delegate("bank_name")
        self._require(self.data.finance, "finance")
        return generate_bank_name(self.data.finance)

    def currency(self) -> str:
        if self.data is None:
            return self._delegate("currency")
        self._require(self.data.finance, "finance")
        return self.data.finance.currency

    def bank_account_number(self) -> str:
        return generate_bank_account_number()

    def amount(self, min_amount: int = 1_000, max_amount: int = 500_000) -> int:
        return generate_amount(min_amount, max_amount)

    def transaction_id(self) -> str:
        return generate_transaction_id()

    # -- Entreprise ---------------------------------------------------------

    def company_name(self) -> str:
        if self.data is None:
            return self._delegate("company_name")
        self._require(self.data.company, "company")
        return generate_company_name(self.data.person, self.data.company)

    def business_sector(self) -> str:
        return generate_business_sector()

    def rccm_number(self) -> str:
        return self.document_number("rccm")

    def ifu_number(self) -> str:
        return self.document_number("ifu")
