# --------------------------------------------------------------------------------------------------------
# dfa_builder.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Description: Direct DFA construction (followpos) with symbol-class alphabet and Hopcroft minimization
#
#              Builds a DFA from regex ASTs using the Dragon Book direct construction (nullable,
#              firstpos, lastpos, followpos) and a build-time position table. Input bytes 0..255
#              are partitioned into equivalence classes for transition tables. Optional EOF
#              transitions are represented by a dedicated class id when patterns use eof.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from regex_parser import (
    RENode,
    CharNode,
    CharClassNode,
    ConcatNode,
    AlternNode,
    StarNode,
    PlusNode,
    QuestionNode,
    DiffNode,
    EofNode,
    AnyCharNode,
)

EOF_MARKER = -1


# ------------------------------------------------ BUILD-TIME POSITION TABLE ------------------------------------------------


@dataclass(frozen=True)
class Position:
    """One leaf position in the augmented regex (symbol table row for followpos)."""
    id: int
    chars: frozenset[int]  # May include EOF_MARKER for EofNode leaves; empty for end markers
    is_end_marker: bool
    accept_rule: int  # Rule index for synthetic end markers; -1 otherwise


class PositionTable:
    """Maps position id -> Position; grows as leaves are registered."""

    def __init__(self):
        self.positions: list[Position] = []

    def add_leaf(self, chars: frozenset[int], is_end_marker: bool, accept_rule: int) -> int:
        pid = len(self.positions)
        self.positions.append(Position(pid, chars, is_end_marker, accept_rule))
        return pid

    def add_end_marker(self, accept_rule: int) -> int:
        return self.add_leaf(frozenset(), True, accept_rule)

    def __getitem__(self, pid: int) -> Position:
        return self.positions[pid]

    def __len__(self) -> int:
        return len(self.positions)


@dataclass
class EndMarkerNode(RENode):
    """Synthetic leaf: end of rule #i (only used inside dfa_builder)."""
    rule_index: int


# ------------------------------------------------ AST NORMALIZATION ------------------------------------------------


def _charset_from_node(node: RENode) -> frozenset[int]:
    if isinstance(node, CharNode):
        return frozenset([node.char])
    if isinstance(node, CharClassNode):
        return frozenset(node.chars)
    raise ValueError(f"# operator requires char or char class leaf, got {type(node).__name__}")


def normalize(node: RENode) -> RENode:
    """Lower Diff and AnyChar so followpos only sees Char, CharClass, Eof, EndMarker."""
    if isinstance(node, AnyCharNode):
        return CharClassNode(set(range(256)))
    if isinstance(node, DiffNode):
        left = normalize(node.left)
        right = normalize(node.right)
        lc = set(_charset_from_node(left))
        rc = set(_charset_from_node(right))
        return CharClassNode(lc - rc)
    if isinstance(node, ConcatNode):
        return ConcatNode(normalize(node.left), normalize(node.right))
    if isinstance(node, AlternNode):
        return AlternNode(normalize(node.left), normalize(node.right))
    if isinstance(node, StarNode):
        return StarNode(normalize(node.child))
    if isinstance(node, PlusNode):
        return PlusNode(normalize(node.child))
    if isinstance(node, QuestionNode):
        return QuestionNode(normalize(node.child))
    return node


# ------------------------------------------------ REGISTER LEAVES + ANNOTATE ------------------------------------------------


def register_leaves(node: RENode, ptable: PositionTable) -> None:
    """Assign node._pos_id for every leaf (including EndMarkerNode)."""
    if isinstance(node, CharNode):
        node._pos_id = ptable.add_leaf(frozenset([node.char]), False, -1)  # type: ignore[attr-defined]
    elif isinstance(node, CharClassNode):
        node._pos_id = ptable.add_leaf(frozenset(node.chars), False, -1)  # type: ignore[attr-defined]
    elif isinstance(node, EofNode):
        node._pos_id = ptable.add_leaf(frozenset([EOF_MARKER]), False, -1)  # type: ignore[attr-defined]
    elif isinstance(node, EndMarkerNode):
        node._pos_id = ptable.add_end_marker(node.rule_index)  # type: ignore[attr-defined]
    elif isinstance(node, ConcatNode):
        register_leaves(node.left, ptable)
        register_leaves(node.right, ptable)
    elif isinstance(node, AlternNode):
        register_leaves(node.left, ptable)
        register_leaves(node.right, ptable)
    elif isinstance(node, StarNode):
        register_leaves(node.child, ptable)
    elif isinstance(node, PlusNode):
        register_leaves(node.child, ptable)
    elif isinstance(node, QuestionNode):
        register_leaves(node.child, ptable)
    else:
        raise ValueError(f"Unsupported regex node after normalize: {type(node).__name__}")


