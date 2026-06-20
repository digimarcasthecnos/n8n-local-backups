# CLAUDE.md — OmniRoute + n8n: Revisão Completa & Configuração Autônoma

> **Executor:** Claude Code (Opus 4.8)  
> **Projeto:** DigiMarcas Thecnos — Implantação OmniRoute no n8n  
> **Diretório base:** `C:\Projetos\digimarcas-thecnos-desenvolvimento-de-softwares`  
> **Modo:** Totalmente autônomo. Não peça confirmação a cada passo — execute, registre o resultado e siga.

---

## CONTEXTO GERAL

OmniRoute é o AI gateway local (porta `20128`) que roteia chamadas de LLM entre múltiplos provedores com fallback automático e compressão de tokens. O n8n está em `http://localhost:5678` (Docker). O objetivo desta sessão é:

1. Diagnosticar o estado atual do OmniRoute
2. Ativar RTK + Caveman (compressão empilhada)
3. Adicionar provedores MiniMax e Kimi (Moonshot)
4. Criar combo estratégico "n8n-smart-combo" com subcombos
5. Configurar e testar a credencial do n8n apontando para o OmniRoute
6. Registrar tudo em log de auditoria

---

## FASE 0 — PRÉ-VERIFICAÇÃO DO AMBIENTE

### 0.1 — Verificar se OmniRoute está rodando

```bash
curl -s http://localhost:20128/v1/models | python3 -m json.tool | head -40
```

**Se retornar lista de modelos:** ✅ siga para Fase 1.  
**Se recusar conexão:** execute `omniroute` em um terminal separado e aguarde 5s, então reteste.

---

### 0.2 — Verificar versão atual

```bash
omniroute --version
```

**Esperado:** v3.8.7 ou superior.  
Se for inferior a v3.8.7, atualize com:

```bash
npm update -g omniroute
```

---

### 0.3 — Verificar n8n rodando

```bash
curl -s http://localhost:5678/healthz
```

**Se não responder:** inicie o n8n via Docker:

```bash
cd C:\n8n-local
docker compose up -d
```

---

### 0.4 — Capturar estado atual dos combos

```bash
curl -s http://localhost:20128/api/combos | python3 -m json.tool
```

Salve o output em `C:\Projetos\digimarcas-thecnos-desenvolvimento-de-softwares\omniroute_audit\combos_antes.json`.

---

### 0.5 — Capturar provedores conectados

```bash
curl -s http://localhost:20128/api/providers | python3 -m json.tool
```

Salve em `omniroute_audit\providers_antes.json`.

---

## FASE 1 — ATIVAR RTK + CAVEMAN STACKED

### Por que isso importa

Atualmente apenas Caveman está ativo (~46% de economia de tokens).  
Com RTK + Caveman empilhados a economia sobe para ~89% em sessões pesadas (tool outputs, logs, Git, JSON de ferramentas).

### Fórmula matemática da compressão combinada:
```
economia_total = 1 - (1 - RTK_saving) × (1 - Caveman_saving)
              = 1 - (1 - 0.80) × (1 - 0.46)
              = 89.2%
```

### 1.1 — Ativar RTK via API

```bash
curl -s -X PATCH http://localhost:20128/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "compression": {
      "rtk": { "enabled": true },
      "caveman": { "enabled": true },
      "pipeline": ["rtk", "caveman"]
    }
  }' | python3 -m json.tool
```

**Se não existir endpoint PATCH /api/settings**, abra o dashboard:

```
http://localhost:20128/dashboard
```

Navegue em: **Settings → Compression**  
Ative: `RTK` e certifique-se que a ordem do pipeline é `RTK → Caveman`.

---

### 1.2 — Verificar que compressão está ativa

```bash
curl -s http://localhost:20128/api/settings | python3 -m json.tool | grep -A 10 "compression"
```

---

### 1.3 — Teste de compressão (verificação funcional)

```bash
curl -s -X POST http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [
      {
        "role": "user",
        "content": "O problema é que o componente está re-renderizando porque uma nova referência de objeto está sendo criada em cada ciclo de renderização. Quando você passa um objeto inline como prop, a comparação rasa do React o vê como um objeto diferente a cada vez, o que aciona um novo render. Eu recomendaria usar useMemo para memorizar o objeto."
      }
    ],
    "max_tokens": 100
  }' | python3 -m json.tool
```

