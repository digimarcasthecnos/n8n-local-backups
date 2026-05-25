import requests, json, os, time

N8N_URL = "http://localhost:5678"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1YjM0MGE3Yi04YzNiLTRlNzAtYTBjNC0xZmI0MzcyNDNjYmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNTM4YjhjYTQtNzQ1My00ZGVlLTg5Y2MtNjI2NDYyNzBiOTQxIiwiaWF0IjoxNzc4NTI0MzcwfQ.B5rlQHXza_h6DliVLU6ifUYqQk9Vxdv0BHrgyPekDXU"
headers = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}

SETTINGS_OK = {"executionOrder","saveManualExecutions","callerPolicy","errorWorkflow","timezone","saveDataSuccessExecution","saveDataErrorExecution","saveExecutionProgress"}
NODES_OK = {"id","name","type","typeVersion","position","parameters","credentials","disabled","notes","notesInFlow","retryOnFail","maxTries","waitBetweenTries","alwaysOutputData","executeOnce","continueOnFail","onError"}

def fix_settings(s):
    if not isinstance(s, dict):
        return {}
    r = {k:v for k,v in s.items() if k in SETTINGS_OK}
    for b in ["saveManualExecutions", "saveExecutionProgress"]:
        if b in r:
            r[b] = bool(r[b])
    for campo_str in ["saveDataSuccessExecution", "saveDataErrorExecution"]:
        if campo_str in r:
            v = r[campo_str]
            r[campo_str] = "all" if (v is True or v == "all") else "none" if (v is False or v == "none") else str(v)
    if "callerPolicy" in r:
        allowed = {"any", "none", "workflowsFromAList", "workflowsFromSameOwner"}
        if r["callerPolicy"] not in allowed:
            del r["callerPolicy"]
    if "errorWorkflow" in r and not isinstance(r["errorWorkflow"], str):
        del r["errorWorkflow"]
    return r

def fix_node(n):
    if not isinstance(n, dict):
        return n
    r = {k:v for k,v in n.items() if k in NODES_OK}
    if "notes" in r and not isinstance(r["notes"], str):
        r["notes"] = str(r["notes"])
    if "notesInFlow" in r:
        r["notesInFlow"] = bool(r["notesInFlow"])
    if "retryOnFail" in r:
        r["retryOnFail"] = bool(r["retryOnFail"])
    if "id" in r and not isinstance(r["id"], str):
        r["id"] = str(r["id"])
    if "typeVersion" in r:
        try:
            r["typeVersion"] = float(r["typeVersion"])
        except:
            r["typeVersion"] = 1
    if "credentials" in r and not isinstance(r["credentials"], dict):
        del r["credentials"]
    for campo in ["waitBetweenTries", "maxTries"]:
        if campo in r:
            try:
                r[campo] = int(r[campo])
            except:
                del r[campo]
    return r

def fix_nome(nome):
    if not nome or not nome.strip():
        return "Workflow sem nome"
    return nome.strip()[:128]

with open("diagnostico.json", "r", encoding="utf-8") as f:
    diag = json.load(f)

lista = diag.get("para_reimportar", [])
total = len(lista)
ok = err = 0
erros_restantes = []
print(f"Reimportando {total} com correcoes completas...")

for i, caminho in enumerate(lista, 1):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            data = json.load(f)
        outer = data.get("workflow", {})
        actual = outer.get("workflow", {})
        nome = fix_nome(outer.get("name", ""))
        nodes = actual.get("nodes", [])
        if not nodes:
            err += 1
            continue
        payload = {
            "name": nome,
            "nodes": [fix_node(n) for n in nodes],
            "connections": actual.get("connections", {}),
            "settings": fix_settings(actual.get("settings", {}))
        }
        r = requests.post(f"{N8N_URL}/api/v1/workflows", headers=headers, json=payload, timeout=60)
        if r.status_code in [200, 201]:
            ok += 1
        else:
            err += 1
            msg = r.json().get("message", "")
            erros_restantes.append({"arquivo": os.path.basename(caminho), "erro": msg})
            if err <= 5:
                print(f"  ERRO: {msg[:80]}")
        if i % 100 == 0:
            print(f"  {i}/{total} OK:{ok} ERR:{err}")
        time.sleep(0.15)
    except Exception as e:
        err += 1

with open("erros_finais.json", "w", encoding="utf-8") as f:
    json.dump(erros_restantes, f, indent=2, ensure_ascii=False)

print(f"\nConcluido! OK:{ok} ERR:{err}")
print(f"Erros salvos em: erros_finais.json")