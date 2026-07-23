import urllib.request
import urllib.parse
import json
import os
import time
from datetime import datetime

# ── CONFIGURAÇÃO ──────────────────────────────────────────
N8N_URL  = "http://localhost:5678"
API_KEY  = os.environ["N8N_API_KEY"]  # export N8N_API_KEY=... (ver chaves-n8n.txt / ~/.minhas_chaves.env)
# ──────────────────────────────────────────────────────────

headers = {
    "Content-Type": "application/json",
    "X-N8N-API-KEY": API_KEY
}

def api(method, path, body=None):
    req = urllib.request.Request(
        f"{N8N_URL}/api/v1{path}",
        headers=headers,
        method=method,
        data=json.dumps(body).encode() if body else None
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# Buscar todos os workflows com paginação
print("🔄 Buscando workflows...")
todos = []
cursor = None
pagina = 1

while True:
    url = "/workflows?limit=250"
    if cursor:
        url += f"&cursor={urllib.parse.quote(cursor)}"
    data = api("GET", url)
    items = data.get("data", [])
    todos.extend(items)
    print(f"  Página {pagina}: {len(todos)} total")
    cursor = data.get("nextCursor")
    if not cursor:
        break
    pagina += 1

print(f"\n✅ Total: {len(todos)} workflows")

# Filtrar com credenciais E não ativos
com_cred = []
for wf in todos:
    if wf.get("active"):
        continue
    nodes = wf.get("nodes", [])
    tem_cred = any(n.get("credentials") for n in nodes)
    if tem_cred:
        com_cred.append(wf)

print(f"🔑 Com credenciais (inativos): {len(com_cred)}")
print("\n⚡ Ativando...")

ok = 0
erro = 0

for wf in com_cred:
    try:
        api("POST", f"/workflows/{wf['id']}/activate")
        print(f"  ✅ [{wf['id']}] {wf['name'][:60]}")
        ok += 1
        time.sleep(0.3)  # evitar sobrecarga
    except Exception as e:
        print(f"  ❌ [{wf['id']}] {wf['name'][:50]} → {e}")
        erro += 1

print(f"\n{'='*50}")
print(f"✅ Ativados: {ok}")
print(f"❌ Erros:    {erro}")
print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