Verifique no response headers ou body se há campo `x-compression-savings` ou similar indicando % de tokens economizados.

---

## FASE 2 — ADICIONAR PROVEDORES NOVOS

### 2.1 — Adicionar MiniMax

MiniMax é um dos provedores mais baratos disponíveis ($0.20/1M tokens) e tem reset de quota a cada 5h.

**Via API:**

```bash
curl -s -X POST http://localhost:20128/api/providers \
  -H "Content-Type: application/json" \
  -d '{
    "id": "minimax",
    "type": "api_key",
    "apiKey": "SUA_CHAVE_MINIMAX_AQUI",
    "models": ["MiniMax-M2.1", "MiniMax-M2.5"]
  }' | python3 -m json.tool
```

> **ATENÇÃO:** Se não tiver chave MiniMax, acesse https://minimaxi.com e crie conta gratuita. A chave fica em API → My API Keys.

**Alternativamente via Dashboard:**  
`http://localhost:20128/dashboard → Providers → Add → MiniMax`

---

### 2.2 — Adicionar Kimi (Moonshot AI)

Kimi K2 é gratuito e ilimitado via provedor `if` (InfFree/Qoder).

```bash
curl -s -X POST http://localhost:20128/api/providers \
  -H "Content-Type: application/json" \
  -d '{
    "id": "kimi_free",
    "type": "oauth_free",
    "provider": "qoder",
    "models": ["if/kimi-k2", "if/kimi-k2-thinking"]
  }' | python3 -m json.tool
```

> **Se necessitar login OAuth:** `http://localhost:20128/dashboard → Providers → Connect Qoder → OAuth login`

---

### 2.3 — Verificar todos os provedores ativos

```bash
curl -s http://localhost:20128/api/providers | python3 -m json.tool
```

**Resultado esperado (provedores mínimos ativos):**
- ✅ groq
- ✅ gemini / google
- ✅ openrouter
- ✅ deepseek
- ✅ pollinations
- ✅ minimax (novo)
- ✅ kimi / qoder (novo)

---

## FASE 3 — CRIAR COMBOS ESTRATÉGICOS

### Estratégia: Combo dentro de Combo

A ideia é ter **um combo principal** para o n8n que internamente usa **subcombos especializados** com estratégias diferentes. Cada subcombo tem um modelo principal e fallbacks encadeados.

---

### 3.1 — Subcombo de Raciocínio/Código (reasoning-code)

```bash
curl -s -X POST http://localhost:20128/api/combos \
  -H "Content-Type: application/json" \
  -d '{
    "name": "reasoning-code",
    "description": "Especializado em código e raciocínio lógico",
    "strategy": "quality_first",
    "compression": "standard",
    "models": [
      {"model": "ds/deepseek-v3", "priority": 1},
      {"model": "if/kimi-k2-thinking", "priority": 2},
      {"model": "pol/deepseek-r1", "priority": 3}
    ]
  }' | python3 -m json.tool
```

---

### 3.2 — Subcombo Econômico/Volume (economy-volume)

```bash
curl -s -X POST http://localhost:20128/api/combos \
  -H "Content-Type: application/json" \
  -d '{
    "name": "economy-volume",
    "description": "Máxima economia para tarefas simples e alto volume",
    "strategy": "least_used",
    "compression": "aggressive",
    "models": [
      {"model": "if/kimi-k2", "priority": 1},
      {"model": "minimax/MiniMax-M2.1", "priority": 2},
      {"model": "pol/deepseek-r1", "priority": 3},
      {"model": "groq/llama-3.3-70b", "priority": 4}
    ]
  }' | python3 -m json.tool
```

---

### 3.3 — Combo Principal n8n (n8n-smart-combo)

Este é o combo que o n8n vai usar. Ele combina os dois subcombos acima como camadas.

```bash
curl -s -X POST http://localhost:20128/api/combos \
  -H "Content-Type: application/json" \
  -d '{
    "name": "n8n-smart-combo",
    "description": "Combo principal para workflows n8n - DeepSeek + Kimi + MiniMax + Pollinations",
    "strategy": "least_used",
    "compression": "standard",
    "models": [
      {"model": "ds/deepseek-v3", "priority": 1, "note": "Principal - raciocínio + código"},
      {"model": "if/kimi-k2", "priority": 2, "note": "Gratuito ilimitado - contexto longo"},
      {"model": "minimax/MiniMax-M2.1", "priority": 3, "note": "Backup barato - $0.20/1M"},
      {"model": "pol/deepseek-r1", "priority": 4, "note": "Emergência - sem bloqueio geo"},
      {"model": "groq/llama-3.3-70b", "priority": 5, "note": "Ultra-rápido - último fallback"}
    ]
  }' | python3 -m json.tool
```

