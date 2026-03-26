# --------------------------------------------------------------------------------------------------------
# code_generator.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Generador de código Python a partir del AFD minimizado
#
#              Serializa el AFD como una tabla de transiciones estática embebida en un
#              archivo Python autónomo. El archivo generado contiene toda la lógica de
#              simulación del analizador léxico: lectura de caracteres, avance de estados,
#              longest match con backtracking, reporte de posición (línea/columna) y
#              manejo de errores léxicos. No requiere dependencias externas para ejecutar.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from dfa_builder import DFA, EOF_MARKER


# ---------------------------------------- GENERACIÓN DEL LEXER ----------------------------------------

def generate_lexer(dfa: DFA, rules: list, entry_name: str,
                   header: str = "", trailer: str = "",
                   output_file: str = "generated_lexer.py"):
    """
    Genera un archivo Python completo con el analizador léxico.
    Recibe el AFD minimizado, la lista de reglas con sus acciones,
    el nombre del entry point, y opcionalmente header/trailer del .yal.
    """

    # Construir tabla de transiciones serializable
    transition_table = {}
    for state in dfa.states:
        trans = {}
        for sym, target in state.transitions.items():
            trans[sym] = target
        transition_table[state.id] = trans

    # Mapear estados de aceptación a sus reglas
    accept_info = {}
    for state in dfa.states:
        if state.is_accept:
            accept_info[state.id] = state.accept_rule

    # Recopilar acciones de cada regla
    actions = []
    for i, rule in enumerate(rules):
        action = rule.action.strip() if rule.action else ""
        pattern = rule.pattern.strip()
        actions.append((i, pattern, action))

    # ---- Inicio del código generado ----

    code = f'''#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------------------
# Analizador Léxico generado automáticamente por YALex
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# ARCHIVO GENERADO — NO EDITAR MANUALMENTE
# Fuente: especificación .yal procesada por yalex.py
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

import sys

# ---------------------------------------- HEADER DEL ARCHIVO .YAL ----------------------------------------
{header}

# ---------------------------------------- TABLA DE TRANSICIONES DEL AFD ----------------------------------------

_TRANSITION_TABLE = {repr(transition_table)}

_ACCEPT_STATES = {repr(accept_info)}

_START_STATE = {dfa.start_id}

_EOF_MARKER = {EOF_MARKER}

_RULE_PATTERNS = {repr([(i, p) for i, p, a in actions])}


# ---------------------------------------- CLASES DEL MOTOR LÉXICO ----------------------------------------

class LexicalError(Exception):
    """Excepción para errores léxicos con información de posición."""
    def __init__(self, message, line, col, char):
        self.line = line
        self.col = col
        self.char = char
        super().__init__(message)


class Token:
    """Representa un token reconocido con su tipo, lexema y posición."""
    def __init__(self, kind: str, value: str = "", line: int = 0, col: int = 0):
        self.kind = kind
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        if self.value and self.value != self.kind:
            return f"{{self.kind}}({{self.value!r}})"
        return f"{{self.kind}}"


# ---------------------------------------- DESPACHADOR DE ACCIONES ----------------------------------------

def _execute_action(rule_index: int, lxm: str, lexbuf_callback) -> str | None:
    """Ejecuta la acción de una regla. Retorna nombre del token o None para skip."""
'''

    # Generar el despachador de acciones
    for i, pattern, action in actions:
        if not action:
            code += f"    if rule_index == {i}:  # {pattern}\n"
            code += f"        return None\n\n"
            continue

        action_clean = action.strip()

        if 'return lexbuf' in action_clean:
            code += f"    if rule_index == {i}:  # {pattern} — skip\n"
            code += f"        return None\n\n"
        elif action_clean.startswith('return '):
            rest = action_clean[7:].strip().rstrip(';').strip()
            if '(' in rest and ')' in rest:
                token_name = rest.split('(')[0].strip()
                code += f"    if rule_index == {i}:  # {pattern}\n"
                code += f"        return \"{token_name}\"\n\n"
            else:
                code += f"    if rule_index == {i}:  # {pattern}\n"
                code += f"        return \"{rest}\"\n\n"
        elif 'raise' in action_clean:
            code += f"    if rule_index == {i}:  # {pattern} — EOF\n"
            code += f"        return \"__EOF__\"\n\n"
        else:
            code += f"    if rule_index == {i}:  # {pattern}\n"
            code += f"        return \"UNKNOWN_RULE_{i}\"\n\n"

    code += f"    return None\n\n"

    # ---- Motor de simulación del AFD ----

    code += f'''
# ---------------------------------------- MOTOR DE ANÁLISIS LÉXICO ----------------------------------------

def {entry_name}(text: str) -> list[Token]:
    """
    Simula el AFD sobre el texto de entrada. Aplica la regla de longest match:
    siempre consume el prefijo más largo que concuerda con algún patrón.
    """
    tokens = []
    pos = 0
    line = 1
    col = 1
    length = len(text)

    while pos < length:
        # Iniciar simulación del AFD desde el estado inicial
        current_state = _START_STATE
        last_accept_pos = -1
        last_accept_rule = -1
        scan_pos = pos
        scan_line = line
        scan_col = col

        # Avanzar mientras existan transiciones válidas
        while scan_pos < length:
            ch = ord(text[scan_pos])
            trans = _TRANSITION_TABLE.get(current_state, {{}})
            if ch in trans:
                current_state = trans[ch]
                scan_pos += 1
                if ch == ord('\\n'):
                    scan_line += 1
                    scan_col = 1
                else:
                    scan_col += 1
                # Recordar la última posición de aceptación
                if current_state in _ACCEPT_STATES:
                    last_accept_pos = scan_pos
                    last_accept_rule = _ACCEPT_STATES[current_state]
            else:
                break

        # Verificar aceptación al final del input
        if scan_pos == length and current_state in _ACCEPT_STATES:
            if scan_pos > last_accept_pos:
                last_accept_pos = scan_pos
                last_accept_rule = _ACCEPT_STATES[current_state]

        if last_accept_pos > pos:
            lexeme = text[pos:last_accept_pos]
            token_name = _execute_action(last_accept_rule, lexeme, None)
            if token_name is not None:
                if token_name == "__EOF__":
                    break
                tokens.append(Token(token_name, lexeme, line, col))
            # Actualizar posición
            for ch in lexeme:
                if ch == '\\n':
                    line += 1
                    col = 1
                else:
                    col += 1
            pos = last_accept_pos
        else:
            bad_char = text[pos]
            raise LexicalError(
                f"LEXICAL ERROR at line {{line}}: Unrecognized character {{bad_char!r}}",
                line, col, bad_char
            )

    return tokens


# ---------------------------------------- PROGRAMA PRINCIPAL ----------------------------------------

def main():
    if len(sys.argv) < 2:
        print("------------------------------------------------------------")
        print("  USO: python {{sys.argv[0]}} <archivo_fuente>")
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
        tokens = {entry_name}(source)
        print("------------------------------------------------------------")
        print(f"  TOKENS RECONOCIDOS — {{filename}}")
        print("------------------------------------------------------------")
        for tok in tokens:
            print(f"  {{tok}}")
        print("------------------------------------------------------------")
        print(f"  Total: {{len(tokens)}} tokens")
        print("------------------------------------------------------------")
    except LexicalError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()

# ---------------------------------------- TRAILER DEL ARCHIVO .YAL ----------------------------------------
{trailer}
'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code)

    return output_file
