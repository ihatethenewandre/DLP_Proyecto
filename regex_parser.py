# --------------------------------------------------------------------------------------------------------
# regex_parser.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Parser de expresiones regulares en formato YALex
#
#              Toma cada expresión regular en texto plano y la convierte en un Árbol
#              Sintáctico (AST) que los módulos posteriores pueden procesar. Utiliza un
#              parser recursivo descendente que respeta la jerarquía de precedencia de
#              YALex: # (mayor) > *, +, ? > concatenación > | (menor). Soporta literales
#              de carácter, cadenas, conjuntos, negación, wildcard, eof e identificadores.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ------------------------------------------------ NODOS DEL AST ------------------------------------------------

@dataclass
class RENode:
    """Nodo base abstracto del árbol de expresiones regulares."""
    pass

@dataclass
class CharNode(RENode):
    """Literal de un solo carácter (almacena su valor ordinal)."""
    char: int

    def __repr__(self):
        if 32 <= self.char < 127:
            return f"Char({chr(self.char)!r})"
        return f"Char(\\x{self.char:02x})"

@dataclass
class CharClassNode(RENode):
    """Conjunto de caracteres [abc], [a-z], [^...], etc."""
    chars: set[int]
    negated: bool = False

    def __repr__(self):
        return f"CharClass({len(self.chars)} chars, neg={self.negated})"

@dataclass
class AnyCharNode(RENode):
    """Wildcard _ que denota cualquier símbolo del alfabeto."""
    def __repr__(self):
        return "AnyChar(_)"

@dataclass
class EofNode(RENode):
    """Marcador especial de fin de archivo."""
    def __repr__(self):
        return "EOF"

@dataclass
class ConcatNode(RENode):
    """Concatenación de dos subexpresiones: AB"""
    left: RENode
    right: RENode

    def __repr__(self):
        return f"Concat({self.left}, {self.right})"

@dataclass
class AlternNode(RENode):
    """Alternación (unión) de dos subexpresiones: A|B"""
    left: RENode
    right: RENode

    def __repr__(self):
        return f"Altern({self.left}, {self.right})"

@dataclass
class StarNode(RENode):
    """Cerradura de Kleene: A*"""
    child: RENode

    def __repr__(self):
        return f"Star({self.child})"

@dataclass
class PlusNode(RENode):
    """Cerradura positiva: A+"""
    child: RENode

    def __repr__(self):
        return f"Plus({self.child})"

@dataclass
class QuestionNode(RENode):
    """Expresión opcional: A?"""
    child: RENode

    def __repr__(self):
        return f"Question({self.child})"

@dataclass
class DiffNode(RENode):
    """Diferencia de conjuntos de caracteres: A # B"""
    left: RENode
    right: RENode

    def __repr__(self):
        return f"Diff({self.left}, {self.right})"


# ------------------------------------------------ SECUENCIAS DE ESCAPE ------------------------------------------------

ESCAPE_MAP = {
    'n': ord('\n'), 't': ord('\t'), 'r': ord('\r'), 's': ord(' '),
    '\\': ord('\\'), "'": ord("'"), '"': ord('"'), '0': 0,
}

def parse_escape(ch: str) -> int:
    """Convierte un carácter de escape a su valor ordinal."""
    if ch in ESCAPE_MAP:
        return ESCAPE_MAP[ch]
    return ord(ch)


# ------------------------------------------------ TOKENIZADOR INTERNO ------------------------------------------------

class Token:
    """Token producido por el lexer interno del parser de regex."""
    CHAR = 'CHAR'
    CHARCLASS = 'CHARCLASS'
    ANYCHAR = 'ANYCHAR'
    EOF_TOKEN = 'EOF'
    STAR = 'STAR'
    PLUS = 'PLUS'
    QUESTION = 'QUESTION'
    PIPE = 'PIPE'
    HASH = 'HASH'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    IDENT = 'IDENT'
    END = 'END'

    def __init__(self, kind: str, value=None):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r})"