def nullable_first_last(node: RENode) -> tuple[bool, frozenset[int], frozenset[int]]:
    """Nullable, firstpos, lastpos for each node (requires _pos_id on leaves)."""
    if isinstance(node, (CharNode, CharClassNode, EofNode, EndMarkerNode)):
        pid = node._pos_id  # type: ignore[attr-defined]
        s = frozenset([pid])
        return False, s, s
    if isinstance(node, ConcatNode):
        n1, f1, l1 = nullable_first_last(node.left)
        n2, f2, l2 = nullable_first_last(node.right)
        nullable = n1 and n2
        first = f1 | (f2 if n1 else frozenset())
        last = l2 | (l1 if n2 else frozenset())
        return nullable, first, last
    if isinstance(node, AlternNode):
        n1, f1, l1 = nullable_first_last(node.left)
        n2, f2, l2 = nullable_first_last(node.right)
        return n1 or n2, f1 | f2, l1 | l2
    if isinstance(node, StarNode):
        _, f, l = nullable_first_last(node.child)
        return True, f, l
    if isinstance(node, PlusNode):
        _, f, l = nullable_first_last(node.child)
        return False, f, l
    if isinstance(node, QuestionNode):
        _, f, l = nullable_first_last(node.child)
        return True, f, l
    raise ValueError(f"Unsupported node: {type(node).__name__}")


def build_followpos(root: RENode, followpos: dict[int, set[int]]) -> None:
    """Populate followpos[p] for each position id p (nullable_first_last must be computable)."""
    if isinstance(root, ConcatNode):
        build_followpos(root.left, followpos)
        build_followpos(root.right, followpos)
        _, _, last1 = nullable_first_last(root.left)
        _, first2, _ = nullable_first_last(root.right)
        for p in last1:
            followpos[p].update(first2)
    elif isinstance(root, AlternNode):
        build_followpos(root.left, followpos)
        build_followpos(root.right, followpos)
    elif isinstance(root, StarNode):
        build_followpos(root.child, followpos)
        _, first1, last1 = nullable_first_last(root.child)
        for p in last1:
            followpos[p].update(first1)
    elif isinstance(root, PlusNode):
        build_followpos(root.child, followpos)
        _, first1, last1 = nullable_first_last(root.child)
        for p in last1:
            followpos[p].update(first1)
    elif isinstance(root, QuestionNode):
        build_followpos(root.child, followpos)


def build_augmented_ast(rule_asts: list[RENode]) -> RENode:
    """(r0 · #0) | (r1 · #1) | ..."""
    if not rule_asts:
        raise ValueError("At least one rule AST is required")
    acc: Optional[RENode] = None
    for i, ast in enumerate(rule_asts):
        branch = ConcatNode(normalize(ast), EndMarkerNode(i))
        if acc is None:
            acc = branch
        else:
            acc = AlternNode(acc, branch)
    assert acc is not None
    return acc


def build_char_classes(ptable: PositionTable) -> tuple[list[int], int, list[frozenset[int]]]:
    """
    Map each byte 0..255 to a class id. Two bytes share a class iff they belong to the same
    set of leaf positions' charsets. Returns (char_to_class list length 256, num_classes, class_signatures).
    """
    n = len(ptable.positions)
    sig_for_byte: list[frozenset[int]] = []
    for b in range(256):
        contained = frozenset(
            pid for pid in range(n)
            if b in ptable[pid].chars and not ptable[pid].is_end_marker
        )
        sig_for_byte.append(contained)

    sig_to_class: dict[frozenset[int], int] = {}
    class_sigs: list[frozenset[int]] = []
    char_to_class = [-1] * 256
    for b in range(256):
        sig = sig_for_byte[b]
        if sig not in sig_to_class:
            sig_to_class[sig] = len(class_sigs)
            class_sigs.append(sig)
        char_to_class[b] = sig_to_class[sig]

    num_classes = len(class_sigs)
    return char_to_class, num_classes, class_sigs


def needs_eof_alphabet(ptable: PositionTable) -> bool:
    return any(EOF_MARKER in ptable[pid].chars for pid in range(len(ptable.positions)))


def representative_byte_for_class(class_id: int, class_sigs: list[frozenset[int]], char_to_class: list[int]) -> int:
    """Any byte in this class (for membership in position charsets)."""
    sig = class_sigs[class_id]
    for b in range(256):
        if char_to_class[b] == class_id:
            return b
    raise RuntimeError("empty class")