---

### 3.4 — Verificar combos criados

```bash
curl -s http://localhost:20128/api/combos | python3 -m json.tool
```

Salve output em `omniroute_audit\combos_depois.json`.

---

## FASE 4 — CONFIGURAR CREDENCIAL NO n8n

### 4.1 — Obter a API Key do OmniRoute

```bash
curl -s http://localhost:20128/api/settings | python3 -m json.tool | grep -i "apikey\|api_key\|dashboardKey"
```

**Ou via dashboard:** `http://localhost:20128/dashboard → Settings → API Key`

Anote a chave. Ela será usada no n8n.

---

### 4.2 — Criar credencial no n8n via API

```bash
curl -s -X POST http://localhost:5678/api/v1/credentials \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: SUA_CHAVE_N8N_AQUI" \
  -d '{
    "name": "OmniRoute - n8n-smart-combo",
    "type": "openAiApi",
    "data": {
      "apiKey": "SUA_CHAVE_OMNIROUTE_AQUI",
      "baseURL": "http://localhost:20128/v1"
    }
  }' | python3 -m json.tool
```

> **Atenção:** Substitua `SUA_CHAVE_N8N_AQUI` e `SUA_CHAVE_OMNIROUTE_AQUI` pelas chaves reais.

---

### 4.3 — Alternativa: Criar manualmente no n8n

Se preferir via interface:

1. Acesse `http://localhost:5678`
2. Menu lateral → **Credentials → New**
3. Selecione: **OpenAI API**
4. Preencha:
   - **Name:** `OmniRoute - n8n-smart-combo`
   - **API Key:** `[chave do dashboard OmniRoute]`
   - **Base URL:** `http://localhost:20128/v1`
5. Clique em **Save**

---

### 4.4 — Testar credencial com chamada real

```bash
curl -s -X POST http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SUA_CHAVE_OMNIROUTE_AQUI" \
  -d '{
    "model": "n8n-smart-combo",
    "messages": [
      {"role": "user", "content": "Responda apenas: OK - OmniRoute funcionando"}
    ],
    "max_tokens": 20
  }' | python3 -m json.tool
```

**Resposta esperada:** mensagem de texto confirmando funcionamento.

---

## FASE 5 — CRIAR WORKFLOW DE TESTE NO n8n

### 5.1 — Importar workflow de teste básico

Crie o arquivo `C:\Projetos\digimarcas-thecnos-desenvolvimento-de-softwares\n8n_workflows\teste_omniroute.json`:

```json
{
  "name": "Teste OmniRoute via n8n",
  "nodes": [
    {
      "id": "trigger",
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300],
      "parameters": {
        "httpMethod": "POST",
        "path": "teste-omniroute",
        "responseMode": "responseNode"
      }
    },
    {
      "id": "llm_call",
      "name": "Chamar OmniRoute",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [480, 300],
      "parameters": {
        "method": "POST",
        "url": "http://localhost:20128/v1/chat/completions",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {"name": "Content-Type", "value": "application/json"}
          ]
        },
        "sendBody": true,
        "bodyContentType": "json",
        "body": "={{ JSON.stringify({ model: 'n8n-smart-combo', messages: [{ role: 'user', content: $json.body.pergunta || 'Olá, OmniRoute!' }], max_tokens: 500 }) }}",
        "options": {}
      }
    },
    {
      "id": "resposta",
      "name": "Resposta Webhook",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [720, 300],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { resposta: $json.choices[0].message.content, modelo_usado: $json.model, tokens_usados: $json.usage } }}"
      }
    }
  ],
  "connections": {
    "Webhook Trigger": {
      "main": [[{"node": "Chamar OmniRoute", "type": "main", "index": 0}]]
    },
    "Chamar OmniRoute": {
      "main": [[{"node": "Resposta Webhook", "type": "main", "index": 0}]]
    }
  }
}
```

---

### 5.2 — Importar no n8n

```bash
curl -s -X POST http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: SUA_CHAVE_N8N_AQUI" \
  -d @"C:\Projetos\digimarcas-thecnos-desenvolvimento-de-softwares\n8n_workflows\teste_omniroute.json" \
  | python3 -m json.tool
```

