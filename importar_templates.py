"""
Importador em massa de templates n8n
Lê JSONs das subpastas e importa via API local (localhost:5678)
"""

import requests
import json
import os
import time
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────
BASE_URL  = "http://localhost:5678"
API_KEY   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1YjM0MGE3Yi04YzNiLTRlNzAtYTBjNC0xZmI0MzcyNDNjYmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNTM4YjhjYTQtNzQ1My00ZGVlLTg5Y2MtNjI2NDYyNzBiOTQxIiwiaWF0IjoxNzc4NTI0MzcwfQ.B5rlQHXza_h6DliVLU6ifUYqQk9Vxdv0BHrgyPekDXU"
PASTA     = r"C:\n8n-local\n8n_templates\Novos_templates_para_analisar_e_importar_no_n8n"
HEADERS   = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}
# ──────────────────────────────────────────────────────────

def eh_workflow_valido(data):
    """Verifica se o JSON é um workflow n8n válido."""
    if not isinstance(data, dict):
        return False
    # Formato direto: tem nodes e connections
    if "nodes" in data and "connections" in data:
        return True
    # Formato exportado com chave 'workflow'
    if "workflow" in data and isinstance(data["workflow"], dict):
        wf = data["workflow"]
        if "nodes" in wf and "connections" in wf:
            return True
    return False

def extrair_workflow(data):
    """Extrai o workflow do JSON, normalizando o formato."""
    if "nodes" in data and "connections" in data:
        return data
    if "workflow" in data:
        return data["workflow"]
    return data

def importar_workflow(wf_data, nome_arquivo):
    """Importa um workflow via API do n8n."""
    # Garante que tem nome
    if not wf_data.get("name"):
        wf_data["name"] = Path(nome_arquivo).stem

    payload = {
        "name":        wf_data.get("name", Path(nome_arquivo).stem),
        "nodes":       wf_data.get("nodes", []),
        "connections": wf_data.get("connections", {}),
        "settings":    wf_data.get("settings", {}),
        "staticData":  wf_data.get("staticData"),
    }

    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/workflows",
            headers=HEADERS,
            json=payload,
            timeout=15
        )
        return r.status_code in (200, 201), r.status_code
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("  Importador de Templates n8n")
    print(f"  Pasta: {PASTA}")
    print("=" * 60)

    # Coletar todos os JSONs
    print("\nVarredura de arquivos JSON...")
    todos_jsons = list(Path(PASTA).rglob("*.json"))
    print(f"Total de arquivos .json: {len(todos_jsons)}")

    # Estatísticas por pasta
    por_pasta = {}
    for arq in todos_jsons:
        pasta_pai = arq.parent.name if arq.parent.name != Path(PASTA).name else arq.parent.parent.name
        por_pasta[pasta_pai] = por_pasta.get(pasta_pai, 0) + 1
    print("\nPor repositório:")
    for p, c in sorted(por_pasta.items(), key=lambda x: -x[1]):
        print(f"  {p}: {c}")

    # Validar quais são workflows reais
    print("\nValidando workflows...")
    validos   = []
    invalidos = 0
    for arq in todos_jsons:
        try:
            with open(arq, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            if eh_workflow_valido(data):
                validos.append((arq, extrair_workflow(data)))
            else:
                invalidos += 1
        except Exception:
            invalidos += 1

    print(f"  Válidos para importar: {len(validos)}")
    print(f"  Inválidos/ignorados:   {invalidos}")

    if not validos:
        print("\nNenhum workflow válido encontrado!")
        input("Pressione Enter para sair.")
        return

    # Confirmação
    print(f"\nPronto para importar {len(validos)} workflows.")
    resp = input("Confirmar? (s/n): ").strip().lower()
    if resp != "s":
        print("Cancelado.")
        return

    # Importar
    print(f"\nImportando...")
    ok = erros = 0
    inicio = time.time()

    for i, (arq, wf) in enumerate(validos):
        sucesso, status = importar_workflow(wf, arq.name)
        if sucesso:
            ok += 1
        else:
            erros += 1
            if erros <= 5:
                print(f"  Erro {status}: {arq.name[:60]}")
        if (i + 1) % 500 == 0:
            elapsed = time.time() - inicio
            vel = (i + 1) / elapsed
            restante = (len(validos) - i - 1) / vel
            print(f"  [{i+1}/{len(validos)}] ok={ok} err={erros} | ~{restante/60:.1f} min restantes", flush=True)
        time.sleep(0.05)

    tempo_total = (time.time() - inicio) / 60
    print(f"\n{'='*60}")
    print(f"  CONCLUÍDO em {tempo_total:.1f} minutos!")
    print(f"  Importados: {ok}")
    print(f"  Erros:      {erros}")
    print(f"{'='*60}")
    print("\n⚠️  Lembre de rodar o dedup.py novamente para remover duplicatas!")
    input("\nPressione Enter para sair.")

if __name__ == "__main__":
    main()
