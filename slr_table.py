# --------------------------------------------------------------------------------------------------------
# slr_table.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Construcción de tablas ACTION y GOTO para el parser SLR(1)
#
#              Aplica las reglas SLR sobre el autómata LR(0) y los conjuntos FOLLOW para
#              generar las tablas de parseo. Detecta y reporta conflictos shift-reduce y
#              reduce-reduce. Las tablas resultantes son el insumo del generador de código.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from grammar import Grammar, END_OF_INPUT, AUGMENTED_START
from lr_automaton import LRState, LRItem, build_canonical_collection


# ---------------------------------------- TIPOS DE ACCIÓN ----------------------------------------

SHIFT  = 'shift'
REDUCE = 'reduce'
ACCEPT = 'accept'
ERROR  = 'error'


# ---------------------------------------- TABLAS SLR ----------------------------------------

class SLRTables:
    """
    Tablas ACTION y GOTO para el parser SLR(1).

    action[state_id][terminal]    → ('shift', next_state)
                                  | ('reduce', prod_index)
                                  | ('accept',)
    goto[state_id][nonterminal]   → next_state_id
    """

    def __init__(self):
        self.action: dict[int, dict[str, tuple]] = {}
        self.goto: dict[int, dict[str, int]] = {}
        self.conflicts: list[str] = []
        self.states: list[LRState] = []
        self.grammar: Grammar | None = None

    def _set_action(self, state: int, terminal: str, entry: tuple):
        if state not in self.action:
            self.action[state] = {}
        existing = self.action[state].get(terminal)
        if existing is not None and existing != entry:
            kind1, kind2 = existing[0], entry[0]
            conflict_type = f"{kind1}-{kind2}" if kind1 != kind2 else f"{kind1}-{kind2}"
            msg = (f"  CONFLICTO {conflict_type.upper()} en Estado {state}, "
                   f"terminal '{terminal}': {existing} vs {entry}")
            self.conflicts.append(msg)
            # Para shift-reduce: preferir shift (comportamiento estándar)
            if SHIFT in (kind1, kind2) and REDUCE in (kind1, kind2):
                if entry[0] == SHIFT:
                    self.action[state][terminal] = entry
                # else: mantener el shift existente
                return
            # Para reduce-reduce: preferir la producción de menor índice
            if kind1 == REDUCE and kind2 == REDUCE:
                if entry[1] < existing[1]:
                    self.action[state][terminal] = entry
                return
        else:
            self.action[state][terminal] = entry


def build_slr_tables(grammar: Grammar) -> SLRTables:
    """
    Construye las tablas SLR(1) a partir de la gramática aumentada.
    """
    tables = SLRTables()
    tables.grammar = grammar

    states, _ = build_canonical_collection(grammar)
    tables.states = states

    aug_prod = grammar.productions[0]  # S' → start_symbol

    for state in states:
        sid = state.id

        for item in state.items:
            prod = grammar.productions[item.prod_index]

            if item.is_complete(grammar):
                # Ítem completo: A → α •
                if prod.lhs == AUGMENTED_START:
                    # S' → start • : ACCEPT en $
                    tables._set_action(sid, END_OF_INPUT, (ACCEPT,))
                else:
                    # Reducir por esta producción en cada terminal de FOLLOW(A)
                    for terminal in grammar.follow(prod.lhs):
                        if terminal in grammar.terminals:
                            tables._set_action(sid, terminal, (REDUCE, prod.index))
            else:
                sym = item.symbol_after_dot(grammar)
                if sym is None:
                    continue

                if grammar.is_terminal(sym):
                    # Shift: A → α • a β, y GOTO(state, a) = next
                    if sym in state.transitions:
                        next_sid = state.transitions[sym]
                        tables._set_action(sid, sym, (SHIFT, next_sid))
                else:
                    # GOTO para no-terminales
                    if sym in state.transitions:
                        next_sid = state.transitions[sym]
                        if sid not in tables.goto:
                            tables.goto[sid] = {}
                        tables.goto[sid][sym] = next_sid

    return tables


# ---------------------------------------- DEBUG ----------------------------------------

def print_tables(tables: SLRTables, grammar: Grammar):
    print(f"\n  Tabla ACTION:")
    for sid in sorted(tables.action):
        for term, act in sorted(tables.action[sid].items()):
            print(f"    ACTION[{sid}][{term}] = {act}")
    print(f"\n  Tabla GOTO:")
    for sid in sorted(tables.goto):
        for nt, nxt in sorted(tables.goto[sid].items()):
            print(f"    GOTO[{sid}][{nt}] = {nxt}")
    if tables.conflicts:
        print(f"\n  CONFLICTOS ({len(tables.conflicts)}):")
        for c in tables.conflicts:
            print(c)
