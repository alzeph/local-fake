# local-fake
Un générateur open source de fausses données (Faker) localisées pour l'Afrique, conçu pour tester les applications avec les réalités du terrain (Mobile Money, formats d'adresses textuelles, numérotations locales, et KYC).

**Pays disponibles** : Côte d'Ivoire (`ci`), Burkina Faso (`bf`), Bénin (`bj`).
Les formats de documents (CNI, passeport, NIF, RCCM, ...) sont plausibles et
cohérents entre eux, mais n'ont pas fait l'objet d'une vérification officielle
auprès des administrations concernées — à valider avant un usage KYC réel.

## Installation

```bash
pip install local-fake              # cœur de la librairie (données uniquement)
pip install local-fake[files]       # + génération de fichiers PDF/Word/PNG/Excel
```

`local.file.svg()` fonctionne sans l'extra `[files]` (texte pur, aucune
dépendance tierce). Les 4 autres méthodes de `local.file.*`
(`excel`/`word`/`pdf`/`png`) nécessitent `openpyxl`/`python-docx`/`fpdf2`/`Pillow`
respectivement et lèvent `MissingOptionalDependencyError` avec un message
explicite si l'extra n'est pas installé — plutôt que de forcer ces
dépendances à tout le monde, y compris qui n'a besoin que de données.

## Reproductibilité

```python
import local_fake
from local_fake import LocalFake

local_fake.seed(42)          # ou : LocalFake(seed=42)
local = LocalFake()
```

`seed()` fixe le générateur interne partagé de local-fake (comme `Faker.seed()`) :
deux exécutions avec la même graine produisent la même séquence de données,
quel que soit le nombre d'instances `LocalFake()` créées. Il n'affecte **pas**
le module `random` global du process — seul le code de local-fake est concerné.

Ceci couvre toutes les données (`first_name()`, `phone_number()`, etc.) ainsi
que les fichiers générés par `local.file.*`, à une nuance près : `svg()`,
`pdf()` et `word()` sont reproductibles à l'octet près ; `excel()` garantit la
reproductibilité de la **donnée** (cellules, en-têtes — vérifiable en
réouvrant le fichier), mais pas l'identité binaire exacte du `.xlsx`, à cause
d'un ordre de sérialisation interne à `openpyxl` indépendant de toute graine
(probablement lié à un hachage par identité d'objets de style, sensible à ce
qui a été alloué plus tôt dans le même process).

## Usage

```python
from local_fake import LocalFake

local = LocalFake()

local.first_name()             # un prénom, peu importe le pays
local.ci.first_name()          # un prénom ivoirien
local.unique.ci.first_name()   # un prénom ivoirien, garanti unique
local.unique.first_name()      # un prénom générique, garanti unique

local.ci.phone_number()        # un numéro ivoirien conforme aux préfixes opérateurs
local.ci.cni_number()          # un numéro de CNI conforme au format du pays
local.ci.passport_number()     # un numéro de passeport conforme au format du pays
local.ci.password()            # un mot de passe conforme aux exigences du pays
local.ci.address()             # une adresse textuelle : "quartier, repère, ville"
```

Certaines méthodes lèvent `MissingCountryDataError` si le pays n'a pas la
section YAML correspondante : elle est optionnelle, contrairement à
`country`, `person` et `telecom`. C'est le cas pour toutes les méthodes
marquées *(optionnel)* ci-dessous.

### Catalogue complet

| Domaine | Méthode | Dépend de (YAML) |
|---|---|---|
| **Identité** | `first_name()`, `last_name()`, `full_name()` | `person` |
| | `birth_date(min_age=18, max_age=90)` | — (générique) |
| | `birth_place()` *(optionnel)* | `address.cities` |
| | `occupation()` *(optionnel)* | `person.occupations` |
| | `marital_status()` | — (générique) |
| **Documents / KYC** | `cni_number()`, `passport_number()`, `password()` | `country` |
| | `document_number(kind)` *(optionnel)* | `documents.<kind>` |
| | `nif_number()`, `cnps_number()`, `driver_license_number()`, `birth_certificate_number()` *(optionnel)* | `documents.{nif,cnps,driver_license,birth_certificate}` |
| | `kyc_tier()` | — (générique, `tier1`/`tier2`/`tier3`) |
| | `document_issue_date()`, `document_expiry_date(issue_date=None, validity_years=10)` | — (génériques) |
| **Adresse / géo** | `address()` *(optionnel)* | `address.{cities,neighborhoods,landmarks}` |
| | `region()` *(optionnel)* | `address.regions` |
| | `gps_coordinates()` *(optionnel)* | `address.gps_bounds` |
| | `area_type()` | — (générique, `urbain`/`rural`) |
| **Télécom** | `phone_number()`, `operator_name()` | `telecom` |
| | `landline_number()` *(optionnel)* | `telecom.landline_prefixes` |
| | `imei()` | — (générique, checksum Luhn) |
| | `email(first_name=None, last_name=None)` | — (générique) |
| **Finance / Mobile Money** | `mobile_money_account()` | `telecom` (= `phone_number()`) |
| | `mobile_money_operator()`, `bank_name()`, `currency()` *(optionnel)* | `finance` |
| | `bank_account_number()`, `amount()`, `transaction_id()` | — (génériques) |
| **Entreprise** | `company_name()` *(optionnel)* | `person` + `company.suffixes` |
| | `business_sector()` | — (générique) |
| | `rccm_number()`, `ifu_number()` *(optionnel)* | `documents.{rccm,ifu}` |

