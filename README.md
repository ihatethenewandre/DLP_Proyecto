# YALex + YAPar — Generadores de Analizadores Léxicos y Sintácticos
## Proyecto I & II · Diseño de Lenguajes de Programación

**Universidad del Valle de Guatemala**  
**CC3071 — Diseño de Lenguajes de Programación**

Genser Andree Catalán Espina – 23401  
Roberto Samuel Nájera Marroquín – 23781  
André Emilio Pivaral López – 23574

---

## Descripción

Este proyecto implementa un ecosistema completo de generación de analizadores para lenguajes formales:

- **YALex** — Generador de analizadores léxicos: convierte una especificación `.yal` en un lexer Python autónomo mediante construcción directa de AFD (método followpos) con minimización Hopcroft.
- **YAPar** — Generador de analizadores sintácticos: convierte una especificación `.yalp` en un parser Python autónomo, soportando **SLR(1)** y **LALR(1)**.

Ambos generadores producen código Python sin dependencias externas, listo para ejecutarse sobre cualquier archivo de entrada.

---

## Arquitectura General

```
  Especificación .yal   →   yalex.py   →   Lexer .py (generado)
                                                    │
  Especificación .yalp  →   yapar.py  ─────────────┴───→  Parser .py (generado)
                                      │
                                      └──→  lr0_automaton.html  (visual)
                                      └──→  lr0_automaton.dot   (Graphviz)
```

---

## YALex — Generador de Analizadores Léxicos

### Pipeline (4 fases)

```
  ┌────────────────┐     ┌────────────────┐     ┌────────────────────────────┐     ┌────────────────┐
  │  1. Lector y   │     │  2. Parser de  │     │  3. AFD directo (followpos) │     │  4. Generador  │
  │ Preprocesador  │  →  │      Regex     │  →  │  + clases de símbolo + Hop  │  →  │     Código     │
  └────────────────┘     └────────────────┘     └────────────────────────────┘     └────────────────┘
      reader.py           regex_parser.py              dfa_builder.py              code_generator.py
```

| Módulo | Responsabilidad |
|--------|-----------------|
| `reader.py` | Lee `.yal`, elimina comentarios `(* … *)`, extrae secciones |
| `regex_parser.py` | Parser recursivo descendente → AST de regex con precedencia completa |
| `dfa_builder.py` | AFD directo (followpos), clases de símbolo, minimización Hopcroft |
| `code_generator.py` | Emite tabla de transición + motor longest-match como `.py` autónomo |

### Algoritmos

| Algoritmo | Módulo |
|-----------|--------|
| Eliminación de comentarios anidados `(* … *)` | `reader.py` |
| Parsing de regex con precedencia `#` > `* + ?` > concat > `\|` | `regex_parser.py` |
| AFD directo por followpos (Dragon Book §3.9.5) | `dfa_builder.py` |
| Clases de símbolo (byte-equivalence) | `dfa_builder.py` |
| Minimización de Hopcroft | `dfa_builder.py` |
| Longest match con backtracking | generado |

### Uso

```bash
# Paso 1: generar el lexer
python yalex.py <archivo.yal> -o <lexer.py>

# Paso 2: ejecutar el lexer sobre una entrada
python <lexer.py> <archivo_fuente>
```

---

## YAPar — Generador de Analizadores Sintácticos

### Pipeline (5 fases + fase 0 opcional)

```
   [0] YALex (opcional, -l)
         │
   [1] Lectura .yalp   →   YAParSpec
         │
   [2] Gramática aumentada + FIRST / FOLLOW
         │
   [3] Autómata LR(0)  ─────────────────────→  lr0_automaton.html  (visual)
         │                                  →  lr0_automaton.dot   (Graphviz)
   [4] Tablas SLR(1)  o  LALR(1)
         │
   [5] Generación de código Python  →  parser.py (autónomo)
```

