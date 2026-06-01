# --------------------------------------------------------------------------------------------------------
# lalr_table.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Construcción de tablas ACTION y GOTO para el parser LALR(1)
#
#              Implementa el algoritmo LALR(1) mediante fusión de estados LR(1) que
#              comparten el mismo núcleo (mismos ítems LR(0)). Las tablas resultantes
#              son más precisas que SLR(1) porque usan lookaheads exactos en lugar
#              de conjuntos FOLLOW conservadores.
#
#              LALR(1) acepta estrictamente más gramáticas que SLR(1) porque sus
#              lookaheads son un subconjunto de los conjuntos FOLLOW utilizados por SLR.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from grammar import Grammar, END_OF_INPUT, AUGMENTED_START
from lr1_automaton import LR1Item, LR1State, build_lr1_canonical_collection


# ---------------------------------------- TIPOS DE ACCIÓN ----------------------------------------

SHIFT  = 'shift'
REDUCE = 'reduce'
ACCEPT = 'accept'
ERROR  = 'error'


# ---------------------------------------- TABLAS LALR ----------------------------------------

class LALRTables:
    """
    Tablas ACTION y GOTO para el parser LALR(1).

    Misma estructura que SLRTables, compatible con generate_parser().

    action[state_id][terminal]   → ('shift', next_state)
                                 | ('reduce', prod_index)
                                 | ('accept',)
    goto[state_id][nonterminal]  → next_state_id
    """

    def __init__(self):
        self.action: dict[int, dict[str, tuple]] = {}
        self.goto: dict[int, dict[str, int]] = {}
        self.conflicts: list[str] = []
        self.states: list = []
        self.grammar: Grammar | None = None
        self.num_lr1_states: int = 0
        self.num_lalr_states: int = 0

    def _set_action(self, state: int, terminal: str, entry: tuple):
        if state not in self.action:
            self.action[state] = {}
        existing = self.action[state].get(terminal)
        if existing is not None and existing != entry:
            kind1, kind2 = existing[0], entry[0]
            conflict_type = f"{kind1}-{kind2}"
            msg = (f"  CONFLICTO {conflict_type.upper()} en Estado {state}, "
                   f"terminal '{terminal}': {existing} vs {entry}")
            self.conflicts.append(msg)
            # Shift sobre reduce (resolución estándar)
            if SHIFT in (kind1, kind2) and REDUCE in (kind1, kind2):
                if entry[0] == SHIFT:
                    self.action[state][terminal] = entry
                return
            # Reduce-reduce: preferir producción de menor índice
            if kind1 == REDUCE and kind2 == REDUCE:
                if entry[1] < existing[1]:
                    self.action[state][terminal] = entry
                return
        else:
            self.action[state][terminal] = entry


# ---------------------------------------- CONSTRUCCIÓN LALR ----------------------------------------

def build_lalr_tables(grammar: Grammar) -> LALRTables:
    """
    Construye tablas LALR(1) en tres pasos:
      1. Calcular la colección canónica LR(1).
      2. Fusionar estados con el mismo núcleo (mismos ítems LR(0), distintos lookaheads).
      3. Construir ACTION y GOTO usando los lookaheads fusionados.

    El estado 0 del LR(1) se mapea siempre al estado 0 del LALR, garantizando que
    _START_STATE = 0 en el parser generado.
    """
    tables = LALRTables()
    tables.grammar = grammar

    # ---- Paso 1: Colección LR(1) ----
    lr1_states, _ = build_lr1_canonical_collection(grammar)
    tables.num_lr1_states = len(lr1_states)

    # ---- Paso 2: Agrupar por núcleo ----
    # Iterar en orden para que el estado 0 (inicio) quede como new_id = 0
    core_to_group: dict[frozenset, list[int]] = {}
    for state in lr1_states:              # orden: 0, 1, 2, …
        core = state.core()
        if core not in core_to_group:
            core_to_group[core] = []
        core_to_group[core].append(state.id)

    # Asignar IDs LALR (primer core procesado = id 0 = estado inicial)
    old_to_new: dict[int, int] = {}
    new_items_list: list[frozenset[LR1Item]] = []
    new_transitions_list: list[dict[str, int]] = []

    for core, old_ids in core_to_group.items():
        new_id = len(new_items_list)
        # Unir todos los ítems LR(1) de los estados con este núcleo
        merged: set[LR1Item] = set()
        for oid in old_ids:
            merged |= set(lr1_states[oid].items)
        new_items_list.append(frozenset(merged))
        new_transitions_list.append({})
        for oid in old_ids:
            old_to_new[oid] = new_id

    # Reconstruir transiciones con los nuevos IDs
    for old_state in lr1_states:
        new_id = old_to_new[old_state.id]
        for sym, old_next in old_state.transitions.items():
            new_next = old_to_new[old_next]
            new_transitions_list[new_id][sym] = new_next

    tables.num_lalr_states = len(new_items_list)
    tables.states = new_items_list

    # ---- Paso 3: Construir ACTION y GOTO ----
    aug_prod = grammar.productions[0]  # S' → start_symbol

    for new_id, items in enumerate(new_items_list):
        for item in items:
            prod = grammar.productions[item.prod_index]

            if item.is_complete(grammar):
                if prod.lhs == AUGMENTED_START:
                    # S' → start • con lookahead $ → ACCEPT
                    tables._set_action(new_id, END_OF_INPUT, (ACCEPT,))
                else:
                    # Reducir usando el lookahead exacto del ítem LR(1)
                    tables._set_action(new_id, item.lookahead, (REDUCE, prod.index))
            else:
                sym = item.symbol_after_dot(grammar)
                if sym is None:
                    continue

                if grammar.is_terminal(sym):
                    if sym in new_transitions_list[new_id]:
                        next_id = new_transitions_list[new_id][sym]
                        tables._set_action(new_id, sym, (SHIFT, next_id))
                else:
                    if sym in new_transitions_list[new_id]:
                        next_id = new_transitions_list[new_id][sym]
                        if new_id not in tables.goto:
                            tables.goto[new_id] = {}
                        tables.goto[new_id][sym] = next_id

    return tables


# ---------------------------------------- DEBUG ----------------------------------------

def print_lalr_tables(tables: LALRTables, grammar: Grammar):
    print(f"\n  Tabla ACTION (LALR):")
    for sid in sorted(tables.action):
        for term, act in sorted(tables.action[sid].items()):
            print(f"    ACTION[{sid}][{term}] = {act}")
    print(f"\n  Tabla GOTO (LALR):")
    for sid in sorted(tables.goto):
        for nt, nxt in sorted(tables.goto[sid].items()):
            print(f"    GOTO[{sid}][{nt}] = {nxt}")
    if tables.conflicts:
        print(f"\n  CONFLICTOS LALR ({len(tables.conflicts)}):")
        for c in tables.conflicts:
            print(c)