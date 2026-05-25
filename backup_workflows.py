import urllib.request
import urllib.parse
import json
import os
from datetime import datetime

# ── CONFIGURAÇÃO ──────────────────────────────────────────
N8N_URL   = "http://localhost:5678"
API_KEY   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1YjM0MGE3Yi04YzNiLTRlNzAtYTBjNC0xZmI0MzcyNDNjYmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNTM4YjhjYTQtNzQ1My00ZGVlLTg5Y2MtNjI2NDYyNzBiOTQxIiwiaWF0IjoxNzc4NTI0MzcwfQ.B5rlQHXza_h6DliVLU6ifUYqQk9Vxdv0BHrgyPekDXU"
BACKUP_DIR = r"C:\n8n-local\backups"
# ──────────────────────────────────────────────────────────

os.makedirs(BACKUP_DIR, exist_ok=True)

headers = {
    "Content-Type": "application/json",
    "X-N8N-API-KEY": API_KEY
}

todos = []
cursor = None
pagina = 1

print("🔄 Buscando workflows (paginação)...")

while True:
    url = f"{N8N_URL}/api/v1/workflows?limit=250"
    if cursor:
        url += f"&cursor={urllib.parse.quote(cursor)}"

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            items = data.get("data", [])
            todos.extend(items)
            print(f"  Página {pagina}: +{len(items)} workflows (total: {len(todos)})")

            cursor = data.get("nextCursor")
            if not cursor:
                break
            pagina += 1

    except Exception as e:
        print(f"❌ Erro na página {pagina}: {e}")
        break

print(f"\n✅ Total encontrado: {len(todos)} workflows")
print("💾 Salvando arquivos...")

for wf in todos:
    name = "".join(c for c in wf["name"] if c.isalnum() or c in " _-")
    fname = f"{wf['id']}_{name[:50]}.json"
    fpath = os.path.join(BACKUP_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)

print(f"📁 Backups salvos em: {BACKUP_DIR}")
print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")