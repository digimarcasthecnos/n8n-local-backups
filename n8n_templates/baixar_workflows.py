import cloudscraper
import json
import os
import time

TEMPLATES_DIR = r"H:\Backup\Users\digim\Downloads\n8n_templates_master\n8n_templates"
OUTPUT_DIR = r"H:\Backup\Users\digim\Downloads\n8n_templates_master\n8n_workflows"
os.makedirs(OUTPUT_DIR, exist_ok=True)

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)

arquivos = [f for f in os.scandir(TEMPLATES_DIR) if f.name.endswith(".json")]
total = len(arquivos)
baixados = erros = 0

print(f"Baixando workflows completos de {total} templates...\n")

for i, arquivo in enumerate(arquivos, 1):
    try:
        with open(arquivo.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        template_id = data.get("id")
        if not template_id:
            erros += 1
            continue

        # Verifica se já foi baixado
        output_file = os.path.join(OUTPUT_DIR, f"{template_id}.json")
        if os.path.exists(output_file):
            baixados += 1
            continue

        url = f"https://api.n8n.io/api/templates/workflows/{template_id}"
        response = scraper.get(url, timeout=15)

        if response.status_code == 200:
            workflow_data = response.json()
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            baixados += 1
        else:
            erros += 1

        if i % 100 == 0:
            print(f"{i}/{total} — ✅ {baixados} baixados | ❌ {erros} erros")

        time.sleep(0.5)

    except Exception as e:
        erros += 1

print(f"\nConcluído! ✅ {baixados} | ❌ {erros}")