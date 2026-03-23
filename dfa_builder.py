# --------------------------------------------------------------------------------------------------------
# dfa_builder.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Conversor de AFN a AFD con minimización
#
#              Elimina el no-determinismo del autómata mediante el algoritmo de construcción
#              de subconjuntos (subset construction). Cada estado del AFD resultante representa
#              un conjunto de estados del AFN original. Posteriormente, aplica el algoritmo de
#              minimización de Hopcroft para reducir el número de estados, preservando siempre
#              la prioridad de las reglas según su orden de definición en el archivo .yal.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass, field
from nfa_builder import (
    NFA, NFAState, epsilon_closure, move, EPSILON, EOF_MARKER
)


# ------------------------------------------------ ESTADO DEL AFD ------------------------------------------------

@dataclass
class DFAState:
    """Estado del AFD. Contiene el conjunto de estados AFN que representa."""
    id: int
    nfa_states: frozenset[NFAState]
    transitions: dict[int, int] = field(default_factory=dict)  # símbolo -> id_destino
    is_accept: bool = False
    accept_rule: int = -1  # Regla con mayor prioridad (menor índice)

    def __hash__(self):
        return self.id

    def __repr__(self):
        tag = f" [accept: regla {self.accept_rule}]" if self.is_accept else ""
        return f"DFA_S{self.id}{tag}"


# ------------------------------------------------ CLASE AFD ------------------------------------------------

class DFA:
    """Autómata Finito Determinista con tabla de transiciones."""

    def __init__(self):
        self.states: list[DFAState] = []
        self.start_id: int = 0
        self.alphabet: set[int] = set()

    def add_state(self, nfa_states: frozenset[NFAState]) -> DFAState:
        """
        Crea un nuevo estado AFD a partir de un conjunto de estados AFN.
        Determina automáticamente si es de aceptación (elige la regla de menor índice).
        """
        state = DFAState(len(self.states), nfa_states)
        self.states.append(state)

        # Regla de mayor prioridad = menor índice
        best_rule = -1
        for nfa_s in nfa_states:
            if nfa_s.is_accept and nfa_s.accept_rule >= 0:
                if best_rule < 0 or nfa_s.accept_rule < best_rule:
                    best_rule = nfa_s.accept_rule

        if best_rule >= 0:
            state.is_accept = True
            state.accept_rule = best_rule

        return state

    def get_transition_table(self) -> dict[int, dict[int, int]]:
        """Retorna la tabla de transiciones como diccionario anidado."""
        table = {}
        for state in self.states:
            table[state.id] = dict(state.transitions)
        return table


# ---------------------------------------- CONSTRUCCIÓN DE SUBCONJUNTOS ----------------------------------------

def nfa_to_dfa(nfa: NFA) -> DFA:
    """
    Convierte un AFN a AFD aplicando el algoritmo de construcción de subconjuntos.
    Calcula epsilon_closure(move(S, a)) para cada símbolo del alfabeto.
    """
    dfa = DFA()

    # Recopilar el alfabeto completo del AFN
    all_nfa_states = set()
    stack = [nfa.start]
    while stack:
        s = stack.pop()
        if s in all_nfa_states:
            continue
        all_nfa_states.add(s)
        for sym, targets in s.transitions.items():
            if sym is not None:
                dfa.alphabet.add(sym)
            for t in targets:
                if t not in all_nfa_states:
                    stack.append(t)

    # Estado inicial del AFD = epsilon_closure del start del AFN
    start_closure = epsilon_closure({nfa.start})
    dfa.add_state(start_closure)
    state_map: dict[frozenset[NFAState], int] = {start_closure: 0}
    worklist = [start_closure]

    # Explorar todos los conjuntos alcanzables
    while worklist:
        current_set = worklist.pop()
        current_id = state_map[current_set]

        for symbol in sorted(dfa.alphabet):
            moved = move(current_set, symbol)
            if not moved:
                continue

            new_set = epsilon_closure(moved)

            if new_set not in state_map:
                new_state = dfa.add_state(new_set)
                state_map[new_set] = new_state.id
                worklist.append(new_set)

            dfa.states[current_id].transitions[symbol] = state_map[new_set]

    return dfa


# ---------------------------------------- MINIMIZACIÓN DE HOPCROFT ----------------------------------------

