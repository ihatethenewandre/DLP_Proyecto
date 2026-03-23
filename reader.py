# --------------------------------------------------------------------------------------------------------
# reader.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Lector y preprocesador de archivos YALex (.yal)
#
#              Este módulo constituye el punto de entrada del sistema. Lee un archivo
#              de especificación escrito en lenguaje YALex y lo descompone en sus cuatro
#              secciones fundamentales: header (opcional), definiciones regulares (let),
#              reglas de tokenización (rule) y trailer (opcional). Además, se encarga de
#              eliminar los comentarios delimitados por (* y *) con soporte de anidamiento.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

import re
import sys


# ---------------------------------------- ESTRUCTURAS DE DATOS ----------------------------------------

class YALexDefinition:
    """Almacena una definición regular: let <nombre> = <patrón>"""
    def __init__(self, name: str, pattern: str):
        self.name = name
        self.pattern = pattern

    def __repr__(self):
        return f"Def({self.name} = {self.pattern})"


class YALexRule:
    """Almacena una regla de tokenización: <patrón> {{ <acción> }}"""
    def __init__(self, pattern: str, action: str):
        self.pattern = pattern
        self.action = action

    def __repr__(self):
        return f"Rule({self.pattern!r} -> {self.action!r})"


class YALexSpec:
    """Contenedor completo de la especificación de un archivo .yal"""
    def __init__(self):
        self.header: str = ""
        self.trailer: str = ""
        self.definitions: list[YALexDefinition] = []
        self.entry_name: str = "tokens"
        self.rules: list[YALexRule] = []


# ---------------------------------------- ELIMINACIÓN DE COMENTARIOS ----------------------------------------

def remove_comments(text: str) -> str:
    """
    Recorre el texto carácter por carácter eliminando bloques (* ... *).
    Respeta comillas simples y dobles para no borrar contenido dentro de literales.
    Soporta comentarios anidados controlando la profundidad.
    """
    result = []
    i = 0
    in_single_quote = False
    in_double_quote = False

    while i < len(text):

        # Alternar estado de comilla simple
        if text[i] == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            result.append(text[i])
            i += 1
            continue

        # Alternar estado de comilla doble
        if text[i] == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            result.append(text[i])
            i += 1
            continue

        # Secuencias de escape dentro de comillas
        if (in_single_quote or in_double_quote) and text[i] == '\\':
            result.append(text[i])
            i += 1
            if i < len(text):
                result.append(text[i])
                i += 1
            continue

        # Inicio de comentario (* ... *)
        if not in_single_quote and not in_double_quote:
            if i + 1 < len(text) and text[i] == '(' and text[i + 1] == '*':
                depth = 1
                i += 2
                while i < len(text) and depth > 0:
                    if i + 1 < len(text) and text[i] == '(' and text[i + 1] == '*':
                        depth += 1
                        i += 2
                    elif i + 1 < len(text) and text[i] == '*' and text[i + 1] == ')':
                        depth -= 1
                        i += 2
                    else:
                        i += 1
                continue

        result.append(text[i])
        i += 1

    return ''.join(result)


# ---------------------------------------- UTILIDADES DE PARSEO ----------------------------------------

def extract_braced_block(text: str, start: int) -> tuple[str, int]:
    """Extrae un bloque { ... } balanceado y retorna (contenido, posición_final)."""
    assert text[start] == '{', f"Se esperaba '{{' en posición {start}"
    depth = 1
    i = start + 1
    while i < len(text) and depth > 0:
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
        i += 1
    return text[start + 1:i - 1].strip(), i


# ---------------------------------------- PARSER PRINCIPAL ----------------------------------------

