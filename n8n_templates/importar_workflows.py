import requests, json, os, time

N8N_URL = "http://localhost:5678"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1YjM0MGE3Yi04YzNiLTRlNzAtYTBjNC0xZmI0MzcyNDNjYmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNTM4YjhjYTQtNzQ1My00ZGVlLTg5Y2MtNjI2NDYyNzBiOTQxIiwiaWF0IjoxNzc4NTI0MzcwfQ.B5rlQHXza_h6DliVLU6ifUYqQk9Vxdv0BHrgyPekDXU"
WORKFLOWS_DIR = r"H:\Backup\Users\digim\Downloads\n8n_templates_master\n8n_workflows"

headers = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}
arquivos = [f for f in os.scandir(WORKFLOWS_DIR) if f.name.endswith(".json")]
total = len(arquivos)
importados = erros = pulados = 0
print(f"Iniciando importacao de {total} workflows...")

for i, arquivo in enumerate(arquivos, 1):
    try:
        with open(arquivo.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        outer = data.get("workflow", {})
        actual = outer.get("workflow", {})
        nodes = actual.get("nodes", [])
        if not nodes:
            pulados += 1
            continue
        payload = {
            "name": outer.get("name", arquivo.name.replace(".json", "")),
            "nodes": nodes,
            "connections": actual.get("connections", {}),
            "settings": actual.get("settings", {})
        }
        r = requests.post(
            f"{N8N_URL}/api/v1/workflows",
            headers=headers,
            json=payload,
            timeout=60
        )
        if r.status_code in [200, 201]:
            importados += 1
        else:
            erros += 1
        if i % 200 == 0:
            print(f"{i}/{total} - OK:{importados} ERR:{erros} SKIP:{pulados}")
        time.sleep(0.2)
    except Exception as e:
        erros += 1
        if erros <= 3:
            print(f"ERRO: {type(e).__name__}: {str(e)[:100]}")

print(f"\nConcluido! OK:{importados} ERR:{erros} SKIP:{pulados}")