| Módulo | Responsabilidad |
|--------|-----------------|
| `yapar_reader.py` | Lee `.yalp`, elimina `/* … */`, extrae tokens y producciones |
| `grammar.py` | Gramática aumentada (S' → start), FIRST, FOLLOW |
| `lr_automaton.py` | Ítems LR(0), clausura, GOTO, colección canónica |
| `lr1_automaton.py` | Ítems LR(1), clausura LR(1), GOTO LR(1), colección canónica LR(1) |
| `slr_table.py` | Tablas ACTION/GOTO SLR(1) usando FOLLOW |
| `lalr_table.py` | Tablas ACTION/GOTO LALR(1) por fusión de estados LR(1) |
| `automaton_visualizer.py` | Genera `.html` interactivo y `.dot` del autómata LR(0) |
| `parser_codegen.py` | Emite el motor SLR/LALR como `.py` autónomo |
| `yapar.py` | Orquestador del pipeline completo |

### SLR(1) vs LALR(1)

| Característica | SLR(1) | LALR(1) |
|----------------|--------|---------|
| Lookaheads | FOLLOW(A) | Lookaheads exactos LR(1) |
| Potencia | Menor | Mayor (acepta más gramáticas) |
| Número de estados | N (LR(0)) | N (igual que LR(0)) |
| Estados intermedios | — | 2N–3N (LR(1), luego fusionados) |
| Conflictos potenciales | Más | Menos |

LALR(1) es más preciso porque usa lookaheads derivados directamente de los ítems LR(1), que son un subconjunto exacto de `FOLLOW`. Esto permite resolver correctamente gramáticas que SLR(1) rechaza por falsos conflictos.

### Uso

```bash
# SLR(1) — modo por defecto
python yapar.py <archivo.yalp> -l <lexer.yal> -o <parser.py>

# LALR(1) — agregar el flag --lalr
python yapar.py <archivo.yalp> -l <lexer.yal> -o <parser.py> --lalr

# Ejecutar el parser generado
python <parser.py> <archivo_fuente>

# Ver el autómata LR(0) visualmente
# Abrir en el navegador: <parser>_lr0_automaton.html
# O usar Graphviz:       dot -Tsvg <parser>_lr0_automaton.dot -o automaton.svg
```

### Salidas generadas

Para `python yapar.py grammar.yalp -l lexer.yal -o myparser.py`:

| Archivo | Descripción |
|---------|-------------|
| `myparser.py` | Parser SLR(1) autónomo |
| `myparser_lexer.py` | Lexer generado por YALex |
| `myparser_lr0_automaton.html` | **Autómata LR(0) visual** (abrir en navegador) |
| `myparser_lr0_automaton.dot` | Autómata en formato Graphviz |

El HTML incluye:
- Panel de estadísticas (estados, ítems, transiciones, terminales, no-terminales)
- **Diagrama interactivo** renderizado con Viz.js
- Tabla de ítems LR(0) por estado con transiciones
- Código DOT colapsable para uso offline

### Formato .yalp

```
/* comentarios con /* ... */ */
%token TOKEN_A TOKEN_B
%token WS
IGNORE WS

%%

regla_inicio :
    regla_inicio TOKEN_A produccion_b
  | produccion_b
;

produccion_b :
    TOKEN_B
;
```

---

## Estructura del repositorio

```
DLP_Proyecto/
├── README.md
│
├── — YALex —
├── yalex.py                  # Orquestador YALex
├── reader.py                 # Módulo 1: lector .yal
├── regex_parser.py           # Módulo 2: parser de regex
├── dfa_builder.py            # Módulo 3: AFD directo + Hopcroft
├── code_generator.py         # Módulo 4: generador de código léxico
│
├── — YAPar —
├── yapar.py                  # Orquestador YAPar (SLR + LALR + visual)
├── yapar_reader.py           # Lector de archivos .yalp
├── grammar.py                # Gramática aumentada + FIRST/FOLLOW
├── lr_automaton.py           # Autómata LR(0): closure, goto, colección canónica
├── lr1_automaton.py          # Autómata LR(1): closure LR(1), para LALR
├── slr_table.py              # Tablas SLR(1) ACTION/GOTO
├── lalr_table.py             # Tablas LALR(1) ACTION/GOTO (fusión de estados LR(1))
├── automaton_visualizer.py   # Generador HTML + DOT del autómata LR(0)
├── parser_codegen.py         # Generador de código del parser SLR/LALR
│
└── — Ejemplo generado —
    ├── pico_parser.py        # Parser SLR(1) generado (lenguaje pico)
    └── pico_parser_lexer.py  # Lexer generado (lenguaje pico)
```

## Requisitos

- Python 3.10+ (sin dependencias externas)
- Para visualización HTML: navegador con conexión a internet (Viz.js CDN) **o** Graphviz local para el `.dot`