class RegexLexer:
    """
    Tokeniza una cadena de expresión regular YALex. Produce una lista de
    Token internos que el parser consume mediante peek() y advance().
    """

    def __init__(self, pattern: str, definitions: dict[str, str] = None):
        self.pattern = pattern
        self.pos = 0
        self.definitions = definitions or {}
        self.tokens: list[Token] = []
        self._tokenize()
        self.idx = 0

    def _peek(self) -> Optional[str]:
        if self.pos < len(self.pattern):
            return self.pattern[self.pos]
        return None

    def _advance(self) -> str:
        ch = self.pattern[self.pos]
        self.pos += 1
        return ch

    def _tokenize(self):
        """Recorre la cadena de patrón y genera la lista completa de tokens."""
        while self.pos < len(self.pattern):
            ch = self._peek()

            # Ignorar espacios en blanco
            if ch in ' \t\n\r':
                self._advance()
                continue

            # Carácter entre comillas simples: 'x' o '\n'
            if ch == "'":
                self._advance()
                if self._peek() == '\\':
                    self._advance()
                    val = parse_escape(self._advance())
                else:
                    val = ord(self._advance())
                assert self._advance() == "'", "Se esperaba cierre de comilla simple"
                self.tokens.append(Token(Token.CHAR, val))

            # Cadena entre comillas dobles: "abc"
            elif ch == '"':
                self._advance()
                while self._peek() != '"':
                    if self._peek() == '\\':
                        self._advance()
                        self.tokens.append(Token(Token.CHAR, parse_escape(self._advance())))
                    else:
                        self.tokens.append(Token(Token.CHAR, ord(self._advance())))
                self._advance()

            # Clase de caracteres: [a-z], [^abc], etc.
            elif ch == '[':
                self._advance()
                negated = False
                if self._peek() == '^':
                    negated = True
                    self._advance()
                chars = self._parse_charset()
                assert self._advance() == ']', "Se esperaba cierre de ']'"
                if negated:
                    chars = set(range(0, 256)) - chars
                self.tokens.append(Token(Token.CHARCLASS, chars))

            # Wildcard _ o inicio de identificador
            elif ch == '_':
                self._advance()
                if self.pos < len(self.pattern) and (self.pattern[self.pos].isalnum() or self.pattern[self.pos] == '_'):
                    name = '_'
                    while self.pos < len(self.pattern) and (self.pattern[self.pos].isalnum() or self.pattern[self.pos] == '_'):
                        name += self._advance()
                    if name in self.definitions:
                        self.tokens.append(Token(Token.IDENT, name))
                    else:
                        self.tokens.append(Token(Token.ANYCHAR))
                else:
                    self.tokens.append(Token(Token.ANYCHAR))

            # Operadores de cuantificación y alternación
            elif ch == '*':
                self._advance(); self.tokens.append(Token(Token.STAR))
            elif ch == '+':
                self._advance(); self.tokens.append(Token(Token.PLUS))
            elif ch == '?':
                self._advance(); self.tokens.append(Token(Token.QUESTION))
            elif ch == '|':
                self._advance(); self.tokens.append(Token(Token.PIPE))
            elif ch == '#':
                self._advance(); self.tokens.append(Token(Token.HASH))
            elif ch == '(':
                self._advance(); self.tokens.append(Token(Token.LPAREN))
            elif ch == ')':
                self._advance(); self.tokens.append(Token(Token.RPAREN))

            # Identificador alfanumérico (referencia a definición let o keyword eof)
            elif ch.isalpha():
                name = ''
                while self.pos < len(self.pattern) and (self.pattern[self.pos].isalnum() or self.pattern[self.pos] == '_'):
                    name += self._advance()
                if name == 'eof':
                    self.tokens.append(Token(Token.EOF_TOKEN))
                else:
                    self.tokens.append(Token(Token.IDENT, name))
            else:
                self._advance()

        # Centinela de fin de tokens
        self.tokens.append(Token(Token.END))

    def _parse_charset(self) -> set[int]:
        """Parsea el contenido interno de [ ... ] y retorna el conjunto de ordinales."""
        chars = set()
        while self._peek() is not None and self._peek() != ']':
            ch = self._peek()

            if ch == "'":
                self._advance()
                if self._peek() == '\\':
                    self._advance()
                    c1 = parse_escape(self._advance())
                else:
                    c1 = ord(self._advance())
                assert self._advance() == "'", "Se esperaba cierre de comilla en charset"
                # Verificar si es un rango: 'a'-'z'
                if self._peek() == '-':
                    self._advance()
                    assert self._peek() == "'", "Se esperaba comilla para rango"
                    self._advance()
                    if self._peek() == '\\':
                        self._advance()
                        c2 = parse_escape(self._advance())
                    else:
                        c2 = ord(self._advance())
                    assert self._advance() == "'", "Se esperaba cierre de comilla en rango"
                    for c in range(c1, c2 + 1):
                        chars.add(c)
                else:
                    chars.add(c1)

            elif ch == '"':
                self._advance()
                while self._peek() != '"':
                    if self._peek() == '\\':
                        self._advance()
                        chars.add(parse_escape(self._advance()))
                    else:
                        chars.add(ord(self._advance()))
                self._advance()

            elif ch in ' \t\n':
                self._advance()
            else:
                self._advance()

        return chars

    def peek(self) -> Token:
        return self.tokens[self.idx]

    def advance(self) -> Token:
        tok = self.tokens[self.idx]
        self.idx += 1
        return tok


# ------------------------------------------------ PARSER RECURSIVO DESCENDENTE ------------------------------------------------

