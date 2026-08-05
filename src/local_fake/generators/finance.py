"""Génération de données financières (Mobile Money, banque, transactions)."""

from __future__ import annotations

import string

from local_fake.engine.models import FinanceData
from local_fake.rng import get_rng
from local_fake.utils.random_utils import digits, pick

_TRANSACTION_ID_LENGTH = 12
_BANK_ACCOUNT_NUMBER_LENGTH = 23  # format RIB UEMOA : banque(5) + guichet(5) + compte(11) + clé(2)


def generate_bank_name(finance: FinanceData) -> str:
    return pick(finance.banks)


def generate_mobile_money_operator(finance: FinanceData) -> str:
    return pick(finance.mobile_money_operators)


def generate_bank_account_number() -> str:
    """Génère un numéro de compte façon RIB UEMOA (23 chiffres), sans donnée de pays.

    Pas de validation de la clé RIB (l'algorithme diffère par pays) : l'objectif
    est un identifiant plausible pour des tests, pas un RIB réellement valide.
    """
    return digits(_BANK_ACCOUNT_NUMBER_LENGTH)


def generate_amount(min_amount: int, max_amount: int) -> int:
    return get_rng().randint(min_amount, max_amount)


def generate_transaction_id() -> str:
    pool = string.ascii_uppercase + string.digits
    rng = get_rng()
    suffix = "".join(rng.choice(pool) for _ in range(_TRANSACTION_ID_LENGTH))
    return f"TXN{suffix}"
