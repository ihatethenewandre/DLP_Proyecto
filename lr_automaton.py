# --------------------------------------------------------------------------------------------------------
# lr_automaton.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Construcción del autómata LR(0)
#
#              Implementa ítems LR(0), clausura (closure), función GOTO y la colección
#              canónica de conjuntos de ítems. Estos son los insumos necesarios para
#              construir las tablas ACTION y GOTO del parser SLR(1).
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass, field
from grammar import Grammar, AUGMENTED_START


# ---------------------------------------- ÍTEM LR(0) ----------------------------------------

@dataclass(frozen=True)
class LRItem:
    """
    Ítem LR(0): una producción con un punto (•) en alguna posición del RHS.
    prod_index — índice de la producción en Grammar.productions
    dot        — posición del punto (0 = antes del primer símbolo)
    """
    prod_index: int
    dot: int

    def is_complete(self, grammar: Grammar) -> bool:
        return self.dot >= len(grammar.productions[self.prod_index].rhs)

    def symbol_after_dot(self, grammar: Grammar) -> str | None:
        prod = grammar.productions[self.prod_index]
        if self.dot < len(prod.rhs):
            return prod.rhs[self.dot]
        return None

    def advance(self) -> LRItem:
        return LRItem(self.prod_index, self.dot + 1)

    def __repr__(self):
        return f"LRItem(prod={self.prod_index}, dot={self.dot})"


# ---------------------------------------- ESTADO DEL AUTÓMATA ----------------------------------------

@dataclass
class LRState:
    """Un estado del autómata LR(0): un conjunto de ítems con sus transiciones."""
    id: int
    items: frozenset[LRItem]
    transitions: dict[str, int] = field(default_factory=dict)  # símbolo → estado_id

    def __repr__(self):
        return f"State({self.id}, items={len(self.items)}, trans={list(self.transitions.keys())})"


# ---------------------------------------- CLAUSURA ----------------------------------------

def closure(items: frozenset[LRItem], grammar: Grammar) -> frozenset[LRItem]:
    """
    Clausura de un conjunto de ítems LR(0).
    Para cada ítem A → α • B β, agrega B → • γ para toda producción de B.
    """
    result = set(items)
    worklist = list(items)

    while worklist:
        item = worklist.pop()
        sym = item.symbol_after_dot(grammar)
        if sym is not None and sym in grammar.nonterminals:
            for prod in grammar.productions_for(sym):
                new_item = LRItem(prod.index, 0)
                if new_item not in result:
                    result.add(new_item)
                    worklist.append(new_item)

    return frozenset(result)


# ---------------------------------------- GOTO ----------------------------------------

def goto(items: frozenset[LRItem], symbol: str, grammar: Grammar) -> frozenset[LRItem]:
    """
    GOTO(I, X): clausura de todos los ítems A → α X • β
    donde A → α • X β estaba en I.
    """
    moved = frozenset(
        item.advance()
        for item in items
        if item.symbol_after_dot(grammar) == symbol
    )
    if not moved:
        return frozenset()
    return closure(moved, grammar)


# ---------------------------------------- COLECCIÓN CANÓNICA ----------------------------------------

def build_canonical_collection(grammar: Grammar) -> tuple[list[LRState], dict[frozenset, int]]:
    """
    Construye la colección canónica de conjuntos de ítems LR(0).
    Retorna (lista de estados, mapa frozenset→id).
    """
    # Estado inicial: clausura de {S' → • start}
    aug_prod = grammar.productions[0]
    start_item = LRItem(aug_prod.index, 0)
    start_set = closure(frozenset([start_item]), grammar)

    states: list[LRState] = []
    state_map: dict[frozenset, int] = {}

    def get_or_create(item_set: frozenset) -> int:
        if item_set in state_map:
            return state_map[item_set]
        sid = len(states)
        state_map[item_set] = sid
        states.append(LRState(id=sid, items=item_set))
        return sid

    get_or_create(start_set)
    worklist = [0]

    while worklist:
        sid = worklist.pop()
        state = states[sid]

        # Reunir todos los símbolos después del punto
        symbols_after_dot: set[str] = set()
        for item in state.items:
            sym = item.symbol_after_dot(grammar)
            if sym is not None:
                symbols_after_dot.add(sym)

        for sym in symbols_after_dot:
            next_set = goto(state.items, sym, grammar)
            if not next_set:
                continue
            next_id = get_or_create(next_set)
            state.transitions[sym] = next_id
            if next_id == len(states) - 1:  # recién creado
                worklist.append(next_id)

    return states, state_map


# ---------------------------------------- DEBUG ----------------------------------------

def print_automaton(states: list[LRState], grammar: Grammar):
    print(f"  Colección canónica: {len(states)} estados")
    for state in states:
        print(f"\n  Estado {state.id}:")
        for item in sorted(state.items, key=lambda x: (x.prod_index, x.dot)):
            prod = grammar.productions[item.prod_index]
            rhs = list(prod.rhs)
            rhs.insert(item.dot, '•')
            print(f"    {prod.lhs} → {' '.join(rhs) if rhs else 'ε'}")
        if state.transitions:
            for sym, tgt in sorted(state.transitions.items()):
                print(f"    -- {sym} --> Estado {tgt}")
