# --------------------------------------------------------------------------------------------------------
# grammar.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Estructuras de gramática y cálculo de conjuntos FIRST / FOLLOW
#
#              Recibe las producciones del lector YAPar y calcula los conjuntos FIRST y FOLLOW
#              necesarios para construir las tablas de parseo SLR(1). También se encarga de
#              aumentar la gramática agregando S' → start_symbol.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from yapar_reader import YAParProduction, YAParSpec

EPSILON = 'ε'
END_OF_INPUT = '$'
AUGMENTED_START = "S'"


# ---------------------------------------- ESTRUCTURA DE GRAMÁTICA ----------------------------------------

class Grammar:
    """
    Gramática aumentada lista para construcción del autómata LR(0).

    Atributos:
        productions  — lista de YAParProduction (índice 0 = S' → start)
        terminals    — conjunto de símbolos terminales (tokens + $)
        nonterminals — conjunto de no-terminales
        start        — símbolo inicial original
        aug_start    — símbolo inicial aumentado (S')
    """

    def __init__(self, spec: YAParSpec):
        self.terminals: set[str] = set(spec.tokens) | {END_OF_INPUT}
        self.ignored: set[str] = set(spec.ignored)
        self.start: str = spec.start_symbol

        # Producción aumentada S' → start_symbol en índice 0
        aug_prod = YAParProduction(AUGMENTED_START, [spec.start_symbol], 0)
        self.productions: list[YAParProduction] = [aug_prod]
        for i, p in enumerate(spec.productions):
            self.productions.append(YAParProduction(p.lhs, p.rhs, i + 1))

        # Re-indexar
        for i, p in enumerate(self.productions):
            p.index = i

        # Construir conjunto de no-terminales
        self.nonterminals: set[str] = {p.lhs for p in self.productions}
        self.aug_start = AUGMENTED_START

        # Índice: lhs → lista de producciones con ese LHS
        self._lhs_index: dict[str, list[YAParProduction]] = {}
        for p in self.productions:
            self._lhs_index.setdefault(p.lhs, []).append(p)

        self._first: dict[str, set[str]] = {}
        self._follow: dict[str, set[str]] = {}
        self._compute_first()
        self._compute_follow()

    def productions_for(self, lhs: str) -> list[YAParProduction]:
        return self._lhs_index.get(lhs, [])

    def is_terminal(self, sym: str) -> bool:
        return sym not in self.nonterminals

    # ---------------------------------------- FIRST ----------------------------------------

    def _first_of_sequence(self, symbols: list[str]) -> set[str]:
        """FIRST de una secuencia de símbolos (para RHS de producción)."""
        result: set[str] = set()
        for sym in symbols:
            f = self.first(sym)
            result |= f - {EPSILON}
            if EPSILON not in f:
                break
        else:
            result.add(EPSILON)
        return result

    def first(self, sym: str) -> set[str]:
        """Retorna FIRST(sym). Cachea resultados."""
        if sym in self._first:
            return self._first[sym]

        if self.is_terminal(sym):
            self._first[sym] = {sym}
            return self._first[sym]

        # Marcar antes de recursión para evitar ciclos
        self._first[sym] = set()

        for prod in self.productions_for(sym):
            if not prod.rhs:
                self._first[sym].add(EPSILON)
            else:
                self._first[sym] |= self._first_of_sequence(prod.rhs)

        return self._first[sym]

    def _compute_first(self):
        """Iteración hasta punto fijo para FIRST de todos los no-terminales."""
        changed = True
        while changed:
            changed = False
            for nt in self.nonterminals:
                old = frozenset(self._first.get(nt, set()))
                self.first(nt)
                if frozenset(self._first[nt]) != old:
                    changed = True

    # ---------------------------------------- FOLLOW ----------------------------------------

    def follow(self, nt: str) -> set[str]:
        return self._follow.get(nt, set())

    def _compute_follow(self):
        """Iteración hasta punto fijo para FOLLOW de todos los no-terminales."""
        for nt in self.nonterminals:
            self._follow[nt] = set()

        self._follow[self.aug_start].add(END_OF_INPUT)

        changed = True
        while changed:
            changed = False
            for prod in self.productions:
                trailer = set(self._follow.get(prod.lhs, set()))
                for sym in reversed(prod.rhs):
                    if sym in self.nonterminals:
                        old_size = len(self._follow[sym])
                        self._follow[sym] |= trailer
                        if len(self._follow[sym]) != old_size:
                            changed = True
                        if EPSILON in self.first(sym):
                            trailer = trailer | (self.first(sym) - {EPSILON})
                        else:
                            trailer = self.first(sym) - {EPSILON}
                    else:
                        trailer = self.first(sym) - {EPSILON}

    # ---------------------------------------- DEBUG ----------------------------------------

    def print_summary(self):
        print(f"  Terminales ({len(self.terminals)}): {sorted(self.terminals)}")
        print(f"  No-terminales ({len(self.nonterminals)}): {sorted(self.nonterminals)}")
        print(f"  Producciones ({len(self.productions)}):")
        for p in self.productions:
            print(f"    {p}")
        print(f"  FIRST:")
        for nt in sorted(self.nonterminals):
            print(f"    FIRST({nt}) = {sorted(self._first.get(nt, set()))}")
        print(f"  FOLLOW:")
        for nt in sorted(self.nonterminals):
            print(f"    FOLLOW({nt}) = {sorted(self._follow.get(nt, set()))}")
