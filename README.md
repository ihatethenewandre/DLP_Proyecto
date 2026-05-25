# YALex — Yet Another Lex
## Generador de Analizadores Léxicos

**Universidad del Valle de Guatemala**  
**Diseño de Lenguajes de Programación**  
**Proyecto I**

Genser Andree Catalán Espina – 23401  
Roberto Samuel Nájera Marroquín – 23781  
André Emilio Pivaral López – 23574

---

## Descripción

YALex es un generador de analizadores léxicos que toma como entrada un archivo escrito en lenguaje YALex (`.yal`) y produce un programa fuente en Python que implementa el analizador léxico correspondiente. El lexer generado es capaz de reconocer los tokens especificados o reportar errores léxicos.

## Arquitectura

El sistema sigue una arquitectura modular de **4 fases**:

```
                                                     PIPELINE
                                                                                    
  ┌────────────────┐     ┌────────────────┐     ┌────────────────────────────┐     ┌────────────────┐
  │  1. Lector y   │     │  2. Parser de  │     │ 3. AFD directo (followpos) │     │  4. Generador  │
  │ Preprocesador  │  →  |      Regex     │  →  │ + clases de símbolo + Hop │  →  │     Código     │
  └────────────────┘     └────────────────┘     └────────────────────────────┘     └────────────────┘
      reader.py           regex_parser.py              dfa_builder.py              code_generator.py

  Archivo .yal ─────────────────────────────────────────────────────────────────────────────▶ Lexer Generado .py
```

### Tablas de símbolos

- **Tabla de posiciones (build-time):** cada hoja del AST aumentado (`(rᵢ · #ᵢ)` unidos por `|`) recibe un índice; se almacenan el conjunto de caracteres de la hoja, si es marcador de fin de regla, y la regla asociada. De ahí se calculan `nullable`, `firstpos`, `lastpos` y `followpos` para construir el AFD sin pasar por un AFN.
- **Tabla de clases de byte (runtime):** los bytes `0..255` se agrupan en clases de equivalencia (dos bytes están en la misma clase si pertenecen exactamente al mismo conjunto de hojas del patrón). El lexer generado traduce `byte → id de clase` y la tabla de transiciones del AFD está indexada por ese id (más una clase opcional para `eof` en el autómata).

### Módulo 1: Lector y Preprocesador (`reader.py`)
- Lee el archivo `.yal` y elimina comentarios `(* ... *)`
- Divide el contenido en: header, definiciones (`let`), reglas (`rule`), trailer
- Produce una estructura `YALexSpec` con toda la información parseada

### Módulo 2: Parser de Expresiones Regulares (`regex_parser.py`)
- Convierte cada expresión regular en texto a un Árbol Sintáctico (AST)
- Soporta la precedencia completa de YALex: `#` > `*, +, ?` > concatenación > `|`
- Maneja: caracteres literales `'c'`, cadenas `"str"`, conjuntos `[a-z]`, negación `[^...]`, wildcard `_`, `eof`, identificadores de definiciones

### Módulo 3: AFD directo y minimización (`dfa_builder.py`)
- Normaliza `#` y `_` a clases de caracteres donde aplica
- Construye el AST aumentado `(r₀·#₀) | (r₁·#₁) | …`, registra **posiciones** (hojas) y calcula **followpos** (construcción directa estilo Dragon Book §3.9.5)
- Particiona el alfabeto de bytes en **clases de símbolo** y construye transiciones del AFD sobre ids de clase (y transiciones `eof` cuando el patrón usa `eof`)
- **Minimización de Hopcroft** sobre los estados del AFD, preservando la prioridad de reglas (menor índice = mayor prioridad)

### Módulo 4: Generador de Código (`code_generator.py`)
- Emite `_CHAR_CLASS_TABLE` (256 entradas) y `_TRANSITION_TABLE` indexada por id de clase
- Incluye la simulación del AFD: longest match, posible cadena de transiciones de clase `eof` al agotar la entrada, y manejo de errores léxicos
- Produce un archivo Python ejecutable y autónomo

## Uso

El programa se ejecuta en dos pasos:

### Paso 1 — Generar el analizador léxico a partir de un archivo `.yal`:
```bash
python yalex.py <archivo.yal> -o <nombre_salida.py>
```
- `<archivo.yal>` — archivo de especificación escrito en lenguaje YALex (proporcionado como entrada)
- `-o <nombre_salida.py>` — nombre del archivo Python que se generará (opcional, por defecto `generated_lexer.py`)

### Paso 2 — Ejecutar el analizador generado sobre un archivo fuente:
```bash
python <lexer_generado.py> <archivo_fuente>
```
- `<lexer_generado.py>` — el archivo producido en el Paso 1
- `<archivo_fuente>` — archivo de texto plano a tokenizar (cualquier nombre y extensión)

## Estructura del repositorio

```
DLP_Proyecto/
├── .gitignore
├── README.md               # Documentación del proyecto
├── yalex.py                # Punto de entrada — orquestador del pipeline
├── reader.py               # Módulo 1: Lector y Preprocesador
├── regex_parser.py         # Módulo 2: Parser de Expresiones Regulares
├── dfa_builder.py          # Módulo 3: AFD directo (followpos) + minimización
└── code_generator.py       # Módulo 4: Generador de Código
```

## Algoritmos Implementados

| Algoritmo | Módulo | Descripción |
|-----------|--------|-------------|
| Eliminación de comentarios | reader.py | Manejo de `(* ... *)` con anidamiento |
| Parsing de regex | regex_parser.py | Parser recursivo descendente con precedencia |
| AFD directo (followpos) | dfa_builder.py | `nullable` / `firstpos` / `lastpos` / `followpos` sobre tabla de posiciones |
| Clases de símbolo (alfabeto) | dfa_builder.py | Equivalencia de bytes según hojas del patrón; transiciones por id de clase |
| Hopcroft Minimization | dfa_builder.py | Minimización del AFD por partición (incluye clase `eof` si aplica) |
| Longest Match | generated_lexer.py | Simulación del AFD con backtracking al último estado de aceptación |

## Requisitos

- Python 3.10.+ (no requiere bibliotecas externas)
