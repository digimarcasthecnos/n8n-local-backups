import requests, json, time
from collections import defaultdict

BASE_URL = "http://localhost:5678"
API_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1YjM0MGE3Yi04YzNiLTRlNzAtYTBjNC0xZmI0MzcyNDNjYmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNTM4YjhjYTQtNzQ1My00ZGVlLTg5Y2MtNjI2NDYyNzBiOTQxIiwiaWF0IjoxNzc4NTI0MzcwfQ.B5rlQHXza_h6DliVLU6ifUYqQk9Vxdv0BHrgyPekDXU"
HEADERS  = {"X-N8N-API-KEY": API_KEY}

print("=" * 55)
print("  n8n Deduplicador - rodando em localhost:5678")
print("=" * 55)

# 1. Buscar todos os workflows
print("\nBuscando workflows...")
all_wf, cursor, page = [], None, 1
while True:
    params = {"limit": 250}
    if cursor:
        params["cursor"] = cursor
    for tentativa in range(5):
        try:
            r = requests.get(
                f"{BASE_URL}/api/v1/workflows",
                headers=HEADERS,
                params=params,
                timeout=30
            )
            if r.status_code == 200:
                break
            print(f"  HTTP {r.status_code} - aguardando...")
            time.sleep(10)
        except Exception as ex:
            print(f"  Erro: {ex} - tentativa {tentativa+1}/5")
            time.sleep(10)
    data   = r.json()
    wfs    = data.get("data", [])
    all_wf.extend(wfs)
    cursor = data.get("nextCursor")
    print(f"  Pag {page:>3} | +{len(wfs)} | Total: {len(all_wf)}", flush=True)
    page  += 1
    time.sleep(0.3)
    if not cursor:
        break

print(f"\nTotal encontrado: {len(all_wf)} workflows")

# 2. Encontrar duplicatas por nome
print("Analisando duplicatas...")
by_name = defaultdict(list)
for wf in all_wf:
    nome = (wf.get("name") or "").strip()
    by_name[nome].append(wf)

to_delete = []
for nome, grupo in by_name.items():
    if len(grupo) > 1:
        # Mantém o mais recente, deleta os demais
        grupo.sort(key=lambda w: w.get("updatedAt", ""), reverse=True)
        for wf in grupo[1:]:
            to_delete.append(wf["id"])

unicos = len(all_wf) - len(to_delete)
print(f"\nResultado:")
print(f"  Workflows unicos:  {unicos}")
print(f"  A deletar:         {len(to_delete)}")
print(f"  Restarao:          {unicos}")

if not to_delete:
    print("\nNenhuma duplicata encontrada!")
    input("Pressione Enter para sair.")
    exit()

# 3. Confirmacao antes de deletar
print(f"\nPronto para deletar {len(to_delete)} duplicatas.")
resp = input("Confirmar? (s/n): ").strip().lower()
if resp != "s":
    print("Cancelado.")
    exit()

# 4. Deletar
print(f"\nDeletando...")
d = e = 0
for i, wf_id in enumerate(to_delete):
    r = requests.delete(
        f"{BASE_URL}/api/v1/workflows/{wf_id}",
        headers=HEADERS,
        timeout=10
    )
    if r.status_code in (200, 204):
        d += 1
    else:
        e += 1
    if (i + 1) % 500 == 0:
        print(f"  Progresso: {i+1}/{len(to_delete)} | ok={d} err={e}", flush=True)
    time.sleep(0.05)

print(f"\n{'='*55}")
print(f"  CONCLUIDO!")
print(f"  Deletados: {d}")
print(f"  Erros:     {e}")
print(f"  Restaram:  {len(all_wf) - d} workflows")
print(f"{'='*55}")
input("\nPressione Enter para sair.")
