import dataclasses
import datetime
import re
import sys
import textwrap
import types

import pytest

from local_fake import LocalFake
from local_fake.engine.loader import load_country_data
from local_fake.exceptions import (
    InvalidProviderModuleError,
    MissingCountryDataError,
    SchemaValidationError,
    UniquenessExhaustedError,
)
from local_fake.generators.pattern import generate_from_pattern
from local_fake.providers.base import BaseProvider
from local_fake.providers.supra import SupraProvider
from local_fake.validators.schema import validate_country_schema


@pytest.fixture
def local() -> LocalFake:
    return LocalFake()


def test_ci_first_name_is_from_known_pool(local: LocalFake) -> None:
    person = local.ci.data.person
    pool = set(person.first_names_male) | set(person.first_names_female)
    assert local.ci.first_name() in pool


def test_ci_last_name_is_from_known_pool(local: LocalFake) -> None:
    assert local.ci.last_name() in set(local.ci.data.person.last_names)


def test_generic_first_name_delegates_to_a_registered_country(local: LocalFake) -> None:
    # Délégation vers un pays enregistré au hasard (ci/bf/bj) : on vérifie
    # juste qu'une valeur plausible revient, pas un pays précis.
    name = local.first_name()
    assert isinstance(name, str) and name


def test_ci_phone_number_matches_expected_length_and_prefix(local: LocalFake) -> None:
    number = local.ci.phone_number()
    assert len(number) == 10
    assert number[:2] in {"07", "08", "09", "05", "04", "06", "01", "02", "03"}


def test_ci_phone_number_international_includes_country_code(local: LocalFake) -> None:
    number = local.ci.phone_number(international=True)
    assert number.startswith("+225")
    assert len(number) == len("+225") + 10


def test_ci_cni_number_matches_country_format(local: LocalFake) -> None:
    cni_format = local.ci.data.country.cni_format
    assert re.fullmatch(cni_format, local.ci.cni_number())


def test_ci_password_matches_country_format(local: LocalFake) -> None:
    password_format = local.ci.data.country.password_format
    assert re.fullmatch(password_format, local.ci.password())


def test_ci_passport_number_matches_country_format(local: LocalFake) -> None:
    passport_format = local.ci.data.country.passport_format
    assert re.fullmatch(passport_format, local.ci.passport_number())


def test_ci_address_uses_known_pools(local: LocalFake) -> None:
    cities = {"Abidjan", "Bouaké", "San-Pédro", "Yamoussoukro", "Korhogo"}
    neighborhoods = {"Angré", "Niangon", "Zone 4", "Riviera 3", "Siporex"}
    landmarks = {
        "en face de la pharmacie",
        "près du terminus de bus",
        "non loin de la station-service",
        "derrière le marché",
    }
    neighborhood, landmark, city = local.ci.address().split(", ")
    assert neighborhood in neighborhoods
    assert landmark in landmarks
    assert city in cities


def test_address_raises_when_country_has_no_address_section(local: LocalFake) -> None:
    original = local.ci.data
    local.ci.data = dataclasses.replace(original, address=None)
    try:
        with pytest.raises(MissingCountryDataError):
            local.ci.address()
    finally:
        local.ci.data = original


def test_unique_ci_address_never_repeats_until_pool_exhausted(local: LocalFake) -> None:
    # 5 quartiers x 4 repères x 5 villes = 100 combinaisons possibles.
    seen = {local.unique.ci.address() for _ in range(20)}
    assert len(seen) == 20


def test_ci_birth_date_respects_age_bounds(local: LocalFake) -> None:
    today = datetime.date.today()
    birth_date = local.ci.birth_date(min_age=20, max_age=30)
    age = today.year - birth_date.year
    assert 20 <= age <= 30


def test_ci_birth_place_is_from_known_cities(local: LocalFake) -> None:
    assert local.ci.birth_place() in local.ci.data.address.cities


def test_ci_occupation_is_from_known_pool(local: LocalFake) -> None:
    assert local.ci.occupation() in local.ci.data.person.occupations


def test_occupation_raises_when_country_has_no_occupations(local: LocalFake) -> None:
    original = local.ci.data
    local.ci.data = dataclasses.replace(original, person=dataclasses.replace(original.person, occupations=[]))
    try:
        with pytest.raises(MissingCountryDataError):
            local.ci.occupation()
    finally:
        local.ci.data = original


