import cloudscraper
import json
import time
import os

# Configurações
OUTPUT_DIR = "n8n_templates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)

page = 1
total = 0

print("🚀 Iniciando download dos templates n8n...\n")

while True:
    url = f"https://api.n8n.io/api/templates/search?page={page}&rows=50"

    try:
        response = scraper.get(url, timeout=15)

        if response.status_code != 200:
            print(f"❌ Erro HTTP {response.status_code} na página {page}. Encerrando.")
            break

        data = response.json()
        workflows = data.get("workflows", [])

        if not workflows:
            print(f"\n✅ Fim! Todos os templates baixados.")
            break

        for wf in workflows:
            wf_id  = wf.get("id", f"sem_id_{total}")
            wf_name = wf.get("name", "sem_nome")

            # Nome de arquivo seguro
            safe = "".join(c for c in wf_name if c.isalnum() or c in " -_").strip()
            filename = f"{OUTPUT_DIR}/{wf_id}_{safe[:60]}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(wf, f, indent=2, ensure_ascii=False)

            total += 1

        print(f"📄 Página {page} — {total} templates salvos...")
        page += 1
        time.sleep(1.5)  # Respeito ao servidor

    except Exception as e:
        print(f"⚠️ Erro na página {page}: {e}")
        print("Aguardando 10s antes de tentar novamente...")
        time.sleep(10)

print(f"\n🎉 Concluído! Total baixado: {total} templates")
print(f"📁 Salvos em: {os.path.abspath(OUTPUT_DIR)}")