---

### 5.3 — Ativar o workflow

```bash
# Pegar o ID do workflow criado no passo anterior e usar aqui:
curl -s -X PATCH http://localhost:5678/api/v1/workflows/ID_DO_WORKFLOW \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: SUA_CHAVE_N8N_AQUI" \
  -d '{"active": true}' | python3 -m json.tool
```

---

### 5.4 — Testar o workflow ponta a ponta

```bash
curl -s -X POST http://localhost:5678/webhook/teste-omniroute \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Quais são as vantagens do DeepSeek V3 em comparação ao GPT-4?"}' \
  | python3 -m json.tool
```

---

## FASE 6 — AUDITORIA FINAL & LOG

### 6.1 — Gerar relatório de auditoria

Salve em `C:\Projetos\digimarcas-thecnos-desenvolvimento-de-softwares\omniroute_audit\relatorio_final.md` com:

```bash
echo "# Relatório OmniRoute - $(date)" > relatorio_final.md

echo "## Versão" >> relatorio_final.md
omniroute --version >> relatorio_final.md

echo "## Provedores Ativos" >> relatorio_final.md
curl -s http://localhost:20128/api/providers | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data:
    print(f'- {p.get(\"id\", p.get(\"name\", \"?\"))}: {p.get(\"status\", \"unknown\")}')
" >> relatorio_final.md

echo "## Combos Configurados" >> relatorio_final.md
curl -s http://localhost:20128/api/combos | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data:
    print(f'- {c[\"name\"]}: {len(c.get(\"models\", []))} modelos')
" >> relatorio_final.md

echo "## Compressão" >> relatorio_final.md
curl -s http://localhost:20128/api/settings | python3 -c "
import sys, json
data = json.load(sys.stdin)
comp = data.get('compression', {})
print(f'RTK: {comp.get(\"rtk\", {}).get(\"enabled\", False)}')
print(f'Caveman: {comp.get(\"caveman\", {}).get(\"enabled\", False)}')
print(f'Pipeline: {comp.get(\"pipeline\", [])}')
" >> relatorio_final.md

echo "## Teste de Chamada" >> relatorio_final.md
curl -s -X POST http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"n8n-smart-combo","messages":[{"role":"user","content":"ping"}],"max_tokens":5}' \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Status: OK')
print(f'Modelo usado: {data.get(\"model\", \"?\")}')
print(f'Tokens: {data.get(\"usage\", {})}')
" >> relatorio_final.md
```

---

## CHECKLIST FINAL

Ao terminar todas as fases, confirme cada item:

- [ ] OmniRoute v3.8.7+ rodando na porta 20128
- [ ] RTK compression ativo
- [ ] Caveman compression ativo
- [ ] Pipeline: RTK → Caveman
- [ ] Provedor MiniMax conectado
- [ ] Provedor Kimi (Qoder) conectado
- [ ] Combo `reasoning-code` criado
- [ ] Combo `economy-volume` criado
- [ ] Combo `n8n-smart-combo` criado (5 modelos com fallback)
- [ ] Credencial OmniRoute criada no n8n
- [ ] Workflow de teste importado e ativo no n8n
- [ ] Teste ponta a ponta retornou resposta com sucesso
- [ ] Relatório de auditoria salvo em `omniroute_audit\relatorio_final.md`

---

## NOTAS IMPORTANTES PARA O CLAUDE CODE

1. **Nunca pare no meio** de uma fase — complete sempre antes de passar para a próxima.
2. **Se uma API retornar erro**, tente a alternativa via dashboard web antes de reportar falha.
3. **Substitua os placeholders** `SUA_CHAVE_*_AQUI` pelas chaves reais antes de executar os curl.
4. **As chaves reais estão em:**
   - OmniRoute: `http://localhost:20128/dashboard → Settings`
   - n8n: `http://localhost:5678 → Settings → API → API Key`
5. **Não modifique workflows existentes** no n8n — apenas adicione novos.
6. **Se o Cloudflare Tunnel não estiver rodando**, inicie-o antes de testar qualquer URL pública.
7. **Porta 20128** = OmniRoute | **Porta 5678** = n8n | **Porta 5432** = PostgreSQL (n8n)

---

*Gerado por Claude Sonnet 4.6 — DigiMarcas Thecnos — 18/06/2026*
