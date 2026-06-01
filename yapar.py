#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------------------
# yapar.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Punto de entrada para el generador de parsers YAPar
#
#              Orquestra un pipeline de 5 fases que convierte una especificación .yalp
#              en un parser SLR(1) o LALR(1) Python:
#                (0) Invoca YALex opcionalmente (-l)
#                (1) Lee el .yalp
#                (2) Construye la gramática aumentada y calcula FIRST/FOLLOW
#                (3) Construye el autómata LR(0) + genera visualización HTML y DOT
#                (4) Construye tablas SLR(1) o LALR(1) según el flag --lalr
#                (5) Genera el parser Python autónomo
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

import sys
import os
import time

from yapar_reader import parse_yapar
from grammar import Grammar
from lr_automaton import build_canonical_collection, print_automaton
from slr_table import build_slr_tables, print_tables
from lalr_table import build_lalr_tables
from automaton_visualizer import generate_automaton_html, generate_automaton_dot_file
from parser_codegen import generate_parser


# ---------------------------------------- PIPELINE PRINCIPAL ----------------------------------------

def main():
    if len(sys.argv) < 2:
        print("------------------------------------------------------------")
        print("  YAPAR — GENERADOR DE ANALIZADORES SINTÁCTICOS SLR(1) / LALR(1)")
        print("------------------------------------------------------------")
        print(f"  Uso: python {sys.argv[0]} <archivo.yalp> [opciones]")
        print()
        print("  Opciones:")
        print("    -l <lexer.yal>      Invocar YALex sobre el archivo indicado")
        print("    -o <salida.py>      Nombre del parser generado (default: generated_parser.py)")
        print("    --lalr              Generar parser LALR(1) en lugar de SLR(1)")
        print("------------------------------------------------------------")
        sys.exit(1)

    input_file  = sys.argv[1]
    lexer_yal   = None
    output_file = "generated_parser.py"
    use_lalr    = "--lalr" in sys.argv

    if "-l" in sys.argv:
        idx = sys.argv.index("-l")
        if idx + 1 < len(sys.argv):
            lexer_yal = sys.argv[idx + 1]

    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
            if not output_file.endswith('.py'):
                output_file += '.py'

    if not os.path.exists(input_file):
        print(f"  ERROR: No se encontró el archivo '{input_file}'")
        sys.exit(1)

    parser_type = "LALR(1)" if use_lalr else "SLR(1)"

    print()
    print("============================================================")
    print(f"  YAPAR — GENERADOR DE ANALIZADORES SINTÁCTICOS {parser_type}")
    print("============================================================")

    t_start = time.time()

    # ---------------------------------------- FASE 0: YALEX (opcional) ----------------------------------------
    lexer_module   = "generated_lexer"
    lexer_function = "gettoken"

    if lexer_yal:
        if not os.path.exists(lexer_yal):
            print(f"  ERROR: No se encontró el archivo lexer '{lexer_yal}'")
            sys.exit(1)
        print()
        print("  [0/5] INVOCANDO YALEX")
        print("  ----------------------------------------")
        lexer_out = os.path.splitext(output_file)[0] + "_lexer.py"
        ret = os.system(f'python yalex.py "{lexer_yal}" -o "{lexer_out}"')
        if ret != 0:
            print(f"  ERROR: YALex falló al procesar '{lexer_yal}'")
            sys.exit(1)
        lexer_module = os.path.splitext(os.path.basename(lexer_out))[0]
        print(f"  Lexer generado: {lexer_out} (módulo: {lexer_module})")

        try:
            from reader import parse_yalex as _parse_yalex
            _spec = _parse_yalex(lexer_yal)
            lexer_function = _spec.entry_name
        except Exception:
            pass

    # ---------------------------------------- FASE 1 ----------------------------------------
    print()
    print("  [1/5] LECTURA DE ESPECIFICACIÓN .YALP")
    print("  ----------------------------------------")
    spec = parse_yapar(input_file)

    print(f"  Archivo:            {input_file}")
    print(f"  Tokens declarados:  {len(spec.tokens)}")
    for t in spec.tokens:
        ignored_mark = " [IGNORED]" if t in spec.ignored else ""
        print(f"    {t}{ignored_mark}")
    print(f"  Símbolo inicial:    {spec.start_symbol}")
    print(f"  Producciones:       {len(spec.productions)}")
    for p in spec.productions:
        print(f"    {p}")

    # ---------------------------------------- FASE 2 ----------------------------------------
    print()
    print("  [2/5] GRAMÁTICA AUMENTADA + FIRST / FOLLOW")
    print("  ----------------------------------------")
    grammar = Grammar(spec)
    grammar.print_summary()

    # ---------------------------------------- FASE 3 ----------------------------------------
    print()
    print("  [3/5] AUTÓMATA LR(0) — COLECCIÓN CANÓNICA + VISUALIZACIÓN")
    print("  ----------------------------------------")
    states, _ = build_canonical_collection(grammar)
    print(f"  Estados generados: {len(states)}")
    for state in states:
        trans_str = ", ".join(f"{s}->{t}" for s, t in sorted(state.transitions.items()))
        print(f"    Estado {state.id:3d}: {len(state.items)} items  |  transiciones: {trans_str or '-'}")

    # Generar visualización visual del autómata LR(0)
    base = os.path.splitext(output_file)[0]
    html_path = base + "_lr0_automaton.html"
    dot_path  = base + "_lr0_automaton.dot"

    try:
        generate_automaton_html(states, grammar, output_file=html_path, parser_type=parser_type)
        print(f"\n  Visualización HTML: {html_path}")
    except Exception as e:
        print(f"\n  ADVERTENCIA: No se pudo generar HTML: {e}")

    try:
        generate_automaton_dot_file(states, grammar, output_file=dot_path)
        print(f"  Visualización DOT:  {dot_path}")
    except Exception as e:
        print(f"  ADVERTENCIA: No se pudo generar DOT: {e}")

    # ---------------------------------------- FASE 4 ----------------------------------------
    print()
    print(f"  [4/5] TABLAS {parser_type} — ACTION / GOTO")
    print("  ----------------------------------------")

    if use_lalr:
        tables = build_lalr_tables(grammar)
        print(f"  Estados LR(1):      {tables.num_lr1_states}")
        print(f"  Estados LALR(1):    {tables.num_lalr_states}")
        print(f"  (fusión: {tables.num_lr1_states - tables.num_lalr_states} estados eliminados)")
    else:
        tables = build_slr_tables(grammar)

    action_entries = sum(len(v) for v in tables.action.values())
    goto_entries   = sum(len(v) for v in tables.goto.values())
    print(f"  Entradas ACTION:    {action_entries}")
    print(f"  Entradas GOTO:      {goto_entries}")

    if tables.conflicts:
        print(f"  CONFLICTOS ({len(tables.conflicts)}):")
        for c in tables.conflicts:
            print(c)
        print(f"  ADVERTENCIA: La gramática no es {parser_type} pura. "
              "Se resolvieron conflictos shift>reduce y menor-índice>reduce-reduce.")
    else:
        print(f"  Sin conflictos — gramática {parser_type} válida.")

    # ---------------------------------------- FASE 5 ----------------------------------------
    print()
    print("  [5/5] GENERACIÓN DE CÓDIGO PYTHON")
    print("  ----------------------------------------")
    out_path = generate_parser(
        grammar=grammar,
        tables=tables,
        lexer_module=lexer_module,
        lexer_function=lexer_function,
        output_file=output_file,
    )
    print(f"  Archivo generado: {out_path}")

    t_end = time.time()

    print()
    print("============================================================")
    print(f"  COMPLETADO EN {t_end - t_start:.3f}s  [{parser_type}]")
    print(f"  Parser:    python {out_path} <archivo_fuente>")
    print(f"  Autómata:  abrir {html_path} en un navegador")
    print("============================================================")
    print()


if __name__ == "__main__":
    main()
