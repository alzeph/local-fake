from importlib.metadata import PackageNotFoundError, version

from local_fake.local_fake import LocalFake
from local_fake.rng import seed

try:
    __version__ = version("local-fake")
except PackageNotFoundError:  # paquet non installé (ex: exécution depuis les sources)
    __version__ = "0.0.0+unknown"

__all__ = ["LocalFake", "seed", "__version__"]
