# --------------------------------------------------------------------------------------------------------
# yapar_reader.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Lector y preprocesador de archivos YAPar (.yalp)
#
#              Lee una especificación gramatical escrita en lenguaje YAPar y la descompone
#              en dos secciones: declaración de tokens (%token / IGNORE) y producciones
#              de la gramática libre de contexto. Los comentarios /* ... */ son eliminados.
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

import re
import sys


# ---------------------------------------- ESTRUCTURAS DE DATOS ----------------------------------------

class YAParProduction:
    """Una producción de la gramática: LHS → RHS (lista de símbolos)."""
    def __init__(self, lhs: str, rhs: list[str], index: int):
        self.lhs = lhs
        self.rhs = rhs          # lista de strings; [] representa ε
        self.index = index

    def __repr__(self):
        rhs_str = ' '.join(self.rhs) if self.rhs else 'ε'
        return f"({self.index}) {self.lhs} -> {rhs_str}"


class YAParSpec:
    """Contenedor completo de la especificación de un archivo .yalp"""
    def __init__(self):
        self.tokens: list[str] = []          # tokens declarados con %token
        self.ignored: list[str] = []         # tokens a ignorar (IGNORE)
        self.productions: list[YAParProduction] = []
        self.start_symbol: str = ""          # primera producción = símbolo inicial


# ---------------------------------------- ELIMINACIÓN DE COMENTARIOS ----------------------------------------

def remove_comments(text: str) -> str:
    """Elimina comentarios /* ... */ del texto fuente."""
    result = []
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i] == '/' and text[i + 1] == '*':
            i += 2
            while i < len(text):
                if i + 1 < len(text) and text[i] == '*' and text[i + 1] == '/':
                    i += 2
                    break
                i += 1
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)


# ---------------------------------------- PARSER PRINCIPAL ----------------------------------------

def parse_yapar(filename: str) -> YAParSpec:
    """
    Lee un archivo .yalp y retorna un YAParSpec con tokens y producciones.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        raw = f.read()

    text = remove_comments(raw)
    spec = YAParSpec()
    prod_index = 0

    # Dividir por %%
    if '%%' not in text:
        raise ValueError("El archivo .yalp no contiene el separador %%")

    parts = text.split('%%', 1)
    token_section = parts[0]
    production_section = parts[1]

    # ---- Sección de tokens ----
    for line in token_section.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith('%token'):
            # Puede haber múltiples tokens en una línea
            rest = line[len('%token'):].strip()
            for tok in rest.split():
                tok = tok.strip()
                if tok:
                    spec.tokens.append(tok)

        elif line.startswith('IGNORE'):
            rest = line[len('IGNORE'):].strip()
            for tok in rest.split():
                tok = tok.strip()
                if tok:
                    spec.ignored.append(tok)

    # ---- Sección de producciones ----
    # Normalizar: combinar líneas en bloques por ";"
    # Cada producción termina con ;
    raw_prods = production_section.strip()

    # Tokenizar bloques separados por ;
    blocks = []
    current = []
    for line in raw_prods.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        current.append(stripped)
        if stripped.endswith(';'):
            blocks.append(' '.join(current))
            current = []
    if current:
        blocks.append(' '.join(current))

    for block in blocks:
        block = block.rstrip(';').strip()
        if not block:
            continue

        # Separar LHS del resto: "lhs : alternativas"
        if ':' not in block:
            continue

        colon_idx = block.index(':')
        lhs = block[:colon_idx].strip()
        rhs_part = block[colon_idx + 1:].strip()

        if not lhs:
            continue

        if spec.start_symbol == "":
            spec.start_symbol = lhs

        # Separar alternativas por |
        alternatives = rhs_part.split('|')
        for alt in alternatives:
            symbols_raw = alt.strip()
            if not symbols_raw:
                # producción vacía → ε
                rhs = []
            else:
                rhs = symbols_raw.split()

            spec.productions.append(YAParProduction(lhs, rhs, prod_index))
            prod_index += 1

    return spec


# ---------------------------------------- EJECUCIÓN STANDALONE ----------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python yapar_reader.py <archivo.yalp>")
        sys.exit(1)

    spec = parse_yapar(sys.argv[1])

    print("------------------------------------------------------------")
    print("  RESULTADO DEL PREPROCESAMIENTO")
    print("------------------------------------------------------------")
    print(f"  Tokens declarados ({len(spec.tokens)}): {spec.tokens}")
    print(f"  Tokens ignorados  ({len(spec.ignored)}): {spec.ignored}")
    print(f"  Símbolo inicial:   {spec.start_symbol}")
    print(f"  Producciones ({len(spec.productions)}):")
    for p in spec.productions:
        print(f"    {p}")
    print("------------------------------------------------------------")
