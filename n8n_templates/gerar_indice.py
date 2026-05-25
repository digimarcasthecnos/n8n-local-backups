import json
import os
import re
from pathlib import Path

# ─── CONFIGURAÇÃO ─────────────────────────────────────────────
TEMPLATES_DIR = r"H:\Backup\Users\digim\Downloads\n8n_templates_master\n8n_templates"
OUTPUT_FILE   = r"H:\Backup\Users\digim\Downloads\n8n_templates_master\index.html"
# ──────────────────────────────────────────────────────────────

def extrair_integracoes(data):
    integracoes = set()
    nodes = data.get("nodes", [])  # ← direto na raiz
    for node in nodes:
        node_type = node.get("name", "")  # ← campo "name", não "type"
        partes = node_type.split(".")
        if len(partes) >= 2:
            nome = partes[-1]
            nome = re.sub(r'([A-Z])', r' \1', nome).strip()
            nome = nome.replace("Trigger", "").strip()
            if nome:
                integracoes.add(nome.title())
    return sorted(integracoes)

def processar_templates():
    templates = []
    arquivos = list(Path(TEMPLATES_DIR).glob("*.json"))
    total = len(arquivos)

    print(f"📂 Processando {total} arquivos JSON...\n")

    for i, arquivo in enumerate(arquivos, 1):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                data = json.load(f)

            nome        = data.get("name", arquivo.stem)
            descricao   = data.get("description", "")
            wf_id       = data.get("id", "")
            integracoes = extrair_integracoes(data)
            caminho     = str(arquivo).replace("\\", "/")

            templates.append({
                "id":          wf_id,
                "name":        nome,
                "description": descricao[:200].replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&") if descricao else "",
                "integrations": integracoes,
                "file":        caminho,
                "filename":    arquivo.name
            })

            if i % 500 == 0:
                print(f"  ✅ {i}/{total} processados...")

        except Exception as e:
            print(f"  ⚠️  Erro em {arquivo.name}: {e}")

    print(f"\n✅ Total processado: {len(templates)} templates")
    return templates

def gerar_html(templates):
    # Coleta todas as integrações únicas para os filtros
    todas_integracoes = set()
    for t in templates:
        todas_integracoes.update(t["integrations"])
    integracoes_sorted = sorted(todas_integracoes)

    templates_json = json.dumps(templates, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>n8n Templates — Biblioteca Local</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

  :root {{
    --bg:        #0d0f14;
    --surface:   #13161e;
    --border:    #1e2330;
    --accent:    #ff6b35;
    --accent2:   #7c3aed;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --card-bg:   #161923;
    --tag-bg:    #1e2330;
    --tag-active:#ff6b35;
  }}

  * {{ margin:0; padding:0; box-sizing:border-box; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
  }}

  /* ── HEADER ── */
  header {{
    background: linear-gradient(135deg, #0d0f14 0%, #13101f 100%);
    border-bottom: 1px solid var(--border);
    padding: 2rem 2.5rem 1.5rem;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(12px);
  }}

  .header-top {{
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.2rem;
  }}

  .logo {{
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
  }}

  h1 {{
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text);
  }}

  h1 span {{ color: var(--accent); }}

  .stats {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    margin-left: auto;
  }}

  /* ── SEARCH ── */
  .search-wrap {{
    position: relative;
    margin-bottom: 1rem;
  }}

  .search-wrap svg {{
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--muted);
  }}

  #busca {{
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.8rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.2s;
  }}

  #busca:focus {{ border-color: var(--accent); }}
  #busca::placeholder {{ color: var(--muted); }}

  /* ── FILTROS ── */
  .filtros {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    max-height: 80px;
    overflow-y: auto;
  }}

  .tag-filtro {{
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--tag-bg);
    color: var(--muted);
    font-size: 0.72rem;
    cursor: pointer;
    transition: all 0.15s;
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
  }}

  .tag-filtro:hover {{ border-color: var(--accent); color: var(--accent); }}
  .tag-filtro.ativo {{ background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 700; }}

  /* ── GRID ── */
  main {{
    padding: 1.5rem 2.5rem;
    max-width: 1600px;
    margin: 0 auto;
  }}

  .resultado-count {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    margin-bottom: 1rem;
  }}

  .resultado-count span {{ color: var(--accent); font-weight: 700; }}

  #grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1rem;
  }}

  /* ── CARD ── */
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    transition: border-color 0.2s, transform 0.15s;
    position: relative;
    overflow: hidden;
  }}

  .card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    opacity: 0;
    transition: opacity 0.2s;
  }}

  .card:hover {{ border-color: var(--accent); transform: translateY(-2px); }}
  .card:hover::before {{ opacity: 1; }}

  .card-id {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
  }}

  .card-name {{
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1.35;
  }}

  .card-desc {{
    font-size: 0.78rem;
    color: var(--muted);
    line-height: 1.5;
    flex: 1;
  }}

  .card-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    margin-top: 0.2rem;
  }}

  .card-tag {{
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    background: var(--tag-bg);
    color: var(--muted);
    font-size: 0.65rem;
    font-family: 'JetBrains Mono', monospace;
    border: 1px solid var(--border);
  }}

  .card-actions {{
    display: flex;
    gap: 0.5rem;
    margin-top: 0.3rem;
  }}

  .btn {{
    flex: 1;
    padding: 0.45rem 0.5rem;
    border-radius: 7px;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    cursor: pointer;
    text-align: center;
    text-decoration: none;
    border: none;
    transition: all 0.15s;
    font-weight: 700;
  }}

  .btn-vscode {{
    background: var(--accent);
    color: #fff;
  }}
  .btn-vscode:hover {{ background: #e55a25; }}

  .btn-copy {{
    background: var(--surface);
    color: var(--muted);
    border: 1px solid var(--border);
  }}
  .btn-copy:hover {{ color: var(--text); border-color: var(--accent2); }}

  /* ── EMPTY ── */
  #empty {{
    display: none;
    text-align: center;
    padding: 4rem;
    color: var(--muted);
  }}
  #empty svg {{ margin-bottom: 1rem; opacity: 0.3; }}

  /* scrollbar */
  ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
  ::-webkit-scrollbar-track {{ background: var(--bg); }}
  ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
