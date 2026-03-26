#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------------------
# run_tests.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Script de pruebas automatizadas para el generador YALex
#
#              Genera el analizador léxico a partir de pico.yal, luego ejecuta todos
#              los archivos de prueba y compara los tokens producidos con los esperados.
#              Incluye 7 archivos que deben tokenizarse correctamente y 6 que deben
#              producir errores léxicos, para un total de 13 casos de prueba.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------- CASOS DE PRUEBA EXITOSOS ----------------------------------------

PASS_TESTS = {
    "tests/hello.pico": [
        "KW_LET", "IDENT", "ASSIGN", "STRING_LIT", "SEMICOLON",
        "KW_EMIT", "STRING_LIT", "SEMICOLON",
        "KW_EMIT", "IDENT", "SEMICOLON"
    ],
    "tests/arithmetic.pico": [
        "KW_LET", "IDENT", "ASSIGN", "INT_LIT", "SEMICOLON",
        "KW_LET", "IDENT", "ASSIGN", "INT_LIT", "SEMICOLON",
        "KW_LET", "IDENT", "ASSIGN", "LPAREN", "IDENT", "PLUS",
        "IDENT", "RPAREN", "TIMES", "INT_LIT", "SEMICOLON",
        "KW_EMIT", "IDENT", "SEMICOLON"
    ],
    "tests/conditional.pico": [
        "KW_LET", "IDENT", "ASSIGN", "INT_LIT", "SEMICOLON",
        "KW_LET", "IDENT", "ASSIGN", "IDENT", "GEQ", "INT_LIT", "SEMICOLON",
        "KW_WHEN", "LPAREN", "IDENT", "RPAREN", "LBRACE",
        "KW_EMIT", "STRING_LIT", "SEMICOLON", "RBRACE",
        "KW_OTHERWISE", "LBRACE",
        "KW_EMIT", "STRING_LIT", "SEMICOLON", "RBRACE"
    ],
    "tests/loop.pico": [
        "KW_LET", "IDENT", "ASSIGN", "INT_LIT", "SEMICOLON",
        "KW_REPEAT", "LBRACE",
        "KW_EMIT", "IDENT", "SEMICOLON",
        "KW_LET", "IDENT", "ASSIGN", "IDENT", "MINUS", "INT_LIT", "SEMICOLON",
        "RBRACE", "KW_UNTIL", "LPAREN", "IDENT", "EQ", "INT_LIT", "RPAREN", "SEMICOLON"
    ],
    "tests/macro.pico": [
        "KW_MACRO", "IDENT", "LPAREN", "IDENT", "RPAREN", "LBRACE",
        "IDENT", "TIMES", "INT_LIT", "RBRACE",
        "KW_LET", "IDENT", "ASSIGN", "INT_LIT", "SEMICOLON",
        "KW_EMIT", "IDENT", "LPAREN", "IDENT", "RPAREN", "SEMICOLON"
    ],
    "tests/floats_and_logic.pico": [
        "KW_LET", "IDENT", "ASSIGN", "FLOAT_LIT", "SEMICOLON",
        "KW_LET", "IDENT", "ASSIGN", "FLOAT_LIT", "SEMICOLON",
        "KW_LET", "IDENT", "ASSIGN", "IDENT", "TIMES", "IDENT", "TIMES", "IDENT", "SEMICOLON",
        "KW_LET", "IDENT", "ASSIGN", "IDENT", "GT", "FLOAT_LIT", "AND",
        "IDENT", "NEQ", "FLOAT_LIT", "SEMICOLON",
        "KW_EMIT", "IDENT", "SEMICOLON"
    ],
    "tests/comments_only.pico": [],
}


# ---------------------------------------- CASOS DE PRUEBA CON ERROR ----------------------------------------

FAIL_TESTS = {
    "tests/bad_string.pico":     "Unrecognized character",
    "tests/invalid_char.pico":   "'@'",
    "tests/bad_number.pico":     "'.'",
    "tests/hash_comment.pico":   "'#'",
    "tests/bad_assign.pico":     "'='",
    "tests/unclosed_block.pico": "'$'",
}


# ---------------------------------------- EJECUCIÓN DE PRUEBAS ----------------------------------------

def main():
    # Generar el lexer
    print("============================================================")
    print("  PRUEBAS AUTOMATIZADAS — YALEX GENERATOR")
    print("============================================================")
    print()
    print("  Generando lexer desde pico.yal...")
    result = subprocess.run(
        [sys.executable, "yalex.py", "pico.yal", "-o", "generated_lexer.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR en la generación:\n{result.stderr}")
        sys.exit(1)
    print("  Lexer generado correctamente.")
    print()

    passed = 0
    failed = 0
    total = 0

    # Ejecutar tests exitosos
    print("  ----------------------------------------")
    print("  TESTS QUE DEBEN PASAR")
    print("  ----------------------------------------")
    for test_file, expected_tokens in PASS_TESTS.items():
        total += 1
        result = subprocess.run(
            [sys.executable, "generated_lexer.py", test_file],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  FAIL  {test_file}")
            print(f"        Se esperaba éxito, obtuvo: {result.stdout.strip()}")
            failed += 1
            continue

        # Extraer nombres de token de la salida (ignorar líneas decorativas)
        lines = result.stdout.strip().split('\n')
        actual_tokens = []
        for line in lines:
            line = line.strip()
            if (line.startswith("---") or line.startswith("===") or
                not line or line.startswith("Total") or
                line.startswith("TOKENS RECONOCIDOS")):
                continue
            token_name = line.split('(')[0].strip()
            actual_tokens.append(token_name)

        if actual_tokens == expected_tokens:
            print(f"  PASS  {test_file:40s} ({len(actual_tokens)} tokens)")
            passed += 1
        else:
            print(f"  FAIL  {test_file}")
            print(f"        Esperado: {expected_tokens}")
            print(f"        Obtenido: {actual_tokens}")
            failed += 1

    print()

    # Ejecutar tests con error
    print("  ----------------------------------------")
    print("  TESTS QUE DEBEN FALLAR")
    print("  ----------------------------------------")
    for test_file, expected_error in FAIL_TESTS.items():
        total += 1
        if not os.path.exists(test_file):
            print(f"  SKIP  {test_file} — archivo no encontrado")
            continue

        result = subprocess.run(
            [sys.executable, "generated_lexer.py", test_file],
            capture_output=True, text=True
        )
        output = result.stdout.strip()
        if "LEXICAL ERROR" in output and expected_error in output:
            print(f"  PASS  {test_file:40s} (error: {expected_error})")
            passed += 1
        else:
            print(f"  FAIL  {test_file}")
            print(f"        Se esperaba error con: {expected_error}")
            print(f"        Salida: {output}")
            failed += 1

    # Resumen
    print()
    print("============================================================")
    status = "TODOS LOS TESTS PASARON" if failed == 0 else f"{failed} TEST(S) FALLARON"
    print(f"  {status}: {passed}/{total}")
    print("============================================================")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
