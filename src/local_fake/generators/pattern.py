r"""Génération d'une chaîne conforme à un sous-ensemble de regex.

Sert à produire des valeurs (CNI, plaques, codes postaux, ...) directement à
partir du champ `*_format` d'un YAML de pays, sans que chaque provider ait à
écrire un générateur dédié pour un simple motif du type `^C[0-9]{8}$`.

Sous-ensemble supporté : littéraux, `.`, classes `[...]` (avec `^` de
négation et plages `a-z`), groupes `(...)`, alternance `|`, échappements
`\d \w \s`, quantificateurs `? * + {n} {n,} {n,m}`, ancres `^ $` (ignorées).
Les assertions `(?=...)`, `(?!...)`, `(?<=...)`, `(?<!...)` ne sont pas
supportées : un format qui les utilise (ex. mot de passe) doit avoir son
propre générateur au lieu de `generate_from_pattern` — voir
`local_fake.generators.security`.
"""

from __future__ import annotations

import string

from local_fake.exceptions import PatternGenerationError
from local_fake.rng import get_rng

_MAX_UNBOUNDED_REPEAT = 6
_DOT_POOL = string.ascii_letters + string.digits
_ESCAPE_POOLS: dict[str, str] = {
    "d": string.digits,
    "w": string.ascii_letters + string.digits + "_",
    "s": " ",
}


class _PatternParser:
    def __init__(self, pattern: str) -> None:
        self._pattern = pattern
        self._pos = 0

    def generate(self) -> str:
        result = self._parse_alternation()
        if self._pos != len(self._pattern):
            raise PatternGenerationError(
                f"Caractère inattendu « {self._pattern[self._pos]} » dans le motif « {self._pattern} »"
            )
        return result

    def _peek(self) -> str | None:
        return self._pattern[self._pos] if self._pos < len(self._pattern) else None

    def _advance(self) -> str:
        char = self._pattern[self._pos]
        self._pos += 1
        return char

    def _parse_alternation(self) -> str:
        branches = [self._parse_concat()]
        while self._peek() == "|":
            self._advance()
            branches.append(self._parse_concat())
        return get_rng().choice(branches)

    def _parse_concat(self) -> str:
        parts: list[str] = []
        while self._peek() is not None and self._peek() not in ")|":
            parts.append(self._parse_quantified())
        return "".join(parts)

    def _parse_quantified(self) -> str:
        atom_fn = self._parse_atom()
        minimum, maximum = self._parse_quantifier()
        count = get_rng().randint(minimum, maximum)
        return "".join(atom_fn() for _ in range(count))

    def _parse_quantifier(self) -> tuple[int, int]:
        char = self._peek()
        if char == "?":
            self._advance()
            return 0, 1
        if char == "*":
            self._advance()
            return 0, _MAX_UNBOUNDED_REPEAT
        if char == "+":
            self._advance()
            return 1, _MAX_UNBOUNDED_REPEAT
        if char == "{":
            return self._parse_braces()
        return 1, 1

    def _parse_braces(self) -> tuple[int, int]:
        start = self._pos
        self._advance()  # consume '{'
        body_start = self._pos
        while self._peek() is not None and self._peek() != "}":
            self._advance()
        if self._peek() != "}":
            raise PatternGenerationError(f"Accolade non fermée dans le motif « {self._pattern} »")
        body = self._pattern[body_start:self._pos]
        self._advance()  # consume '}'

        if "," in body:
            low_str, _, high_str = body.partition(",")
            low = int(low_str) if low_str else 0
            high = int(high_str) if high_str else low + _MAX_UNBOUNDED_REPEAT
        else:
            if not body.isdigit():
                raise PatternGenerationError(f"Quantificateur invalide « {{{body}}} » à la position {start}")
            low = high = int(body)
        return low, high

    def _parse_atom(self):  # -> Callable[[], str]
        char = self._peek()
        if char is None:
            raise PatternGenerationError(f"Motif incomplet : « {self._pattern} »")

        if char in "^$":
            self._advance()
            return lambda: ""

        if char == ".":
            self._advance()
            return lambda: get_rng().choice(_DOT_POOL)

        if char == "(":
            return self._parse_group()

        if char == "[":
            return self._parse_char_class()

        if char == "\\":
            self._advance()
            escaped = self._advance()
            pool = _ESCAPE_POOLS.get(escaped)
            if pool is not None:
                return lambda: get_rng().choice(pool)
            return lambda literal=escaped: literal

        self._advance()
        return lambda literal=char: literal

    def _parse_group(self):
        self._advance()  # consume '('
        if self._pattern[self._pos:self._pos + 2] in ("?=", "?!") or self._pattern[self._pos:self._pos + 3] in (
            "?<=",
            "?<!",
        ):
            raise PatternGenerationError(
                "Les assertions (lookahead/lookbehind) ne sont pas supportées par "
                f"generate_from_pattern : « {self._pattern} ». Écrivez un générateur dédié."
            )
        if self._pattern[self._pos:self._pos + 2] == "?:":
            self._pos += 2

        value = self._parse_alternation()
        if self._peek() != ")":
            raise PatternGenerationError(f"Parenthèse non fermée dans le motif « {self._pattern} »")
        self._advance()  # consume ')'
        return lambda literal=value: literal

    def _parse_char_class(self):
        self._advance()  # consume '['
        negate = False
        if self._peek() == "^":
            negate = True
            self._advance()

        pool_chars: list[str] = []
        while self._peek() is not None and self._peek() != "]":
            char = self._advance()
            if self._peek() == "-" and self._pattern[self._pos + 1:self._pos + 2] not in ("", "]"):
                self._advance()  # consume '-'
                end_char = self._advance()
                pool_chars.extend(chr(code) for code in range(ord(char), ord(end_char) + 1))
            else:
                pool_chars.append(char)

        if self._peek() != "]":
            raise PatternGenerationError(f"Classe de caractères non fermée dans le motif « {self._pattern} »")
        self._advance()  # consume ']'

        if negate:
            universe = string.printable.strip()
            pool_chars = [char for char in universe if char not in pool_chars]

        if not pool_chars:
            raise PatternGenerationError(f"Classe de caractères vide dans le motif « {self._pattern} »")

        pool = tuple(pool_chars)
        return lambda: get_rng().choice(pool)


def generate_from_pattern(pattern: str) -> str:
    """Génère une chaîne aléatoire conforme au motif regex `pattern`."""
    return _PatternParser(pattern).generate()