def minimize_dfa(dfa: DFA) -> DFA:
    """
    Reduce el número de estados del AFD agrupando estados equivalentes.
    Estados que aceptan diferentes reglas nunca se fusionan (preserva prioridad).
    """

    # Partición inicial: separar por regla de aceptación
    accept_groups: dict[int, set[int]] = {}
    non_accept = set()
    for state in dfa.states:
        if state.is_accept:
            if state.accept_rule not in accept_groups:
                accept_groups[state.accept_rule] = set()
            accept_groups[state.accept_rule].add(state.id)
        else:
            non_accept.add(state.id)

    partition: list[set[int]] = []
    if non_accept:
        partition.append(non_accept)
    for group in accept_groups.values():
        partition.append(group)

    if not partition:
        return dfa

    def state_to_group(sid: int) -> int:
        for i, group in enumerate(partition):
            if sid in group:
                return i
        return -1

    # Refinar particiones hasta estabilizar
    changed = True
    while changed:
        changed = False
        new_partition = []

        for group in partition:
            if len(group) <= 1:
                new_partition.append(group)
                continue

            # Crear firma de transición para cada estado del grupo
            subgroups: dict[tuple, set[int]] = {}
            for sid in group:
                state = dfa.states[sid]
                sig = []
                for sym in sorted(dfa.alphabet):
                    target_group = state_to_group(state.transitions[sym]) if sym in state.transitions else -1
                    sig.append((sym, target_group))
                sig_tuple = tuple(sig)
                if sig_tuple not in subgroups:
                    subgroups[sig_tuple] = set()
                subgroups[sig_tuple].add(sid)

            if len(subgroups) > 1:
                changed = True
                for sub in subgroups.values():
                    new_partition.append(sub)
            else:
                new_partition.append(group)

        partition = new_partition

    # Construir el AFD minimizado a partir de las particiones finales
    min_dfa = DFA()
    min_dfa.alphabet = dfa.alphabet

    group_rep: dict[int, int] = {}
    state_to_new: dict[int, int] = {}

    for i, group in enumerate(partition):
        rep = min(group)
        group_rep[i] = rep
        old_state = dfa.states[rep]
        new_state = DFAState(
            id=i, nfa_states=old_state.nfa_states,
            is_accept=old_state.is_accept, accept_rule=old_state.accept_rule
        )
        min_dfa.states.append(new_state)
        for sid in group:
            state_to_new[sid] = i

    min_dfa.start_id = state_to_new[dfa.start_id]

    for i, group in enumerate(partition):
        rep = group_rep[i]
        old_state = dfa.states[rep]
        for sym, target in old_state.transitions.items():
            min_dfa.states[i].transitions[sym] = state_to_new[target]

    return min_dfa


# ---------------------------------------- IMPRESIÓN DE DIAGNÓSTICO ----------------------------------------

def print_dfa(dfa: DFA, max_symbols: int = 20):
    """Imprime un resumen del AFD para depuración."""
    accept_states = [s for s in dfa.states if s.is_accept]
    print(f"  Estados:       {len(dfa.states)}")
    print(f"  Símbolos:      {len(dfa.alphabet)}")
    print(f"  Inicio:        S{dfa.start_id}")
    print(f"  Aceptación:    {len(accept_states)} estados")


# ---------------------------------------- EJECUCIÓN STANDALONE ----------------------------------------

if __name__ == "__main__":
    from regex_parser import parse_regex
    from nfa_builder import build_nfa, combine_nfas, NFA as NFAClass

    NFAClass.reset_ids()
    patterns = [("['0'-'9']+", 0), ("['a'-'z']+", 1), ("'+'", 2)]
    nfas = []
    for pat, idx in patterns:
        tree = parse_regex(pat)
        nfa = build_nfa(tree)
        nfas.append((nfa, idx))

    combined = combine_nfas(nfas)
    dfa = nfa_to_dfa(combined)

    print("------------------------------------------------------------")
    print("  AFD SIN MINIMIZAR")
    print("------------------------------------------------------------")
    print_dfa(dfa)

    min_dfa = minimize_dfa(dfa)
    print("------------------------------------------------------------")
    print("  AFD MINIMIZADO")
    print("------------------------------------------------------------")
    print_dfa(min_dfa)
    print("------------------------------------------------------------")