# ------------------------------------------------ ESTADO DEL AFD ------------------------------------------------

@dataclass
class DFAState:
    """One DFA state: set of leaf position ids (followpos construction)."""
    id: int
    positions: frozenset[int]
    transitions: dict[int, int] = field(default_factory=dict)  # class_id -> destination state id
    eof_transition: Optional[int] = None  # single step on EOF when input exhausted (optional)
    is_accept: bool = False
    accept_rule: int = -1

    def __hash__(self):
        return self.id

    def __repr__(self):
        tag = f" [accept: rule {self.accept_rule}]" if self.is_accept else ""
        return f"DFA_S{self.id}{tag}"


# ------------------------------------------------ CLASE AFD ------------------------------------------------

class DFA:
    """Deterministic finite automaton over alphabet symbol classes (+ optional EOF class)."""

    def __init__(self):
        self.states: list[DFAState] = []
        self.start_id: int = 0
        self.alphabet: set[int] = set()  # class ids that appear on some transition
        self.char_to_class: list[int] = [-1] * 256
        self.num_classes: int = 0
        self.eof_class_id: Optional[int] = None  # if set, transitions may use this key
        self.class_signatures: list[frozenset[int]] = []
        self.position_count: int = 0  # leaf positions in augmented regex (for diagnostics)

    def add_state(self, positions: frozenset[int], ptable: PositionTable) -> DFAState:
        best_rule = -1
        for pid in positions:
            pos = ptable[pid]
            if pos.is_end_marker:
                if best_rule < 0 or pos.accept_rule < best_rule:
                    best_rule = pos.accept_rule
        st = DFAState(len(self.states), positions, is_accept=best_rule >= 0, accept_rule=best_rule)
        self.states.append(st)
        return st


# ---------------------------------------- CONSTRUCCIÓN DIRECTA DE AFD ----------------------------------------


def build_dfa_direct(rule_asts: list[RENode]) -> DFA:
    """
    Build a DFA from a list of per-rule regex ASTs using followpos and a symbol-class alphabet.
    """
    root = build_augmented_ast(rule_asts)
    ptable = PositionTable()
    register_leaves(root, ptable)
    followpos: dict[int, set[int]] = defaultdict(set)
    build_followpos(root, followpos)
    for pid in range(len(ptable.positions)):
        followpos.setdefault(pid, set())

    char_to_class, num_classes, class_sigs = build_char_classes(ptable)
    eof_needed = needs_eof_alphabet(ptable)
    eof_class_id: Optional[int] = None
    if eof_needed:
        eof_class_id = num_classes
        num_classes += 1

    _, first_root, _ = nullable_first_last(root)
    dfa = DFA()
    dfa.char_to_class = char_to_class
    dfa.num_classes = num_classes
    dfa.eof_class_id = eof_class_id
    dfa.class_signatures = class_sigs

    state_map: dict[frozenset[int], int] = {}
    start_set = first_root
    dfa.add_state(start_set, ptable)
    state_map[start_set] = 0
    worklist: list[frozenset[int]] = [start_set]

    def transition_on_byte(S: frozenset[int], byte_b: int) -> frozenset[int]:
        moved: set[int] = set()
        for pid in S:
            pos = ptable[pid]
            if pos.is_end_marker:
                continue
            if byte_b in pos.chars:
                moved.update(followpos[pid])
        return frozenset(moved)

    def transition_on_eof_symbol(S: frozenset[int]) -> frozenset[int]:
        moved: set[int] = set()
        for pid in S:
            pos = ptable[pid]
            if EOF_MARKER in pos.chars:
                moved.update(followpos[pid])
        return frozenset(moved)

    while worklist:
        S = worklist.pop()
        sid = state_map[S]
        state = dfa.states[sid]

        # Byte classes 0 .. len(class_sigs)-1
        for c in range(len(class_sigs)):
            b = representative_byte_for_class(c, class_sigs, char_to_class)
            U = transition_on_byte(S, b)
            if not U:
                continue
            dfa.alphabet.add(c)
            if U not in state_map:
                new_st = dfa.add_state(U, ptable)
                state_map[U] = new_st.id
                worklist.append(U)
            state.transitions[c] = state_map[U]

        if eof_class_id is not None:
            Ue = transition_on_eof_symbol(S)
            if Ue:
                dfa.alphabet.add(eof_class_id)
                if Ue not in state_map:
                    new_st = dfa.add_state(Ue, ptable)
                    state_map[Ue] = new_st.id
                    worklist.append(Ue)
                state.eof_transition = state_map[Ue]

    dfa.position_count = len(ptable.positions)
    return dfa


