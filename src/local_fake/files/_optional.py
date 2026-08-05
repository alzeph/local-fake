"""Import paresseux des dépendances de l'extra optionnel `files`.

`openpyxl`, `python-docx`, `fpdf2` et `Pillow` ne sont PAS des dépendances du
paquet de base — seul `local.file.svg()` (texte pur, sans dépendance tierce)
fonctionne sans rien installer de plus. Chaque autre méthode de `FileProvider`
importe son paquet à l'appel, pas au chargement du module, pour qu'un
utilisateur qui n'a besoin que de `first_name()`/`address()`/... n'ait jamais
à installer Pillow, python-docx, etc.
"""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

from local_fake.exceptions import MissingOptionalDependencyError


def optional_import(module_name: str, *, feature: str) -> ModuleType:
    try:
        return import_module(module_name)
    except ImportError as exc:
        raise MissingOptionalDependencyError(
            f"local.file.{feature}() nécessite les dépendances optionnelles de l'extra "
            f"« files » (paquet manquant : « {module_name} »). Installez-les avec : "
            "pip install 'local-fake[files]' (ou : uv add local-fake --extra files)."
        ) from exc
