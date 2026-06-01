# --------------------------------------------------------------------------------------------------------
# automaton_visualizer.py
# --------------------------------------------------------------------------------------------------------
# UNIVERSIDAD DEL VALLE DE GUATEMALA
# Diseño de Lenguajes de Programación
#
# Descripción: Generador de representación visual del autómata LR(0)
#
#              Produce dos artefactos de visualización a partir de la colección
#              canónica LR(0):
#                1. Archivo .dot (Graphviz) — abrir con `dot -Tsvg lr0.dot -o lr0.svg`
#                   o en https://dreampuf.github.io/GraphvizOnline/
#                2. Archivo .html autocontenido — renderiza el autómata directamente
#                   en el navegador sin dependencias locales (usa Viz.js desde CDN).
#
# Autores:     André Pivaral, Roberto Nájera, Genser Catalán
# Fecha:       23 de Marzo de 2026
# --------------------------------------------------------------------------------------------------------

from __future__ import annotations
from grammar import Grammar
from lr_automaton import LRState


# ---------------------------------------- GENERACIÓN DOT ----------------------------------------

def _dot_escape(s: str) -> str:
    """Escapa caracteres especiales para etiquetas DOT."""
    return (
        s.replace('\\', '\\\\')
         .replace('"', '\\"')
         .replace('<', '\\<')
         .replace('>', '\\>')
         .replace('{', '\\{')
         .replace('}', '\\}')
         .replace('|', '\\|')
    )


def generate_dot(states: list[LRState], grammar: Grammar) -> str:
    """
    Genera una cadena en formato Graphviz DOT representando el autómata LR(0).

    Cada nodo muestra el id del estado y sus ítems (con el punto •).
    Los estados de aceptación (S' → start •) usan doble octágono.
    """
    lines = [
        'digraph LR0_Automaton {',
        '    rankdir=LR;',
        '    graph [fontname="Courier New" fontsize=11 splines=ortho nodesep=0.6];',
        '    node  [fontname="Courier New" fontsize=10 shape=box style=rounded];',
        '    edge  [fontname="Arial" fontsize=10 color="#555555"];',
        '',
    ]

    aug_start = "S'"

    for state in states:
        # Construir etiqueta del nodo
        item_lines = [f"Estado {state.id}"]
        for item in sorted(state.items, key=lambda x: (x.prod_index, x.dot)):
            prod = grammar.productions[item.prod_index]
            rhs = list(prod.rhs)
            rhs.insert(item.dot, '•')
            rhs_str = ' '.join(rhs) if rhs else 'ε'
            item_lines.append(f"  {prod.lhs} → {rhs_str}")

        label = '\\n'.join(_dot_escape(line) for line in item_lines)

        # ¿Es estado de aceptación? (contiene S' → start •)
        is_accept = any(
            item.is_complete(grammar)
            and grammar.productions[item.prod_index].lhs == aug_start
            for item in state.items
        )
        shape = "doubleoctagon" if is_accept else "box"
        color = '"#1a6b3a"' if is_accept else '"#1a3a6b"'
        fillcolor = '"#d4edda"' if is_accept else '"#dce8f8"'

        lines.append(
            f'    state{state.id} [label="{label}" shape={shape} '
            f'color={color} fillcolor={fillcolor} style="rounded,filled"];'
        )

    lines.append('')
    lines.append('    // Flecha de inicio')
    lines.append('    __start__ [shape=point width=0.2];')
    lines.append('    __start__ -> state0 [color="#333333"];')
    lines.append('')

    lines.append('    // Transiciones')
    for state in states:
        for sym, next_id in sorted(state.transitions.items()):
            escaped = _dot_escape(sym)
            lines.append(
                f'    state{state.id} -> state{next_id} [label="{escaped}"];'
            )

    lines.append('}')
    return '\n'.join(lines)


def generate_automaton_dot_file(
    states: list[LRState],
    grammar: Grammar,
    output_file: str = "lr0_automaton.dot",
) -> str:
    """Escribe el autómata LR(0) en formato Graphviz DOT."""
    dot = generate_dot(states, grammar)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(dot)
    return output_file


# ---------------------------------------- GENERACIÓN HTML ----------------------------------------