def parse_yalex(filename: str) -> YALexSpec:
    """
    Lee un archivo .yal completo y retorna un objeto YALexSpec con todas
    las secciones separadas: header, definiciones, reglas y trailer.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        raw = f.read()

    text = remove_comments(raw)
    spec = YALexSpec()

    pos = 0
    length = len(text)

    def skip_ws():
        nonlocal pos
        while pos < length and text[pos] in ' \t\n\r':
            pos += 1

    skip_ws()

    # Extraer header opcional
    if pos < length and text[pos] == '{':
        spec.header, pos = extract_braced_block(text, pos)
        skip_ws()

    # Extraer definiciones: let ident = regexp
    while pos < length:
        skip_ws()
        if pos >= length:
            break

        rest = text[pos:]
        if rest.startswith('rule ') or rest.startswith('rule\t') or rest.startswith('rule\n'):
            break

        m = re.match(r'let\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*', rest)
        if m:
            name = m.group(1)
            pos += m.end()
            # Acumular el patrón hasta encontrar otra directiva let/rule
            pattern_chars = []
            while pos < length:
                if text[pos] == '\n':
                    save = pos
                    pos += 1
                    while pos < length and text[pos] in ' \t':
                        pos += 1
                    if pos < length:
                        ahead = text[pos:]
                        if (ahead.startswith('let ') or ahead.startswith('let\t') or
                            ahead.startswith('rule ') or ahead.startswith('rule\t') or
                            ahead.startswith('rule\n')):
                            pos = save + 1
                            break
                    pattern_chars.append('\n')
                    continue
                pattern_chars.append(text[pos])
                pos += 1

            pattern = ''.join(pattern_chars).strip()
            spec.definitions.append(YALexDefinition(name, pattern))
        else:
            if pos < length:
                pos += 1

    skip_ws()

    # Extraer nombre del entry point: rule <nombre> =
    rest = text[pos:]
    m = re.match(r'rule\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\[.*?\])?\s*=\s*', rest)
    if m:
        spec.entry_name = m.group(1)
        pos += m.end()
    elif rest.startswith('rule'):
        m2 = re.match(r'rule\s+(\w+)\s*=', rest)
        if m2:
            spec.entry_name = m2.group(1)
            pos += m2.end()

    skip_ws()

    # Extraer reglas: patrón { acción } separadas por |
    while pos < length:
        skip_ws()
        if pos >= length:
            break

        if text[pos] == '{':
            pass

        # Consumir separador de alternación
        if text[pos] == '|':
            pos += 1
            skip_ws()

        # Leer el patrón regex hasta encontrar { de acción
        pattern_chars = []
        bracket_depth = 0
        paren_depth = 0

        while pos < length:
            ch = text[pos]

            if ch == '[':
                bracket_depth += 1
                pattern_chars.append(ch)
                pos += 1
            elif ch == ']' and bracket_depth > 0:
                bracket_depth -= 1
                pattern_chars.append(ch)
                pos += 1
            elif ch == '(' and bracket_depth == 0:
                paren_depth += 1
                pattern_chars.append(ch)
                pos += 1
            elif ch == ')' and bracket_depth == 0:
                paren_depth -= 1
                pattern_chars.append(ch)
                pos += 1
            elif ch == "'" and bracket_depth == 0:
                pattern_chars.append(ch)
                pos += 1
                while pos < length and text[pos] != "'":
                    pattern_chars.append(text[pos])
                    pos += 1
                if pos < length:
                    pattern_chars.append(text[pos])
                    pos += 1
            elif ch == '"' and bracket_depth == 0:
                pattern_chars.append(ch)
                pos += 1
                while pos < length and text[pos] != '"':
                    if text[pos] == '\\':
                        pattern_chars.append(text[pos])
                        pos += 1
                        if pos < length:
                            pattern_chars.append(text[pos])
                            pos += 1
                    else:
                        pattern_chars.append(text[pos])
                        pos += 1
                if pos < length:
                    pattern_chars.append(text[pos])
                    pos += 1
            elif ch == '{' and bracket_depth == 0 and paren_depth == 0:
                break
            else:
                pattern_chars.append(ch)
                pos += 1

        pattern = ''.join(pattern_chars).strip()

        if not pattern:
            if pos < length and text[pos] == '{':
                content, end_pos = extract_braced_block(text, pos)
                remaining = text[end_pos:].strip()
                if not remaining or not any(c in remaining for c in '|'):
                    spec.trailer = content
                    pos = end_pos
                    break
            break

        # Leer la acción { ... }
        skip_ws()
        action = ""
        if pos < length and text[pos] == '{':
            action, pos = extract_braced_block(text, pos)

        if pattern:
            spec.rules.append(YALexRule(pattern, action))

        skip_ws()

        # Verificar si viene trailer
        if pos < length and text[pos] != '|':
            skip_ws()
            if pos < length and text[pos] == '{':
                content, end_pos = extract_braced_block(text, pos)
                spec.trailer = content
                pos = end_pos
            break

    return spec


# ---------------------------------------- EJECUCIÓN STANDALONE ----------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python reader.py <archivo.yal>")
        sys.exit(1)

    spec = parse_yalex(sys.argv[1])

    print("------------------------------------------------------------")
    print("  RESULTADO DEL PREPROCESAMIENTO")
    print("------------------------------------------------------------")
    print(f"  Header:       {'Presente' if spec.header else 'Vacío'}")
    print(f"  Definiciones: {len(spec.definitions)}")
    for d in spec.definitions:
        print(f"    let {d.name} = {d.pattern}")
    print(f"  Entry point:  {spec.entry_name}")
    print(f"  Reglas:       {len(spec.rules)}")
    for r in spec.rules:
        print(f"    {r}")
    print(f"  Trailer:      {'Presente' if spec.trailer else 'Vacío'}")
    print("------------------------------------------------------------")
