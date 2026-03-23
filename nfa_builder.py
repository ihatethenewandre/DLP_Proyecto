# --------------------------------------------------------------------------------------------------------
# nfa_builder.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Constructor de AFN mediante la construcción de Thompson
#
#              Recibe un AST de expresión regular y lo transforma en un Autómata Finito
#              No Determinista (AFN) con transiciones epsilon. Implementa cada operador
#              del álgebra regular (concatenación, alternación, Kleene, positiva, opcional
#              y diferencia de conjuntos) como una transformación local de estados. Al
#              final, combina todos los AFN individuales en un único autómata maestro.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass, field
from regex_parser import (
    RENode, CharNode, CharClassNode, ConcatNode, AlternNode,
    StarNode, PlusNode, QuestionNode, DiffNode, EofNode, AnyCharNode
)

EPSILON = None   # Las transiciones epsilon se representan con None
EOF_MARKER = -1  # Símbolo especial para fin de archivo


# ------------------------------------------------ ESTADO DEL AFN ------------------------------------------------

@dataclass
class NFAState:
    """Representa un estado individual dentro del AFN."""
    id: int
    transitions: dict[int | None, list[NFAState]] = field(default_factory=dict)
    is_accept: bool = False
    accept_rule: int = -1  # Índice de la regla asociada (para resolver prioridad)

    def add_transition(self, symbol: int | None, target: 'NFAState'):
        """Agrega una arista al estado. symbol=None indica transición epsilon."""
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        self.transitions[symbol].append(target)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, NFAState) and self.id == other.id

    def __repr__(self):
        return f"S{self.id}"


# ------------------------------------------------ CLASE AFN ------------------------------------------------

class NFA:
    """Autómata Finito No Determinista con un estado inicial y uno de aceptación."""

    _next_id = 0

    def __init__(self, start: NFAState, accept: NFAState):
        self.start = start
        self.accept = accept

    @classmethod
    def new_state(cls) -> NFAState:
        state = NFAState(cls._next_id)
        cls._next_id += 1
        return state

    @classmethod
    def reset_ids(cls):
        cls._next_id = 0

    def get_all_states(self) -> set[NFAState]:
        """Recorre el grafo y retorna todos los estados alcanzables."""
        visited = set()
        stack = [self.start]
        while stack:
            state = stack.pop()
            if state in visited:
                continue
            visited.add(state)
            for targets in state.transitions.values():
                for t in targets:
                    if t not in visited:
                        stack.append(t)
        return visited


# ------------------------------------------------ CONSTRUCCIÓN DE THOMPSON ------------------------------------------------