def test_marital_status_is_a_known_value(local: LocalFake) -> None:
    assert local.ci.marital_status() in {"célibataire", "marié(e)", "divorcé(e)", "veuf(ve)"}


@pytest.mark.parametrize(
    ("method_name", "document_kind"),
    [
        ("nif_number", "nif"),
        ("cnps_number", "cnps"),
        ("driver_license_number", "driver_license"),
        ("birth_certificate_number", "birth_certificate"),
        ("rccm_number", "rccm"),
        ("ifu_number", "ifu"),
    ],
)
def test_ci_document_numbers_match_their_format(local: LocalFake, method_name: str, document_kind: str) -> None:
    pattern = local.ci.data.documents[document_kind]
    value = getattr(local.ci, method_name)()
    assert re.fullmatch(pattern, value)


def test_document_number_raises_for_unknown_kind(local: LocalFake) -> None:
    with pytest.raises(MissingCountryDataError):
        local.ci.document_number("passeport_diplomatique")


def test_kyc_tier_is_a_known_tier(local: LocalFake) -> None:
    assert local.ci.kyc_tier() in {"tier1", "tier2", "tier3"}


def test_document_expiry_date_is_after_issue_date(local: LocalFake) -> None:
    issue_date = local.ci.document_issue_date()
    expiry_date = local.ci.document_expiry_date(issue_date, validity_years=5)
    assert expiry_date.year - issue_date.year == 5


def test_ci_region_is_from_known_pool(local: LocalFake) -> None:
    assert local.ci.region() in local.ci.data.address.regions


def test_ci_gps_coordinates_are_within_bounds(local: LocalFake) -> None:
    bounds = local.ci.data.address.gps_bounds
    latitude, longitude = local.ci.gps_coordinates()
    assert bounds.min_lat <= latitude <= bounds.max_lat
    assert bounds.min_lon <= longitude <= bounds.max_lon


def test_gps_coordinates_raises_when_country_has_no_bounds(local: LocalFake) -> None:
    original = local.ci.data
    stripped_address = dataclasses.replace(original.address, gps_bounds=None)
    local.ci.data = dataclasses.replace(original, address=stripped_address)
    try:
        with pytest.raises(MissingCountryDataError):
            local.ci.gps_coordinates()
    finally:
        local.ci.data = original


def test_area_type_is_urban_or_rural(local: LocalFake) -> None:
    assert local.ci.area_type() in {"urbain", "rural"}


def test_ci_landline_number_matches_length_and_prefix(local: LocalFake) -> None:
    number = local.ci.landline_number()
    assert len(number) == local.ci.data.country.phone_length
    assert number[:2] in set(local.ci.data.telecom.landline_prefixes)


def test_landline_number_raises_when_country_has_no_landline_prefixes(local: LocalFake) -> None:
    original = local.ci.data
    stripped_telecom = dataclasses.replace(original.telecom, landline_prefixes=[])
    local.ci.data = dataclasses.replace(original, telecom=stripped_telecom)
    try:
        with pytest.raises(MissingCountryDataError):
            local.ci.landline_number()
    finally:
        local.ci.data = original


def test_imei_has_15_digits_and_passes_luhn_checksum(local: LocalFake) -> None:
    imei = local.ci.imei()
    assert len(imei) == 15 and imei.isdigit()
    total = 0
    for index, char in enumerate(reversed(imei)):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    assert total % 10 == 0


def test_email_uses_provided_names_and_a_known_domain(local: LocalFake) -> None:
    address = local.ci.email(first_name="Awa", last_name="Koné")
    local_part, _, domain = address.partition("@")
    assert "awa" in local_part.lower()
    assert "kone" in local_part.lower()
    assert domain in {"gmail.com", "yahoo.fr", "outlook.com", "hotmail.com"}


def test_mobile_money_account_is_a_phone_number(local: LocalFake) -> None:
    account = local.ci.mobile_money_account()
    assert len(account) == local.ci.data.country.phone_length


def test_ci_mobile_money_operator_is_from_known_pool(local: LocalFake) -> None:
    assert local.ci.mobile_money_operator() in local.ci.data.finance.mobile_money_operators


