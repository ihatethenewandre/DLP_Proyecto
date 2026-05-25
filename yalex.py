#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------------------
# yalex.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Punto de entrada para el generador de lexers YALex
#
#              Orquestra un pipeline de 4 fases que convierte una especificación .yal en un lexer Python: (1) lee y preprocesa, (2) parsea expresiones regulares a AST, (3) construye AFD directo (followpos) con alfabeto de clases de símbolo y minimización de Hopcroft, (4) emite fuente lexer autónomo con tablas de transición y clases estáticas.
#
# Authors:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:        23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

import sys
import os
import time

from reader import parse_yalex
from regex_parser import parse_regex
from dfa_builder import build_dfa_direct, minimize_dfa
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
    print()
    print("  [1/4] LECTURA Y PREPROCESAMIENTO")
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
    print()
    print("  [2/4] PARSING DE EXPRESIONES REGULARES")
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
    print()
    print("  [3/4] AFD DIRECTO (FOLLOWPOS) + MINIMIZACIÓN")
    print("  ----------------------------------------")
    dfa = build_dfa_direct(trees)
    accept_count = sum(1 for s in dfa.states if s.is_accept)
    byte_classes = len(dfa.class_signatures)
    ratio = (256 / byte_classes) if byte_classes else 0.0
    print(f"  Tabla de posiciones (hojas): {dfa.position_count}")
    print(f"  Clases de byte (alfabeto):   {byte_classes}  (~{ratio:.2f} bytes/clase)")
    print(f"  AFD inicial:        {len(dfa.states)} estados, {accept_count} de aceptación")
    if dfa.eof_class_id is not None:
        print(f"  Clase EOF (patrones eof):    id={dfa.eof_class_id}")
    else:
        print(f"  Clase EOF:                   no")

    min_dfa = minimize_dfa(dfa)
    min_accept = sum(1 for s in min_dfa.states if s.is_accept)
    trans_count = sum(len(s.transitions) for s in min_dfa.states)
    eof_steps = sum(1 for s in min_dfa.states if s.eof_transition is not None)
    print(f"  AFD minimizado:     {len(min_dfa.states)} estados, {min_accept} de aceptación")
    print(f"  Transiciones:       {trans_count} (+ {eof_steps} aristas EOF explícitas)")
    print(f"  Alfabeto (clases):  {len(min_dfa.alphabet)} ids en uso")

    # ---------------------------------------- FASE 4 ----------------------------------------
    print()
    print("  [4/4] GENERACIÓN DE CÓDIGO")
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