def generate_automaton_html(
    states: list[LRState],
    grammar: Grammar,
    output_file: str = "lr0_automaton.html",
    parser_type: str = "SLR(1)",
) -> str:
    """
    Genera un archivo HTML autocontenido que muestra el autómata LR(0)
    interactivo usando Viz.js (Graphviz compilado a WebAssembly).

    El HTML incluye:
    - Panel de estadísticas del autómata
    - Diagrama SVG interactivo (zoom, pan)
    - Tabla de ítems por estado
    - Código DOT colapsable
    """
    dot_source = generate_dot(states, grammar)

    # Calcular estadísticas
    total_items = sum(len(s.items) for s in states)
    total_trans = sum(len(s.transitions) for s in states)
    num_nt = len(grammar.nonterminals)
    num_t  = len(grammar.terminals)
    num_prods = len(grammar.productions)

    # Tabla de ítems HTML (escapada)
    state_rows_html = ""
    aug_start = "S'"
    for state in states:
        is_accept = any(
            item.is_complete(grammar)
            and grammar.productions[item.prod_index].lhs == aug_start
            for item in state.items
        )
        badge = '<span class="badge accept">ACCEPT</span>' if is_accept else ''

        item_strs = []
        for item in sorted(state.items, key=lambda x: (x.prod_index, x.dot)):
            prod = grammar.productions[item.prod_index]
            rhs = list(prod.rhs)
            rhs.insert(item.dot, '<span class="dot">•</span>')
            rhs_str = ' '.join(rhs) if prod.rhs or item.dot > 0 else 'ε'
            item_strs.append(
                f"<code>{prod.lhs} → {rhs_str}</code>"
            )

        trans_strs = [
            f'<code>{sym}</code> → Estado {nxt}'
            for sym, nxt in sorted(state.transitions.items())
        ]

        state_rows_html += f"""
        <tr>
          <td class="state-id">{state.id}{badge}</td>
          <td>{'<br>'.join(item_strs)}</td>
          <td>{'<br>'.join(trans_strs) if trans_strs else '—'}</td>
        </tr>"""

    # Escapar DOT para JavaScript (template literal)
    dot_for_js = (
        dot_source
        .replace('\\', '\\\\')
        .replace('`', '\\`')
        .replace('$', '\\$')
    )
    # Para mostrar en <pre> (escapar HTML)
    dot_html = (
        dot_source
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Autómata LR(0) — {parser_type} — YAPar</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js"></script>
  <style>
    :root {{
      --bg:       #1e1e2e;
      --surface:  #313244;
      --surface2: #45475a;
      --blue:     #89b4fa;
      --green:    #a6e3a1;
      --red:      #f38ba8;
      --yellow:   #f9e2af;
      --text:     #cdd6f4;
      --subtext:  #a6adc8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      padding: 24px;
    }}
    h1 {{ color: var(--blue); font-size: 22px; margin-bottom: 6px; }}
    .subtitle {{ color: var(--subtext); font-size: 13px; margin-bottom: 20px; }}

    /* ---- Tarjetas de estadísticas ---- */
    .stats {{
      display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px;
    }}
    .stat-card {{
      background: var(--surface); border-radius: 10px;
      padding: 14px 20px; min-width: 110px;
    }}
    .stat-label {{ font-size: 11px; color: var(--subtext); text-transform: uppercase; margin-bottom: 4px; }}
    .stat-value {{ font-size: 28px; font-weight: 700; color: var(--blue); }}

    /* ---- Pestañas ---- */
    .tabs {{ display: flex; gap: 4px; margin-bottom: 16px; }}
    .tab {{
      padding: 8px 18px; border-radius: 6px 6px 0 0;
      background: var(--surface); border: none; color: var(--subtext);
      cursor: pointer; font-size: 14px; transition: background .15s;
    }}
    .tab.active {{ background: var(--surface2); color: var(--text); }}
    .tab:hover {{ background: var(--surface2); }}

    /* ---- Paneles de contenido ---- */
    .panel {{ display: none; }}
    .panel.active {{ display: block; }}

    /* ---- Diagrama SVG ---- */
    #graph-container {{
      background: #fff; border-radius: 10px; padding: 12px;
      min-height: 420px; overflow: auto; position: relative;
    }}
    #graph-container svg {{ max-width: 100%; height: auto; display: block; margin: auto; }}
    .loading {{ text-align: center; padding: 60px; color: var(--subtext); font-size: 16px; }}
    .error {{ color: var(--red); padding: 20px; text-align: center; }}
    .error a {{ color: var(--blue); }}

    /* ---- Tabla de estados ---- */
    table {{
      width: 100%; border-collapse: collapse;
      background: var(--surface); border-radius: 10px; overflow: hidden;
    }}
    th {{
      background: var(--surface2); padding: 10px 14px;
      text-align: left; font-size: 13px; color: var(--subtext);
      text-transform: uppercase;
    }}
    td {{
      padding: 10px 14px; border-top: 1px solid var(--surface2);
      font-size: 13px; vertical-align: top;
    }}
    .state-id {{
      font-weight: 700; font-size: 15px; color: var(--blue);
      white-space: nowrap;
    }}
    tr:hover td {{ background: var(--surface2); }}
    .dot {{ color: #f5a742; font-weight: bold; }}
    .badge {{
      display: inline-block; font-size: 10px; padding: 1px 6px;
      border-radius: 4px; margin-left: 6px; font-weight: bold;
      vertical-align: middle;
    }}
    .badge.accept {{ background: #1a6b3a; color: var(--green); }}

    /* ---- Código DOT ---- */
    details {{ margin-top: 20px; }}
    summary {{
      cursor: pointer; color: var(--blue); font-weight: 600;
      padding: 8px 0; user-select: none;
    }}
    pre.dot-code {{
      background: #12121e; border-radius: 8px; padding: 16px;
      font-family: 'Courier New', monospace; font-size: 12px;
      color: var(--green); overflow-x: auto; white-space: pre;
      max-height: 360px; overflow-y: auto; margin-top: 8px;
    }}
  </style>
</head>
<body>
  <h1>🤖 Autómata LR(0) — {parser_type}</h1>
  <p class="subtitle">Universidad del Valle de Guatemala · CC3071 Diseño de Lenguajes de Programación · YAPar</p>

  <div class="stats">
    <div class="stat-card">
      <div class="stat-label">Estados</div>
      <div class="stat-value">{len(states)}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Ítems totales</div>
      <div class="stat-value">{total_items}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Transiciones</div>
      <div class="stat-value">{total_trans}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">No-terminales</div>
      <div class="stat-value">{num_nt}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Terminales</div>
      <div class="stat-value">{num_t}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Producciones</div>
      <div class="stat-value">{num_prods}</div>
    </div>
  </div>

  <div class="tabs">
    <button class="tab active" onclick="showTab('diagram')">📊 Diagrama</button>
    <button class="tab" onclick="showTab('table')">📋 Tabla de estados</button>
  </div>

  <!-- Panel: Diagrama -->
  <div id="tab-diagram" class="panel active">
    <div id="graph-container">
      <div class="loading" id="loading-msg">⏳ Renderizando autómata con Viz.js…</div>
    </div>
  </div>

  <!-- Panel: Tabla de estados -->
  <div id="tab-table" class="panel">
    <table>
      <thead>
        <tr>
          <th>Estado</th>
          <th>Ítems LR(0)</th>
          <th>Transiciones</th>
        </tr>
      </thead>
      <tbody>
        {state_rows_html}
      </tbody>
    </table>
  </div>

  <details>
    <summary>🔧 Ver código Graphviz DOT</summary>
    <pre class="dot-code">{dot_html}</pre>
  </details>

  <script>
    function showTab(name) {{
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      document.getElementById('tab-' + name).classList.add('active');
      event.target.classList.add('active');
    }}

    const dotSource = `{dot_for_js}`;

    const viz = new Viz();
    viz.renderSVGElement(dotSource)
      .then(svg => {{
        const c = document.getElementById('graph-container');
        document.getElementById('loading-msg').remove();
        c.appendChild(svg);
      }})
      .catch(err => {{
        const c = document.getElementById('graph-container');
        c.innerHTML = `
          <div class="error">
            <p>❌ No se pudo renderizar el autómata (sin conexión a CDN o gramática muy grande).</p>
            <p style="margin-top:10px">
              Copie el código DOT del panel inferior y péguelo en
              <a href="https://dreampuf.github.io/GraphvizOnline/" target="_blank">
                dreampuf.github.io/GraphvizOnline
              </a>.
            </p>
            <p style="margin-top:6px; font-size:12px; color:#888">Error: ${{err}}</p>
          </div>`;
      }});
  </script>
</body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_file