def test_ci_bank_name_is_from_known_pool(local: LocalFake) -> None:
    assert local.ci.bank_name() in local.ci.data.finance.banks


def test_ci_currency_matches_country_data(local: LocalFake) -> None:
    assert local.ci.currency() == local.ci.data.finance.currency


def test_bank_account_number_has_23_digits(local: LocalFake) -> None:
    account_number = local.ci.bank_account_number()
    assert len(account_number) == 23 and account_number.isdigit()


def test_amount_respects_bounds(local: LocalFake) -> None:
    amount = local.ci.amount(min_amount=100, max_amount=200)
    assert 100 <= amount <= 200


def test_transaction_id_has_expected_prefix(local: LocalFake) -> None:
    assert local.ci.transaction_id().startswith("TXN")


def test_ci_company_name_uses_known_last_name_and_suffix(local: LocalFake) -> None:
    name = local.ci.company_name()
    assert any(last_name in name for last_name in local.ci.data.person.last_names)
    assert any(suffix in name for suffix in [*local.ci.data.company.suffixes, "& Fils"])


def test_business_sector_is_a_non_empty_string(local: LocalFake) -> None:
    assert isinstance(local.ci.business_sector(), str) and local.ci.business_sector()


def test_finance_methods_raise_when_country_has_no_finance_section(local: LocalFake) -> None:
    original = local.ci.data
    local.ci.data = dataclasses.replace(original, finance=None)
    try:
        with pytest.raises(MissingCountryDataError):
            local.ci.bank_name()
    finally:
        local.ci.data = original


def test_company_name_raises_when_country_has_no_company_section(local: LocalFake) -> None:
    original = local.ci.data
    local.ci.data = dataclasses.replace(original, company=None)
    try:
        with pytest.raises(MissingCountryDataError):
            local.ci.company_name()
    finally:
        local.ci.data = original


def test_generic_methods_without_country_data_still_work(local: LocalFake) -> None:
    # Génériques (aucune dépendance à un pays) : doivent fonctionner directement
    # sur `local`, sans délégation, y compris avant tout ajout de pays.
    assert isinstance(local.birth_date(), datetime.date)
    assert local.marital_status() in {"célibataire", "marié(e)", "divorcé(e)", "veuf(ve)"}
    assert len(local.imei()) == 15
    assert local.transaction_id().startswith("TXN")


def test_generic_delegating_methods_work_through_root_instance(local: LocalFake) -> None:
    # Délégation vers un pays enregistré au hasard : doit fonctionner malgré
    # l'absence de données de pays sur `local` lui-même.
    assert isinstance(local.mobile_money_account(), str)
    assert isinstance(local.company_name(), str)
    assert isinstance(local.region(), str)


def test_unique_ci_first_name_never_repeats_until_pool_exhausted(local: LocalFake) -> None:
    person = local.ci.data.person
    pool_size = len(person.first_names_male) + len(person.first_names_female)
    seen = {local.unique.ci.first_name() for _ in range(pool_size)}
    assert len(seen) == pool_size
    with pytest.raises(UniquenessExhaustedError):
        local.unique.ci.first_name()


def test_unique_namespaces_are_independent_per_country_and_method(local: LocalFake) -> None:
    generic_value = local.unique.first_name()
    ci_value = local.unique.ci.first_name()
    # Deux espaces de noms distincts : aucune exception, même si les valeurs coïncident.
    assert isinstance(generic_value, str)
    assert isinstance(ci_value, str)


def test_validate_country_schema_rejects_missing_fields() -> None:
    with pytest.raises(SchemaValidationError):
        validate_country_schema({"country": {}, "person": {}, "telecom": {}}, source="broken.yaml")


def test_validate_country_schema_accepts_extra_sections() -> None:
    raw = {
        "country": {
            "name": "Test",
            "code_alpha2": "TS",
            "code_alpha3": "TST",
            "country_code": "+000",
            "cni_format": "^[0-9]{5}$",
            "passport_format": "^[0-9]{5}$",
            "phone_length": 5,
            "password_format": "^.{8,}$",
        },
        "person": {
            "first_names_male": ["A"],
            "first_names_female": ["B"],
            "last_names": ["C"],
        },
        "telecom": {"operators": {"op": {"prefixes": ["1"]}}},
        "loyalty_program": {"tiers": ["bronze", "silver"]},  # section additionnelle libre
    }
    validate_country_schema(raw, source="ok.yaml")  # ne doit pas lever


