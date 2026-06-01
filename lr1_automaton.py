# --------------------------------------------------------------------------------------------------------
# lr1_automaton.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Construcción del autómata LR(1) para soporte LALR(1)
#
#              Implementa ítems LR(1) (ítem LR(0) + lookahead), la clausura LR(1),
#              función GOTO LR(1) y la colección canónica LR(1). Estos son los insumos
#              necesarios para construir las tablas LALR(1) mediante fusión de estados.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass, field
from grammar import Grammar, AUGMENTED_START, EPSILON, END_OF_INPUT


# ---------------------------------------- ÍTEM LR(1) ----------------------------------------

@dataclass(frozen=True)
class LR1Item:
    """
    Ítem LR(1): una producción con punto y un símbolo de lookahead.
    prod_index — índice de la producción en Grammar.productions
    dot        — posición del punto
    lookahead  — símbolo terminal de anticipación
    """
    prod_index: int
    dot: int
    lookahead: str

    def is_complete(self, grammar: Grammar) -> bool:
        return self.dot >= len(grammar.productions[self.prod_index].rhs)

    def symbol_after_dot(self, grammar: Grammar) -> str | None:
        prod = grammar.productions[self.prod_index]
        if self.dot < len(prod.rhs):
            return prod.rhs[self.dot]
        return None

    def advance(self) -> 'LR1Item':
        return LR1Item(self.prod_index, self.dot + 1, self.lookahead)

    def core(self) -> tuple[int, int]:
        """Núcleo del ítem: (prod_index, dot) sin lookahead."""
        return (self.prod_index, self.dot)

    def __repr__(self):
        return f"LR1Item(prod={self.prod_index}, dot={self.dot}, la={self.lookahead!r})"


# ---------------------------------------- ESTADO LR(1) ----------------------------------------

@dataclass
class LR1State:
    """Un estado del autómata LR(1): conjunto de ítems LR(1) con transiciones."""
    id: int
    items: frozenset[LR1Item]
    transitions: dict[str, int] = field(default_factory=dict)

    def core(self) -> frozenset[tuple[int, int]]:
        """Núcleo del estado: ítems sin lookaheads, para fusión LALR."""
        return frozenset(item.core() for item in self.items)


# ---------------------------------------- CLAUSURA LR(1) ----------------------------------------

def lr1_closure(items: frozenset[LR1Item], grammar: Grammar) -> frozenset[LR1Item]:
    """
    Clausura LR(1): para [A → α • B β, a], agrega [B → • γ, b]
    para todo b ∈ FIRST(β a) y toda producción B → γ.
    """
    result = set(items)
    worklist = list(items)

    while worklist:
        item = worklist.pop()
        B = item.symbol_after_dot(grammar)
        if B is None or B not in grammar.nonterminals:
            continue

        # β = símbolos después de B en el RHS
        prod = grammar.productions[item.prod_index]
        beta = list(prod.rhs[item.dot + 1:])

        # FIRST(β a) donde a = lookahead del ítem
        beta_plus_la = beta + [item.lookahead]
        first_set = grammar._first_of_sequence(beta_plus_la)

        for b in first_set:
            if b == EPSILON:
                continue
            for prod_b in grammar.productions_for(B):
                new_item = LR1Item(prod_b.index, 0, b)
                if new_item not in result:
                    result.add(new_item)
                    worklist.append(new_item)

    return frozenset(result)


# ---------------------------------------- GOTO LR(1) ----------------------------------------

def lr1_goto(items: frozenset[LR1Item], symbol: str, grammar: Grammar) -> frozenset[LR1Item]:
    """GOTO LR(1): clausura de los ítems avanzados sobre el símbolo dado."""
    moved = frozenset(
        item.advance()
        for item in items
        if item.symbol_after_dot(grammar) == symbol
    )
    if not moved:
        return frozenset()
    return lr1_closure(moved, grammar)


# ---------------------------------------- COLECCIÓN CANÓNICA LR(1) ----------------------------------------

def build_lr1_canonical_collection(
    grammar: Grammar,
) -> tuple[list[LR1State], dict[frozenset, int]]:
    """
    Construye la colección canónica de conjuntos de ítems LR(1).
    Retorna (lista de estados LR(1), mapa frozenset→id).
    """
    aug_prod = grammar.productions[0]
    start_item = LR1Item(aug_prod.index, 0, END_OF_INPUT)
    start_set = lr1_closure(frozenset([start_item]), grammar)

    states: list[LR1State] = []
    state_map: dict[frozenset, int] = {}

    def get_or_create(item_set: frozenset) -> int:
        if item_set in state_map:
            return state_map[item_set]
        sid = len(states)
        state_map[item_set] = sid
        states.append(LR1State(id=sid, items=item_set))
        return sid

    get_or_create(start_set)
    worklist = [0]

    while worklist:
        sid = worklist.pop()
        state = states[sid]

        symbols: set[str] = set()
        for item in state.items:
            sym = item.symbol_after_dot(grammar)
            if sym is not None:
                symbols.add(sym)

        for sym in symbols:
            next_set = lr1_goto(state.items, sym, grammar)
            if not next_set:
                continue
            next_id = get_or_create(next_set)
            state.transitions[sym] = next_id
            if next_id == len(states) - 1:  # recién creado
                worklist.append(next_id)

    return states, state_map