# ---------------------------------------- MINIMIZACIÓN DE HOPCROFT ----------------------------------------

def minimize_dfa(dfa: DFA) -> DFA:
    """
    Hopcroft-style partition refinement on DFA states.
    States accepting different rules are never merged.
    """
    if not dfa.states:
        return dfa

    # Partición inicial: separar por regla de aceptación
    accept_groups: dict[int, set[int]] = {}
    non_accept: set[int] = set()
    for state in dfa.states:
        if state.is_accept:
            accept_groups.setdefault(state.accept_rule, set()).add(state.id)
        else:
            non_accept.add(state.id)

    partition: list[set[int]] = []
    if non_accept:
        partition.append(non_accept)
    for group in accept_groups.values():
        partition.append(group)

    if not partition:
        return dfa

    alphabet = sorted(dfa.alphabet)
    eof_id = dfa.eof_class_id

    def state_to_group(sid: int) -> int:
        for i, group in enumerate(partition):
            if sid in group:
                return i
        return -1

    # Refinar particiones hasta estabilizar
    changed = True
    while changed:
        changed = False
        new_partition: list[set[int]] = []
        for group in partition:
            if len(group) <= 1:
                new_partition.append(group)
                continue

            # Crear firma de transición para cada estado del grupo
            subgroups: dict[tuple, set[int]] = {}
            for sid in group:
                st = dfa.states[sid]
                sig: list[tuple[int, int]] = []
                for sym in alphabet:
                    if sym == eof_id:
                        tgt = st.eof_transition if st.eof_transition is not None else -1
                        sig.append((sym, state_to_group(tgt)))
                    else:
                        tgt = st.transitions.get(sym, -1)
                        sig.append((sym, state_to_group(tgt)))
                sig_t = tuple(sig)
                subgroups.setdefault(sig_t, set()).add(sid)
            if len(subgroups) > 1:
                changed = True
                new_partition.extend(subgroups.values())
            else:
                new_partition.append(group)
        partition = new_partition

    # Construir el AFD minimizado a partir de las particiones finales
    min_dfa = DFA()
    min_dfa.alphabet = set(dfa.alphabet)
    min_dfa.char_to_class = list(dfa.char_to_class)
    min_dfa.num_classes = dfa.num_classes
    min_dfa.eof_class_id = dfa.eof_class_id
    min_dfa.class_signatures = list(dfa.class_signatures)
    min_dfa.position_count = dfa.position_count

    group_rep: dict[int, int] = {}
    state_to_new: dict[int, int] = {}

    for i, group in enumerate(partition):
        rep = min(group)
        group_rep[i] = rep
        old = dfa.states[rep]
        new_state = DFAState(
            id=i,
            positions=old.positions,
            is_accept=old.is_accept,
            accept_rule=old.accept_rule,
            eof_transition=old.eof_transition,
        )
        min_dfa.states.append(new_state)
        for sid in group:
            state_to_new[sid] = i

    min_dfa.start_id = state_to_new[dfa.start_id]

    for i, group in enumerate(partition):
        rep = group_rep[i]
        old = dfa.states[rep]
        for sym, target in old.transitions.items():
            min_dfa.states[i].transitions[sym] = state_to_new[target]
        if old.eof_transition is not None:
            min_dfa.states[i].eof_transition = state_to_new[old.eof_transition]

    return min_dfa


# ---------------------------------------- IMPRESIÓN DE DIAGNÓSTICO ----------------------------------------

def print_dfa(dfa: DFA, max_symbols: int = 20):
    """Imprime un resumen del AFD para depuración."""
    accept_states = [s for s in dfa.states if s.is_accept]
    print(f"  States:       {len(dfa.states)}")
    print(f"  Symbols:      {len(dfa.alphabet)} (class ids)")
    print(f"  Start:        S{dfa.start_id}")
    print(f"  Accept:       {len(accept_states)} states")

# ---------------------------------------- EJECUCIÓN STANDALONE ----------------------------------------

if __name__ == "__main__":
    from regex_parser import parse_regex

    trees = [parse_regex(p) for p in ["['0'-'9']+", "['a'-'z']+", "'+'"]]
    dfa = build_dfa_direct(trees)
    print("------------------------------------------------------------")
    print("  AFD SIN MINIMIZAR")
    print("------------------------------------------------------------")
    print_dfa(dfa)
    m = minimize_dfa(dfa)
    print("------------------------------------------------------------")
    print("  AFD MINIMIZADO")
    print("------------------------------------------------------------")
    print_dfa(m)
    print("------------------------------------------------------------")
