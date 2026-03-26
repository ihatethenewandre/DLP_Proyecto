#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------------------
# yalex.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Punto de entrada del generador de analizadores léxicos YALex
#
#              Orquesta el pipeline completo de 5 fases que transforma un archivo de
#              especificación .yal en un programa Python funcional capaz de tokenizar
#              archivos fuente. Las fases son: (1) lectura y preprocesamiento, (2) parsing
#              de expresiones regulares a AST, (3) construcción de Thompson para generar
#              AFNs, (4) conversión AFN→AFD con minimización, y (5) generación del código
#              fuente del analizador léxico con tabla de transiciones estática.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

import sys
import os
import time

from reader import parse_yalex
from regex_parser import parse_regex
from nfa_builder import NFA, build_nfa, combine_nfas
from dfa_builder import nfa_to_dfa, minimize_dfa
from code_generator import generate_lexer


# ---------------------------------------- PIPELINE PRINCIPAL ----------------------------------------

def main():
    # Validar argumentos de línea de comandos
    if len(sys.argv) < 2:
        print("------------------------------------------------------------")
        print("  YALEX — GENERADOR DE ANALIZADORES LÉXICOS")
        print("------------------------------------------------------------")
        print(f"  Uso: python {sys.argv[0]} <archivo.yal> [-o <salida.py>]")
        print("------------------------------------------------------------")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = "generated_lexer.py"

    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
            if not output_file.endswith('.py'):
                output_file += '.py'

    if not os.path.exists(input_file):
        print(f"  ERROR: No se encontró el archivo '{input_file}'")
        sys.exit(1)

    print()
    print("============================================================")
    print("  YALEX — GENERADOR DE ANALIZADORES LÉXICOS")
    print("============================================================")

    t_start = time.time()

    # ---------------------------------------- FASE 1 ----------------------------------------
    # LECTOR Y PREPROCESADOR
    # ----------------------------------------

    print()
    print("  [1/5] LECTURA Y PREPROCESAMIENTO")
    print("  ----------------------------------------")
    spec = parse_yalex(input_file)

    print(f"  Archivo:        {input_file}")
    print(f"  Header:         {'Sí' if spec.header else 'No'}")
    print(f"  Definiciones:   {len(spec.definitions)}")
    for d in spec.definitions:
        print(f"    let {d.name} = {d.pattern}")
    print(f"  Entry point:    {spec.entry_name}")
    print(f"  Reglas:         {len(spec.rules)}")
    for i, r in enumerate(spec.rules):
        action_preview = r.action[:35] + "..." if len(r.action) > 35 else r.action
        print(f"    [{i:2d}] {r.pattern[:45]:45s} -> {{{action_preview}}}")
    print(f"  Trailer:        {'Sí' if spec.trailer else 'No'}")

    # ---------------------------------------- FASE 2 ----------------------------------------
    # PARSER DE EXPRESIONES REGULARES
    # ----------------------------------------

    print()
    print("  [2/5] PARSING DE EXPRESIONES REGULARES")
    print("  ----------------------------------------")

    definitions = {}
    for d in spec.definitions:
        definitions[d.name] = d.pattern

    trees = []
    for i, rule in enumerate(spec.rules):
        try:
            tree = parse_regex(rule.pattern, definitions)
            trees.append(tree)
            print(f"    [{i:2d}] OK  {rule.pattern[:50]}")
        except Exception as e:
            print(f"    [{i:2d}] ERR {rule.pattern}: {e}")
            sys.exit(1)

    print(f"  Total: {len(trees)} expresiones parseadas")

    # ---------------------------------------- FASE 3 ----------------------------------------
    # CONSTRUCCIÓN DE AFN (THOMPSON)
    # ----------------------------------------

    print()
    print("  [3/5] CONSTRUCCIÓN DE AFN (THOMPSON)")
    print("  ----------------------------------------")
    NFA.reset_ids()

    nfas = []
    for i, tree in enumerate(trees):
        nfa = build_nfa(tree)
        nfas.append((nfa, i))

    combined_nfa = combine_nfas(nfas)

    # Contar estados totales del AFN combinado
    all_states = set()
    stack = [combined_nfa.start]
    while stack:
        s = stack.pop()
        if s in all_states:
            continue
        all_states.add(s)
        for targets in s.transitions.values():
            for t in targets:
                if t not in all_states:
                    stack.append(t)

    print(f"  AFN combinado:  {len(all_states)} estados")

    # ---------------------------------------- FASE 4 ----------------------------------------
    # CONVERSIÓN AFN → AFD + MINIMIZACIÓN
    # ----------------------------------------

    print()
    print("  [4/5] CONVERSIÓN AFN → AFD + MINIMIZACIÓN")
    print("  ----------------------------------------")
    dfa = nfa_to_dfa(combined_nfa)
    accept_count = sum(1 for s in dfa.states if s.is_accept)
    print(f"  AFD original:   {len(dfa.states)} estados, {accept_count} de aceptación")

    min_dfa = minimize_dfa(dfa)
    min_accept = sum(1 for s in min_dfa.states if s.is_accept)
    trans_count = sum(len(s.transitions) for s in min_dfa.states)
    print(f"  AFD minimizado: {len(min_dfa.states)} estados, {min_accept} de aceptación")
    print(f"  Transiciones:   {trans_count}")
    print(f"  Alfabeto:       {len(min_dfa.alphabet)} símbolos")

    # ---------------------------------------- FASE 5 ----------------------------------------
    # GENERACIÓN DE CÓDIGO
    # ----------------------------------------

    print()
    print("  [5/5] GENERACIÓN DE CÓDIGO")
    print("  ----------------------------------------")

    output_path = generate_lexer(
        dfa=min_dfa, rules=spec.rules, entry_name=spec.entry_name,
        header=spec.header, trailer=spec.trailer, output_file=output_file
    )
    print(f"  Archivo generado: {output_path}")

    t_end = time.time()

    print()
    print("============================================================")
    print(f"  COMPLETADO EN {t_end - t_start:.3f}s")
    print(f"  Ejecutar con: python {output_path} <archivo_fuente>")
    print("============================================================")
    print()


if __name__ == "__main__":
    main()
