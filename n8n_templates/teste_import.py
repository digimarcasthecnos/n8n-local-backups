import requests, json, os

N8N_URL = "http://localhost:5678"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1YjM0MGE3Yi04YzNiLTRlNzAtYTBjNC0xZmI0MzcyNDNjYmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNTM4YjhjYTQtNzQ1My00ZGVlLTg5Y2MtNjI2NDYyNzBiOTQxIiwiaWF0IjoxNzc4NTI0MzcwfQ.B5rlQHXza_h6DliVLU6ifUYqQk9Vxdv0BHrgyPekDXU"

headers = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}
pasta = r"H:\Backup\Users\digim\Downloads\n8n_templates_master\n8n_workflows"
arquivo = next(f for f in os.scandir(pasta) if f.name.endswith(".json"))

with open(arquivo.path, "r", encoding="utf-8") as f:
    data = json.load(f)

outer = data.get("workflow", {})
actual = outer.get("workflow", {})

payload = {
    "name": outer.get("name", "teste"),
    "nodes": actual.get("nodes", []),
    "connections": actual.get("connections", {}),
    "settings": actual.get("settings", {})
}

print("Nome:", payload["name"])
print("Nodes:", len(payload["nodes"]))
r = requests.post(f"{N8N_URL}/api/v1/workflows", headers=headers, json=payload, timeout=60)
print("Status:", r.status_code)
print("Resposta:", r.text[:400])