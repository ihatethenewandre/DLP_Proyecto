# --------------------------------------------------------------------------------------------------------
# parser_codegen.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Generador de código Python para el analizador sintáctico SLR(1)
#
#              Serializa las tablas ACTION y GOTO como diccionarios Python estáticos
#              y emite un archivo .py autónomo que implementa el loop de parseo SLR.
#              El parser generado importa el lexer producido por YALex.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from grammar import Grammar
from slr_table import SLRTables, SHIFT, REDUCE, ACCEPT


# ---------------------------------------- GENERACIÓN ----------------------------------------

def generate_parser(
    grammar: Grammar,
    tables: SLRTables,
    lexer_module: str,
    lexer_function: str,
    output_file: str = "generated_parser.py",
) -> str:
    """
    Genera un parser SLR(1) en Python a partir de las tablas y la gramática.

    grammar       — gramática aumentada con FIRST/FOLLOW
    tables        — tablas ACTION y GOTO
    lexer_module  — nombre del módulo del lexer generado (sin .py)
    lexer_function — nombre de la función del lexer (entry_name)
    output_file   — ruta del archivo a generar
    """

    # Serializar producciones como (lhs, rhs_len, lhs_display)
    prods_repr = []
    for p in grammar.productions:
        prods_repr.append((p.lhs, len(p.rhs), ' '.join(p.rhs) if p.rhs else 'ε'))

    ignored_repr = repr(set(grammar.ignored))

    code = f'''#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------------------
# Analizador Sintáctico generado automáticamente por YAPar
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# ARCHIVO GENERADO — NO EDITAR MANUALMENTE
# Fuente: especificación .yalp procesada por yapar.py
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

import sys
from {lexer_module} import {lexer_function}, Token, LexicalError


# ---------------------------------------- TABLAS SLR ----------------------------------------

# Cada entrada: ('shift', next_state) | ('reduce', prod_index) | ('accept',)
_ACTION = {repr(tables.action)}

# GOTO[estado][no_terminal] → siguiente estado
_GOTO = {repr(tables.goto)}

# Producciones: (lhs, len_rhs, descripcion_legible)
_PRODUCTIONS = {repr(prods_repr)}

_START_STATE = 0

_IGNORED_TOKENS = {ignored_repr}


# ---------------------------------------- EXCEPCIÓN DE PARSEO ----------------------------------------

class ParseError(Exception):
    """Error sintáctico con información de posición."""
    def __init__(self, message: str, token=None):
        self.token = token
        super().__init__(message)


# ---------------------------------------- MOTOR SLR ----------------------------------------

def parse(text: str) -> bool:
    """
    Analiza el texto usando el autómata SLR generado.
    Retorna True si la entrada es sintácticamente válida.
    Lanza ParseError en caso de error sintáctico.
    """
    # Obtener tokens del lexer y filtrar los ignorados
    try:
        raw_tokens = {lexer_function}(text)
    except LexicalError as e:
        raise ParseError(str(e))

    tokens = [t for t in raw_tokens if t.kind not in _IGNORED_TOKENS]
    tokens.append(Token('$', '$', -1, -1))  # marcador de fin de entrada

    stack = [_START_STATE]
    tok_pos = 0

    while True:
        state = stack[-1]
        token = tokens[tok_pos]

        action = _ACTION.get(state, {{}}).get(token.kind)

        if action is None:
            expected = sorted(_ACTION.get(state, {{}}).keys())
            raise ParseError(
                f"Error sintáctico: token inesperado {{token.kind!r}} "
                f"(línea {{token.line}}, col {{token.col}}). "
                f"Se esperaba uno de: {{expected}}",
                token=token
            )

        kind = action[0]

        if kind == 'shift':
            stack.append(action[1])
            tok_pos += 1

        elif kind == 'reduce':
            prod_idx = action[1]
            lhs, rhs_len, _ = _PRODUCTIONS[prod_idx]
            for _ in range(rhs_len):
                stack.pop()
            top_state = stack[-1]
            next_state = _GOTO.get(top_state, {{}}).get(lhs)
            if next_state is None:
                raise ParseError(
                    f"Error interno: GOTO[{{top_state}}][{{lhs!r}}] no definido.",
                    token=token
                )
            stack.append(next_state)

        elif kind == 'accept':
            return True

        else:
            raise ParseError(f"Acción desconocida: {{action}}", token=token)


# ---------------------------------------- PROGRAMA PRINCIPAL ----------------------------------------

def main():
    if len(sys.argv) < 2:
        print("------------------------------------------------------------")
        print(f"  USO: python {{sys.argv[0]}} <archivo_fuente>")
        print("------------------------------------------------------------")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"  ERROR: No se encontró el archivo '{{filename}}'")
        sys.exit(1)

    try:
        result = parse(source)
        print("------------------------------------------------------------")
        print(f"  RESULTADO DE PARSEO — {{filename}}")
        print("------------------------------------------------------------")
        if result:
            print("  La entrada es ACEPTADA por la gramática.")
        print("------------------------------------------------------------")
    except (ParseError, LexicalError) as e:
        print("------------------------------------------------------------")
        print(f"  RESULTADO DE PARSEO — {{filename}}")
        print("------------------------------------------------------------")
        print(f"  La entrada es RECHAZADA.")
        print("  " + str(e))
        print("------------------------------------------------------------")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code)

    return output_file
