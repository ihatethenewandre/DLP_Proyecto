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

El sistema sigue una arquitectura modular de 5 fases:

```
                                                     PIPELINE
                                                                                    
  ┌────────────────┐     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
  │  1. Lector y   │     │  2. Parser de  │     │ 3. Constructor │     │  4. Conversor  │     │  5. Generador  │
  │ Preprocesador  │  →  |      Regex     │  →  │       AFN      │  →  │   AFN a AFD    │  →  │     Código     │
  └────────────────┘     └────────────────┘     └────────────────┘     └────────────────┘     └────────────────┘
      reader.py           regex_parser.py         nfa_builder.py         dfa_builder.py       code_generator.py

  Archivo .yal ─────────────────────────────────────────────────────────────────────────────▶ Lexer Generado .py
```

### Módulo 1: Lector y Preprocesador (`reader.py`)
- Lee el archivo `.yal` y elimina comentarios `(* ... *)`
- Divide el contenido en: header, definiciones (`let`), reglas (`rule`), trailer
- Produce una estructura `YALexSpec` con toda la información parseada

### Módulo 2: Parser de Expresiones Regulares (`regex_parser.py`)
- Convierte cada expresión regular en texto a un Árbol Sintáctico (AST)
- Soporta la precedencia completa de YALex: `#` > `*, +, ?` > concatenación > `|`
- Maneja: caracteres literales `'c'`, cadenas `"str"`, conjuntos `[a-z]`, negación `[^...]`, wildcard `_`, `eof`, identificadores de definiciones

### Módulo 3: Constructor de AFN (`nfa_builder.py`)
- Aplica la **construcción de Thompson** para cada expresión regular
- Soporta: literales, clases de caracteres, concatenación, alternación, `*`, `+`, `?`, diferencia `#`
- Combina todos los AFN individuales en un solo AFN con un nuevo estado inicial

### Módulo 4: Conversor AFN → AFD (`dfa_builder.py`)
- Implementa el **algoritmo de construcción de subconjuntos** (epsilon-cerradura + move)
- Preserva la prioridad de reglas (menor índice = mayor prioridad)
- Incluye **minimización del AFD** usando el algoritmo de partición de Hopcroft

### Módulo 5: Generador de Código (`code_generator.py`)
- Serializa el AFD como una **tabla de transiciones estática** en Python
- Genera la lógica de simulación completa: lectura de caracteres, avance de estados, longest match
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
├── nfa_builder.py          # Módulo 3: Constructor de AFN (Thompson)
├── dfa_builder.py          # Módulo 4: Conversor AFN→AFD + Minimización
└── code_generator.py       # Módulo 5: Generador de Código
```

## Algoritmos Implementados

| Algoritmo | Módulo | Descripción |
|-----------|--------|-------------|
| Eliminación de comentarios | reader.py | Manejo de `(* ... *)` con anidamiento |
| Parsing de regex | regex_parser.py | Parser recursivo descendente con precedencia |
| Thompson's Construction | nfa_builder.py | Conversión regex → AFN con ε-transiciones |
| Subset Construction | dfa_builder.py | Conversión AFN → AFD con ε-cerradura |
| Hopcroft Minimization | dfa_builder.py | Minimización del AFD por partición |
| Longest Match | generated_lexer.py | Simulación del AFD con backtracking al último estado de aceptación |

## Requisitos

- Python 3.10.+ (no requiere bibliotecas externas)