def test_supra_provider_auto_discovers_yaml_without_a_python_provider(tmp_path, monkeypatch) -> None:
    (tmp_path / "zz.yaml").write_text(
        textwrap.dedent(
            """
            country:
              name: "Zed Land"
              code_alpha2: "ZZ"
              code_alpha3: "ZZZ"
              country_code: "+999"
              cni_format: "^[0-9]{5}$"
              passport_format: "^[0-9]{5}$"
              phone_length: 5
              password_format: "^.{8,}$"
            person:
              first_names_male: ["Zed"]
              first_names_female: ["Zoe"]
              last_names: ["Zorro"]
            telecom:
              operators:
                zeltel:
                  prefixes: ["9"]
            """
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("local_fake.providers.supra.COUNTRIES_DIR", tmp_path)
    monkeypatch.setattr("local_fake.engine.loader.COUNTRIES_DIR", tmp_path)
    load_country_data.cache_clear()

    try:
        supra = SupraProvider()
        assert hasattr(supra, "zz")
        assert supra.zz.country_code == "ZZ"
        assert supra.zz.first_name() in {"Zed", "Zoe"}
    finally:
        load_country_data.cache_clear()


def test_resolve_provider_class_raises_when_python_module_has_no_provider(monkeypatch) -> None:
    module_name = "local_fake.providers.countries.zz"
    monkeypatch.setitem(sys.modules, module_name, types.ModuleType(module_name))

    with pytest.raises(InvalidProviderModuleError):
        SupraProvider._resolve_provider_class("zz")


def test_resolve_provider_class_raises_when_python_module_has_multiple_providers(monkeypatch) -> None:
    module_name = "local_fake.providers.countries.zz"
    fake_module = types.ModuleType(module_name)

    class ProviderZZA(BaseProvider):
        yaml_file = "zz.yaml"
        country_code = "ZZ"

    class ProviderZZB(BaseProvider):
        yaml_file = "zz.yaml"
        country_code = "ZZ"

    ProviderZZA.__module__ = module_name
    ProviderZZB.__module__ = module_name
    fake_module.ProviderZZA = ProviderZZA
    fake_module.ProviderZZB = ProviderZZB
    monkeypatch.setitem(sys.modules, module_name, fake_module)

    with pytest.raises(InvalidProviderModuleError):
        SupraProvider._resolve_provider_class("zz")


def test_all_providers_never_includes_the_localfake_instance_itself(local: LocalFake) -> None:
    # Régression : `LocalFake` hérite à la fois de `SupraProvider` et de
    # `BaseProvider`, et stocke `self._registry = self`. Un scan naïf de
    # `vars(self)` dans `all_providers()` incluait alors `self` lui-même
    # (`country_code=None`) parmi les pays disponibles pour la délégation
    # générique, avec un risque de récursion infinie.
    providers = local.all_providers()
    assert local not in providers
    assert all(provider.country_code is not None for provider in providers)


def test_random_provider_never_returns_the_localfake_instance_itself(local: LocalFake) -> None:
    for _ in range(200):
        assert local._registry.random_provider() is not local


@pytest.mark.parametrize("code", ["ci", "bf", "bj"])
def test_each_registered_country_is_fully_usable(local: LocalFake, code: str) -> None:
    provider = getattr(local, code)
    assert provider.country_code == code.upper()
    assert provider.first_name()
    assert provider.phone_number()
    assert re.fullmatch(provider.data.country.cni_format, provider.cni_number())
    assert re.fullmatch(provider.data.country.passport_format, provider.passport_number())
    for document_kind, pattern in provider.data.documents.items():
        assert re.fullmatch(pattern, provider.document_number(document_kind))


@pytest.mark.parametrize(
    "pattern",
    ["^C[0-9]{8}$", "[A-Z]{2}[0-9]{4}", "(foo|bar)baz", "a[bc]?d{2,3}"],
)
def test_generate_from_pattern_matches_itself(pattern: str) -> None:
    for _ in range(20):
        assert re.fullmatch(pattern, generate_from_pattern(pattern))
