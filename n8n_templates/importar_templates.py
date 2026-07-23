import requests, json, os, time

N8N_URL = "http://localhost:5678"
API_KEY = os.environ["N8N_API_KEY"]  # export N8N_API_KEY=... (ver chaves-n8n.txt / ~/.minhas_chaves.env)
TEMPLATES_DIR = r"H:\Backup\Users\digim\Downloads\n8n_templates_master\n8n_templates"

headers = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}
arquivos = [f for f in os.scandir(TEMPLATES_DIR) if f.name.endswith(".json")]
total = len(arquivos)
importados = erros = pulados = 0
print(f"Iniciando importacao de {total} templates...")

for i, arquivo in enumerate(arquivos, 1):
    try:
        with open(arquivo.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extrai workflow correto
        wf = data.get("workflow", {})

        # Monta payload obrigatório
        payload = {
            "name": data.get("name", arquivo.name.replace(".json", "")),
            "nodes": wf.get("nodes", []),
            "connections": wf.get("connections", {}),
            "settings": wf.get("settings", {}),
            "staticData": wf.get("staticData", None)
        }

        # Pula se não tiver nodes
        if not payload["nodes"]:
            pulados += 1
            continue

        r = requests.post(
            f"{N8N_URL}/api/v1/workflows",
            headers=headers,
            json=payload,
            timeout=10
        )
        if r.status_code in [200, 201]:
            importados += 1
        else:
            erros += 1

        if i % 200 == 0:
            print(f"{i}/{total} - OK:{importados} ERR:{erros} PULADOS:{pulados}")

        time.sleep(0.1)

    except Exception as e:
        erros += 1

print(f"\nConcluido! OK:{importados} ERR:{erros} PULADOS:{pulados}")