class RegexParser:
    """
    Construye un AST a partir de una expresión regular YALex.
    Precedencia (menor a mayor): | < concatenación < *, +, ? < #
    """

    def __init__(self, pattern: str, definitions: dict[str, str] = None):
        self.definitions = definitions or {}
        self.lexer = RegexLexer(pattern, self.definitions)
        self._resolved_cache: dict[str, RENode] = {}

    def parse(self) -> RENode:
        node = self._parse_alternation()
        if self.lexer.peek().kind != Token.END:
            raise SyntaxError(f"Tokens sobrantes tras parsear regex: {self.lexer.peek()}")
        return node

    # Cada nivel de precedencia invoca al siguiente nivel más alto

    def _parse_alternation(self) -> RENode:
        left = self._parse_concat()
        while self.lexer.peek().kind == Token.PIPE:
            self.lexer.advance()
            right = self._parse_concat()
            left = AlternNode(left, right)
        return left

    def _parse_concat(self) -> RENode:
        left = self._parse_quantifier()
        if left is None:
            return left
        while True:
            tok = self.lexer.peek()
            if tok.kind in (Token.CHAR, Token.CHARCLASS, Token.ANYCHAR,
                           Token.LPAREN, Token.IDENT, Token.EOF_TOKEN):
                right = self._parse_quantifier()
                if right is not None:
                    left = ConcatNode(left, right)
                else:
                    break
            else:
                break
        return left

    def _parse_quantifier(self) -> Optional[RENode]:
        node = self._parse_hash()
        if node is None:
            return None
        while self.lexer.peek().kind in (Token.STAR, Token.PLUS, Token.QUESTION):
            tok = self.lexer.advance()
            if tok.kind == Token.STAR:
                node = StarNode(node)
            elif tok.kind == Token.PLUS:
                node = PlusNode(node)
            elif tok.kind == Token.QUESTION:
                node = QuestionNode(node)
        return node

    def _parse_hash(self) -> Optional[RENode]:
        node = self._parse_atom()
        if node is None:
            return None
        while self.lexer.peek().kind == Token.HASH:
            self.lexer.advance()
            right = self._parse_atom()
            node = DiffNode(node, right)
        return node

    def _parse_atom(self) -> Optional[RENode]:
        """Parsea un átomo: literal, clase, wildcard, eof, grupo o referencia a definición."""
        tok = self.lexer.peek()

        if tok.kind == Token.CHAR:
            self.lexer.advance()
            return CharNode(tok.value)
        elif tok.kind == Token.CHARCLASS:
            self.lexer.advance()
            return CharClassNode(tok.value)
        elif tok.kind == Token.ANYCHAR:
            self.lexer.advance()
            return CharClassNode(set(range(0, 256)))
        elif tok.kind == Token.EOF_TOKEN:
            self.lexer.advance()
            return EofNode()
        elif tok.kind == Token.LPAREN:
            self.lexer.advance()
            node = self._parse_alternation()
            assert self.lexer.advance().kind == Token.RPAREN, "Se esperaba ')'"
            return node
        elif tok.kind == Token.IDENT:
            self.lexer.advance()
            name = tok.value
            if name not in self.definitions:
                raise NameError(f"Identificador no definido: {name}")
            # Expandir la definición recursivamente con cache
            if name in self._resolved_cache:
                return self._resolved_cache[name]
            sub_parser = RegexParser(self.definitions[name], self.definitions)
            sub_parser._resolved_cache = self._resolved_cache
            result = sub_parser.parse()
            self._resolved_cache[name] = result
            return result

        return None


# ---------------------------------------- FUNCIÓN DE CONVENIENCIA ----------------------------------------

def parse_regex(pattern: str, definitions: dict[str, str] = None) -> RENode:
    """Punto de entrada rápido: parsea un patrón y retorna su AST."""
    parser = RegexParser(pattern, definitions or {})
    return parser.parse()


# ---------------------------------------- EJECUCIÓN STANDALONE ----------------------------------------

if __name__ == "__main__":
    defs = {"digit": "['0'-'9']", "letter": "['a'-'z' 'A'-'Z']"}
    tests = [
        ("'a'", {}), ("['0'-'9']+", {}), ("digit+", defs),
        ("letter (letter | digit | '_')*", defs),
        ("'a' | 'b' | 'c'", {}), ("\"hello\"", {}),
    ]

    print("------------------------------------------------------------")
    print("  PRUEBAS DEL PARSER DE REGEX")
    print("------------------------------------------------------------")
    for pat, d in tests:
        try:
            tree = parse_regex(pat, d)
            print(f"  OK   {pat:40s} => {tree}")
        except Exception as e:
            print(f"  ERR  {pat:40s} => {e}")
    print("------------------------------------------------------------")