</style>
</head>
<body>

<header>
  <div class="header-top">
    <div class="logo">⚡</div>
    <h1>n8n <span>Templates</span></h1>
    <div class="stats" id="stats">Carregando...</div>
  </div>

  <div class="search-wrap">
    <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
    </svg>
    <input type="text" id="busca" placeholder="Buscar por nome, descrição ou integração..." autocomplete="off">
  </div>

  <div class="filtros" id="filtros">
    <button class="tag-filtro ativo" data-filtro="todos" onclick="filtrar(this)">Todos</button>
    {"".join(f'<button class="tag-filtro" data-filtro="{i}" onclick="filtrar(this)">{i}</button>' for i in integracoes_sorted)}
  </div>
</header>

<main>
  <div class="resultado-count">Exibindo <span id="count">0</span> templates</div>
  <div id="grid"></div>
  <div id="empty">
    <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
    </svg>
    <p>Nenhum template encontrado.</p>
  </div>
</main>

<script>
const TEMPLATES = {templates_json};

let filtroAtivo = "todos";
let buscaAtual  = "";

function filtrar(el) {{
  document.querySelectorAll('.tag-filtro').forEach(b => b.classList.remove('ativo'));
  el.classList.add('ativo');
  filtroAtivo = el.dataset.filtro;
  renderizar();
}}

document.getElementById('busca').addEventListener('input', e => {{
  buscaAtual = e.target.value.toLowerCase();
  renderizar();
}});

function escapeHtml(str) {{
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function copiarJSON(btn, filename) {{
  const caminho = `H:/Backup/Users/digim/Downloads/n8n_templates_master/n8n_templates/${{filename}}`;
  navigator.clipboard.writeText(caminho).then(() => {{
    btn.textContent = '✓ Copiado!';
    setTimeout(() => btn.textContent = 'Copiar Caminho', 1500);
  }});
}}

function renderizar() {{
  const grid  = document.getElementById('grid');
  const empty = document.getElementById('empty');
  let exibidos = 0;

  const filtrados = TEMPLATES.filter(t => {{
    const matchFiltro = filtroAtivo === "todos" || t.integrations.includes(filtroAtivo);
    const texto = (t.name + ' ' + t.description + ' ' + t.integrations.join(' ')).toLowerCase();
    const matchBusca = !buscaAtual || texto.includes(buscaAtual);
    return matchFiltro && matchBusca;
  }});

  exibidos = filtrados.length;
  document.getElementById('count').textContent = exibidos.toLocaleString('pt-BR');

  if (exibidos === 0) {{
    grid.innerHTML = '';
    empty.style.display = 'block';
    return;
  }}
  empty.style.display = 'none';

  // Renderiza em lote para não travar o browser
  const chunk = filtrados.slice(0, 200);
  grid.innerHTML = chunk.map(t => `
    <div class="card">
      <div class="card-id">#${{escapeHtml(t.id)}}</div>
      <div class="card-name">${{escapeHtml(t.name)}}</div>
      ${{t.description ? `<div class="card-desc">${{escapeHtml(t.description)}}</div>` : ''}}
      ${{t.integrations.length ? `
        <div class="card-tags">
          ${{t.integrations.slice(0,6).map(i => `<span class="card-tag">${{escapeHtml(i)}}</span>`).join('')}}
          ${{t.integrations.length > 6 ? `<span class="card-tag">+${{t.integrations.length - 6}}</span>` : ''}}
        </div>` : ''}}
      <div class="card-actions">
        <a class="btn btn-vscode" href="vscode://file/${{encodeURIComponent(t.file).replace(/%2F/g,'/')}}">
          ⚡ Abrir no VS Code
        </a>
        <button class="btn btn-copy" onclick="copiarJSON(this, '${{escapeHtml(t.filename)}}')">
          Copiar Caminho
        </button>
      </div>
    </div>
  `).join('');

  if (filtrados.length > 200) {{
    const aviso = document.createElement('div');
    aviso.style.cssText = 'grid-column:1/-1;text-align:center;padding:1.5rem;color:#64748b;font-family:JetBrains Mono,monospace;font-size:.75rem;';
    aviso.textContent = `Exibindo 200 de ${{filtrados.length.toLocaleString('pt-BR')}} resultados. Refine a busca para ver mais.`;
    grid.appendChild(aviso);
  }}
}}

// Init
document.getElementById('stats').textContent =
  `${{TEMPLATES.length.toLocaleString('pt-BR')}} templates · ${{new Date().toLocaleDateString('pt-BR')}}`;
renderizar();
</script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"🎉 Índice HTML gerado com sucesso!")
    print(f"📄 Arquivo: {OUTPUT_FILE}")
    print(f"\n➡️  Abra o arquivo index.html no navegador para usar.")

if __name__ == "__main__":
    templates = processar_templates()
    gerar_html(templates)