Toutes ces méthodes existent aussi sous `local.unique.*` et
`local.unique.<code>.*` (garanties uniques), et sur `local.*` directement
pour un pays tiré au hasard parmi ceux enregistrés (délégation).

## Génération de fichiers

`local.file` génère des fichiers de test (PDF, Word, PNG, SVG, Excel),
indépendamment de tout pays — combinable avec les générateurs ci-dessus.

```python
local.file.svg()                          # SVG minimal, taille par défaut
local.file.png(width=800, height=600)      # PNG de bruit aléatoire, dimensions imposées
local.file.pdf(min_size=50_000)            # PDF d'au moins 50 Ko (rempli de pages de texte)
local.file.word(max_size=100_000)          # Word d'au plus 100 Ko
local.file.excel()                          # classeur vide

local.file.excel(data=["Nom", "Prénom", "Téléphone"])  # une seule ligne d'en-tête

local.file.excel(data={                     # en-têtes = clés, lignes = valeurs
    "Nom": [local.ci.last_name() for _ in range(20)],
    "Téléphone": [local.ci.phone_number() for _ in range(20)],
})

local.file.pdf(path="rapport.pdf")           # écrit aussi sur disque en plus de retourner les bytes
```

- Chaque méthode retourne des `bytes` ; `path=` (optionnel) écrit en plus le
  résultat sur disque.
- `min_size`/`max_size` sont optionnels et définissent un **intervalle**
  (pas une taille exacte — pas réaliste pour des formats binaires
  structurés) ; sans eux, un intervalle standard par format est utilisé.
  Le fichier est amené dans l'intervalle en ajoutant du contenu de
  remplissage (pages, paragraphes, lignes, ou dimensions pour le PNG),
  jamais en tronquant des octets qui casseraient la structure du fichier.
- Si l'intervalle demandé est irréalisable (ex: `max_size` plus petit que
  le poids incompressible du format, ~36 Ko pour un `.docx` vide côté
  python-docx), `InvalidFileSizeError` est levée avec une explication.
- Pour `excel(data=...)` : une `list[str]` devient la ligne d'en-tête (sans
  données) ; un `dict[str, list]` a ses clés comme en-têtes de colonnes et
  ses valeurs comme lignes — les colonnes plus courtes sont complétées par
  des cellules vides.

## Ajouter un pays

**Cas courant — aucune règle spécifique au pays :**

Créer `src/local_fake/data/countries/<code>.yaml` en respectant la structure
minimale (`country`, `person`, `telecom.operators`) — voir `ci.yaml` comme
référence. Des sections additionnelles (`address`, ...) peuvent être ajoutées
librement. C'est tout : `SupraProvider` découvre automatiquement le fichier
au démarrage et expose `local.xx.*` / `local.unique.xx.*` avec un provider
générique (`xx` = le nom du fichier sans l'extension, qui devient aussi le
`country_code` par défaut).

**Cas avancé — une réalité locale demande de surcharger une méthode :**

Créer en plus `src/local_fake/providers/countries/<code>.py` :

```python
from local_fake.providers.base import BaseProvider

class ProviderXX(BaseProvider):
    yaml_file = "xx.yaml"
    country_code = "XX"
    # surcharger ici une méthode si les réalités du pays le demandent
```

`SupraProvider` détecte ce fichier et utilise cette classe à la place du
provider générique — toujours sans rien déclarer ailleurs.

**Sections YAML optionnelles reconnues** (activent des méthodes supplémentaires,
voir le catalogue ci-dessus) : `person.occupations`, `address` (+ sous-champs
`regions`, `gps_bounds`), `telecom.landline_prefixes`, `documents` (mapping
libre `nom: regex`, ex. `nif`, `cnps`, `driver_license`, `birth_certificate`,
`rccm`, `ifu`), `finance` (`currency`, `banks`, `mobile_money_operators`),
`company` (`suffixes`). Voir `ci.yaml` pour un exemple complet. Toute autre
section reste libre et accessible via `CountryData.extra`.

## Structure du projet

```
src/local_fake/
    local_fake.py          # classe LocalFake (point d'entrée)
    cache.py                # UniqueCache : mémorisation des valeurs déjà servies
    proxy.py                # UniqueProxy : implémente .unique
    exceptions.py
    data/countries/          # un YAML par pays
    engine/
        loader.py             # chargement + validation + cache des YAML
        models.py              # CountryData et modèles associés
    validators/
        schema.py              # structure minimale exigée d'un YAML de pays
        pattern.py              # validation d'une valeur contre une regex
    generators/
        person.py, telecom.py, identity.py, security.py, pattern.py,
        address.py, contact.py, dates.py, finance.py, company.py
    providers/
        base.py                 # BaseProvider : générateurs génériques + délégation
        supra.py                 # SupraProvider : registre de tous les pays
        countries/<code>.py      # un provider par pays, hérite de BaseProvider
    files/
        provider.py              # FileProvider, exposé comme local.file
        sizing.py                # respect de [min_size, max_size] par remplissage
        svg.py, image.py, pdf.py, word.py, excel.py
    utils/
        random_utils.py          # pick, digits, shuffled
```
