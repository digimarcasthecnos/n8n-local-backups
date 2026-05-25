python -c "
import cloudscraper, json, os

TEMPLATES_DIR = r'H:\Backup\Users\digim\Downloads\n8n_templates_master\n8n_templates'
WORKFLOWS_DIR = r'H:\Backup\Users\digim\Downloads\n8n_templates_master\n8n_workflows'

scraper = cloudscraper.create_scraper(browser={'browser':'chrome','platform':'windows','mobile':False})

ids_baixados = {f.name.replace('.json','') for f in os.scandir(WORKFLOWS_DIR) if f.name.endswith('.json')}
ids_faltando = []
for arquivo in os.scandir(TEMPLATES_DIR):
    if not arquivo.name.endswith('.json'): continue
    with open(arquivo.path,'r',encoding='utf-8') as f:
        data = json.load(f)
    tid = str(data.get('id',''))
    if tid and tid not in ids_baixados:
        ids_faltando.append(tid)

print('Testando primeiros 5...')
for tid in ids_faltando[:5]:
    url = f'https://api.n8n.io/api/templates/workflows/{tid}'
    r = scraper.get(url, timeout=15)
    print(f'ID {tid}: Status {r.status_code} - {r.text[:80]}')
"