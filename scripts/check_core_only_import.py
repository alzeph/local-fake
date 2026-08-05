"""Vérifie que le paquet de base fonctionne sans les dépendances optionnelles de l'extra `files`.

Utilisé par le job CI `core-only-import` (`.github/workflows/ci.yml`). Un vrai
fichier Python plutôt qu'un one-liner shell : `python -c "..."` multi-lignes
se comporte différemment selon le shell qui invoque la commande (bash sur
Linux/macOS, PowerShell par défaut sur les runners Windows), ce qui rend le
quoting fragile d'une plateforme à l'autre. Un script exécuté via
`python scripts/check_core_only_import.py` n'a pas ce problème.
"""

from __future__ import annotations

from local_fake import LocalFake
from local_fake.exceptions import MissingOptionalDependencyError

local = LocalFake()

assert local.ci.first_name()
assert local.file.svg().startswith(b"<svg")

try:
    local.file.excel()
except MissingOptionalDependencyError:
    pass
else:
    raise SystemExit("excel() aurait dû lever MissingOptionalDependencyError sans l'extra files")

print("OK: le paquet de base fonctionne sans les dépendances optionnelles")