def build_nfa(node: RENode) -> NFA:
    """
    Aplica la construcción de Thompson de forma recursiva sobre el AST.
    Cada tipo de nodo genera un fragmento de AFN con un start y un accept.
    """

    # Literal: un solo carácter
    if isinstance(node, CharNode):
        start = NFA.new_state()
        accept = NFA.new_state()
        start.add_transition(node.char, accept)
        return NFA(start, accept)

    # Clase de caracteres: una transición por cada símbolo del conjunto
    elif isinstance(node, CharClassNode):
        start = NFA.new_state()
        accept = NFA.new_state()
        for ch in node.chars:
            start.add_transition(ch, accept)
        return NFA(start, accept)

    # Fin de archivo: transición con marcador especial
    elif isinstance(node, EofNode):
        start = NFA.new_state()
        accept = NFA.new_state()
        start.add_transition(EOF_MARKER, accept)
        return NFA(start, accept)

    # Concatenación: encadenar accept de A con start de B
    elif isinstance(node, ConcatNode):
        nfa1 = build_nfa(node.left)
        nfa2 = build_nfa(node.right)
        nfa1.accept.add_transition(EPSILON, nfa2.start)
        nfa1.accept.is_accept = False
        return NFA(nfa1.start, nfa2.accept)

    # Alternación: nuevo start con epsilon a ambos fragmentos
    elif isinstance(node, AlternNode):
        start = NFA.new_state()
        accept = NFA.new_state()
        nfa1 = build_nfa(node.left)
        nfa2 = build_nfa(node.right)
        start.add_transition(EPSILON, nfa1.start)
        start.add_transition(EPSILON, nfa2.start)
        nfa1.accept.add_transition(EPSILON, accept)
        nfa2.accept.add_transition(EPSILON, accept)
        nfa1.accept.is_accept = False
        nfa2.accept.is_accept = False
        return NFA(start, accept)

    # Cerradura de Kleene: A* (cero o más)
    elif isinstance(node, StarNode):
        start = NFA.new_state()
        accept = NFA.new_state()
        inner = build_nfa(node.child)
        start.add_transition(EPSILON, inner.start)
        start.add_transition(EPSILON, accept)        # Permite cadena vacía
        inner.accept.add_transition(EPSILON, inner.start)  # Loop
        inner.accept.add_transition(EPSILON, accept)
        inner.accept.is_accept = False
        return NFA(start, accept)

    # Cerradura positiva: A+ (una o más)
    elif isinstance(node, PlusNode):
        start = NFA.new_state()
        accept = NFA.new_state()
        inner = build_nfa(node.child)
        start.add_transition(EPSILON, inner.start)
        inner.accept.add_transition(EPSILON, inner.start)  # Loop
        inner.accept.add_transition(EPSILON, accept)
        inner.accept.is_accept = False
        return NFA(start, accept)

    # Opcional: A? (cero o una)
    elif isinstance(node, QuestionNode):
        start = NFA.new_state()
        accept = NFA.new_state()
        inner = build_nfa(node.child)
        start.add_transition(EPSILON, inner.start)
        start.add_transition(EPSILON, accept)  # Permite cadena vacía
        inner.accept.add_transition(EPSILON, accept)
        inner.accept.is_accept = False
        return NFA(start, accept)

    # Diferencia de conjuntos: A # B
    elif isinstance(node, DiffNode):
        left_chars = _get_charset(node.left)
        right_chars = _get_charset(node.right)
        diff = left_chars - right_chars
        start = NFA.new_state()
        accept = NFA.new_state()
        for ch in diff:
            start.add_transition(ch, accept)
        return NFA(start, accept)

    else:
        raise ValueError(f"Nodo de AST no soportado: {type(node)}")


def _get_charset(node: RENode) -> set[int]:
    """Extrae el conjunto de ordinales de un nodo CharClass o Char."""
    if isinstance(node, CharClassNode):
        return node.chars
    elif isinstance(node, CharNode):
        return {node.char}
    else:
        raise ValueError(f"Operador # requiere conjuntos de caracteres, no {type(node)}")


# ------------------------------------------------ COMBINACIÓN DE AFNS ------------------------------------------------

def combine_nfas(nfas: list[tuple[NFA, int]]) -> NFA:
    """
    Crea un nuevo estado inicial con transiciones epsilon hacia cada AFN individual.
    El índice de regla se guarda en cada estado de aceptación para resolver prioridad.
    """
    start = NFA.new_state()
    dummy_accept = NFA.new_state()

    for nfa, rule_idx in nfas:
        start.add_transition(EPSILON, nfa.start)
        nfa.accept.is_accept = True
        nfa.accept.accept_rule = rule_idx

    return NFA(start, dummy_accept)


# ------------------------------------------------ FUNCIONES AUXILIARES ------------------------------------------------

def epsilon_closure(states: set[NFAState]) -> frozenset[NFAState]:
    """Calcula la epsilon-cerradura: todos los estados alcanzables solo con epsilon."""
    stack = list(states)
    closure = set(states)
    while stack:
        state = stack.pop()
        if EPSILON in state.transitions:
            for target in state.transitions[EPSILON]:
                if target not in closure:
                    closure.add(target)
                    stack.append(target)
    return frozenset(closure)


def move(states: frozenset[NFAState], symbol: int) -> set[NFAState]:
    """Calcula move(S, a): todos los estados alcanzables desde S consumiendo el símbolo a."""
    result = set()
    for state in states:
        if symbol in state.transitions:
            for target in state.transitions[symbol]:
                result.add(target)
    return result


# ---------------------------------------- EJECUCIÓN STANDALONE ----------------------------------------

if __name__ == "__main__":
    from regex_parser import parse_regex

    NFA.reset_ids()
    tree = parse_regex("['0'-'9']+")
    nfa = build_nfa(tree)
    states = nfa.get_all_states()

    print("------------------------------------------------------------")
    print("  AFN GENERADO PARA ['0'-'9']+")
    print("------------------------------------------------------------")
    print(f"  Estado inicial:  {nfa.start}")
    print(f"  Estado final:    {nfa.accept}")
    print(f"  Total estados:   {len(states)}")
    print("------------------------------------------------------------")
