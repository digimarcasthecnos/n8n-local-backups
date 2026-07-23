# ARQUITETURA COMPLETA — DigiMarcas Thecnos

> **Documento-mestre unificado.** Consolida os 15 chats do projeto (do primeiro template n8n ao pendrive portátil) numa única fonte da verdade, pronta para o **Claude Code** executar de ponta a ponta.

---

## 0. Metadados

| Campo | Valor |
|---|---|
| Projeto | DigiMarcas Thecnos — Infraestrutura de IA local/portátil |
| Responsável | André (Embu-Guaçu, SP) |
| Executor de referência | Claude Code (Opus 4.8) + Claude Sonnet 4.6 |
| Documento gerado em | 22/07/2026 |
| Versão da arquitetura | **v2 (com mesclagem combinatória aplicada)** |
| OmniRoute — versão alvo | **v3.8.48** (pendrive) · v3.8.31 (Windows, a atualizar) |
| Ambientes | **3**: Windows nativo (20128) · Docker/n8n (20129) · **Pendrive MX Linux (portátil)** |
| Fonte da verdade | Este arquivo + `omniroute/combos_max_economia_v2.json` |
| Repositório | `github.com/digimarcasthecnos/n8n-local-backups` |

---

## 1. Visão geral

O **OmniRoute** é um *AI gateway* local que roteia chamadas de LLM entre vários provedores com **fallback automático**, **compressão de tokens** (RTK + Caveman) e suporte a 160+ modelos. A filosofia do projeto é a **"Max Economia"**: cada combo começa por um modelo **gratuito** e só desce para modelos pagos quando o de cima falha — mantendo o **custo base em R$ 0** na esmagadora maioria das chamadas.

Existem **três ambientes** que devem ficar **espelhados**:

| Ambiente | Porta | Uso principal | Estado |
|---|---|---|---|
| Windows nativo | 20128 | Claude Code, Cursor, RooCode, Cline, Codex CLI | Concluído (jun/2026) — **a atualizar p/ v2** |
| Docker / n8n | 20129 | Workflows n8n + WhatsApp + Evolution API | Concluído (jun/2026) |
| **Pendrive MX Linux** | — | Réplica portátil de tudo | **Mais evoluído (jul/2026)** — base do v2 |

> **Regra de ouro do projeto:** nunca deixar um modelo *"thinking"* liderar um combo — ele "pensa" até estourar o `max_tokens` e devolve vazio **sem** cair no fallback.

---

## 2. Linha do tempo — os 15 chats em ordem sincronizada

| Fase | # | Chat | O que consolidou |
|---|---|---|---|
| **A — Fundação n8n** | 1 | Extração em massa … Evolution API 1 | n8n + templates + Evolution API (base) |
| | 2 | … Evolution API 2 | Continuação da extração em massa |
| | 3 | … Evolution API 3 | Deduplicação + remap de credenciais |
| | 4 | … Evolution API 4 | Evolution API + WhatsApp (500 msgs) |
| | 5 | … Evolution API 5 | 1ª configuração do OmniRoute |
| **B — Gateway OmniRoute** | 6 | Implementar OmniRoute no n8n | Nasce a arquitetura (relatório-mestre) |
| | 7 | Ferramentas disponíveis no n8n | 87 skills/MCP + nós disponíveis |
| **C — Agentes & IDEs** | 8 | Instalando Codex no Claude Code | Codex CLI + Claude Code |
| | 9 | Instalar múltiplas IDEs no Opensquad | Cursor, RooCode, Cline, Continue.dev |
| | 10 | Codex vs Claude Code para OpenClaw | Escolha de executor por fase |
| | 11 | Skills p/ OpenClaw (admin. empresarial) | Time de agentes administrativos |
| **D — Organização & validação** | 12 | Organizando projeto antes de executar | Estrutura de pastas/repos |
| | 13 | Setup validation strategy | Estratégia de validação |
| **E — Infra portátil** | 14 | Criar pendrive bootável MX Linux live 1 | Pendrive + CLIs + Docker/n8n/Evolution |
| | 15 | Criar pendrive bootável MX Linux live 2 | 9 provedores + 10 combos + SSH + clone |

---

## 3. Estado atual de cada ambiente

| Item | Windows/Docker (jun/2026) | Pendrive (jul/2026) | Fonte da verdade v2 |
|---|---|---|---|
| Versão OmniRoute | v3.8.31 / v3.8.7 | **v3.8.48** | v3.8.48 |
| Provedores | 9 (+ Antigravity 10º) | 9 (6 API + 3 OAuth) | 9 (Antigravity opcional) |
| sub-gratis | 3 modelos mortos ☠️ | **6/6 validados** | Pendrive |
| sub-barato | tem `minimax-m2.5` | 5 modelos | **Mesclar → 6** |
| sub-codex | `gh/gpt-5-mini` | 7/7 (Luna low) | Pendrive |
| sub-premium | 4 modelos (opus-4-7) | **6, 3+3 até opus-4-8** | Pendrive |
| Combos centrais | 3 (faltam 3) | **6 completos** | Pendrive |
| Compressão | RTK+Caveman | RTK+Caveman | Idêntica |

**Conclusão:** o **pendrive é a base** do v2. O Windows/Docker importa deste documento e do `combos_max_economia_v2.json`.

---

## 4. Provedores (9 conectados)

### 4.1 Via API Key (6)

| # | Provedor | Modelos | Observação |
|---|---|---|---|
| 1 | Groq | 17 | Rápido; catálogo gira (validar modelos) |
| 2 | Gemini (Google AI Studio) | 56 | Cota gratuita alta (1500 req/dia) |
| 3 | Cohere | 20 | Chave trial — rate limit apertado |
| 4 | Mistral | 60 | Codestral/Devstral/Small nativos |
| 5 | DeepSeek | 2 | Pré-pago (manter saldo) |
| 6 | OpenRouter | 339 | Roteia centenas de modelos |

### 4.2 Via OAuth (3)

| # | Provedor | Prefixo | Observação |
|---|---|---|---|
| 7 | Codex / OpenAI | `cx/` | Assinatura — janela de limite ~5h |
| 8 | Claude | `cc/` | Habilita até `claude-opus-4-8` sem custo de API |
| 9 | GitHub Copilot | `gh/` | 22/22 modelos ativos na v3.8.48 |

### 4.3 Candidatos (não conectados — seção de modernização)

- **Antigravity** (10º, OAuth Google) — modelos preview/free; opcional.
- **Ollama** (provedor local) — útil para rodar modelos offline no pendrive.

> **Chaves de API:** ficam em `~/.minhas_chaves.env` (fora do Git). A chave OpenRouter válida é a `OPENROUTER_API_KEY`; variantes antigas (`_N8N`, `_WSL`…) podem estar revogadas — **não usar**.

---

## 5. Arquitetura de combos — fonte da verdade **v2**

Estratégia de todos: **Prioridade** (fallback sequencial: tenta o 1º; só desce em falha).

### 5.1 Subcombos (blocos de construção)

**`sub-gratis`** — cascata 100% gratuita (validado 6/6):

| # | Modelo | Provedor |
|---|---|---|
| 1 | gemini-2.5-flash | Gemini |
| 2 | gemini-2.5-flash-lite | Gemini |
| 3 | command-r (Aug 2024) | Cohere |
| 4 | llama-3.3-70b | Groq |
| 5 | nemotron-3-super-120b-a12b:free | OpenRouter |
| 6 | qwen3.6-27b | Groq |

**`sub-barato`** — degrau barato **(v2 — com MiniMax mesclado, 6 modelos)**:

| # | Modelo | Provedor | Nota |
|---|---|---|---|
| 1 | kimi-k2-0905 | OpenRouter | |
| 2 | **minimax-m2.5** | OpenRouter | **← Ação 1 (mesclagem)** |
| 3 | deepseek-v3.2-exp | OpenRouter | |
| 4 | kimi-k2 | OpenRouter | |
| 5 | deepseek-v4-flash | DeepSeek (`ds/` direto) | manter saldo |
| 6 | mistral-small-4 | Mistral | |

**`sub-codex`** — especialistas em código (validado 7/7):

| # | Modelo | Provedor |
|---|---|---|
| 1 | codestral-latest | Mistral |
| 2 | devstral-latest | Mistral |
| 3 | deepseek-v3.2-exp | OpenRouter |
| 4 | qwen3.6-27b | Groq |
| 5 | nemotron-3-super:free | OpenRouter |
| 6 | gpt-5.6-luna-low | Codex (`cx/`) |
| 7 | claude-sonnet-4-6 | Claude Code (`cc/`) |

**`sub-premium`** — 3+3 intercalado (desenho do André; validado 6/6):

| # | Modelo | Assinatura | Nível |
|---|---|---|---|
| 1 | gpt-5.6-luna-low | OpenAI `cx/` | Leve |
| 2 | claude-haiku-4-5 | Claude `cc/` | Leve |
| 3 | gpt-5.6-terra-low | OpenAI `cx/` | Médio |
| 4 | claude-sonnet-4-6 | Claude `cc/` | Médio |
| 5 | gpt-5.6-sol-low | OpenAI `cx/` | Topo |
| 6 | claude-opus-4-8 | Claude `cc/` | Topo |

### 5.2 Combos centrais (referenciam subcombos via COMBO REF)

| Combo | Composição (v2) | Público |
|---|---|---|
| `n8n-smart-combo` | sub-gratis → sub-barato → sub-codex → **sub-premium** ← *Ação 2* | Workflows n8n |
| `claude-code-combo` | sub-codex → sub-premium | Claude Code CLI |
| `reasoning-code` | sub-codex → sub-barato → sub-premium | Código pesado |
| `cursor-combo` | sub-codex → sub-gratis | IDEs (Cursor etc.) |
| `economy-volume` | sub-gratis → sub-barato | Alto volume, custo mínimo |
| `openclaw-free` | sub-gratis | OpenClaw / agentes free |

> **Ação 3 — DECIDIDA:** `economy-volume` **fica SEM** `sub-premium`. Motivo técnico: proteger a cota premium (janela ~5h) de ser drenada em volume alto; manter o propósito "burro de carga barato" limpo; a rede de segurança completa já vive no `n8n-smart-combo` (que ganhou premium na Ação 2). Decisão validada — é também o estado mais refinado (a versão antiga do Windows tinha premium aqui; o pendrive já havia removido).

---

## 6. Compressão RTK + Caveman

Ativar **apenas** RTK + Caveman (nem todos os motores!). Economia empilhada ≈ **89%**.

- RTK = modo `minimal` · Caveman = modo `lite`
- Interruptor mestre **"Prompt Compression"** ligado → conferir `Effective pipeline: runs: rtk → caveman`
- Endpoint: `PUT /api/settings/compression`

---

## 7. Skills / MCP & Mídia (vivem 100% dentro do OmniRoute)

**MCP nativo:** `/api/mcp/stream` — **87 ferramentas** em 30 escopos (roteamento, cota, memória, saúde).

```
claude mcp add omniroute --type http --url http://localhost:20128/api/mcp/stream
```

**Endpoints de mídia:**

| Tipo | Endpoint | Providers |
|---|---|---|
| Imagem | `/v1/images/generations` | DALL-E, Pollinations, ComfyUI… |
| Vídeo | `/v1/video/generations` | AnimateDiff, KIE |
| Música | `/v1/music/generations` | Stable Audio, MusicGen |
| Voz (TTS) | `/v1/audio/speech` | ElevenLabs, Coqui, Qwen3 |
| Transcrição (STT) | `/v1/audio/transcriptions` | Whisper, Groq (grátis!) |

---

## 8. Integração n8n

1. **Credencial** no n8n: tipo *OpenAI API*, Base URL `http://172.17.0.1:20128/v1` (ou `http://omniroute:20128/v1` no Docker), chave = agente Bearer do OmniRoute.
2. **Import dos 16.494 workflows** do repositório (`backups/`) usando os scripts já prontos: `importar_templates.py` / `2_corrigir_e_importar.py` / `ativar_workflows.py`.
3. Validar workflow de teste ponta-a-ponta.

---

## 9. Evolution API / WhatsApp

- Stack: Docker + PostgreSQL + Evolution API (já no pendrive).
- Criar **1ª instância** + gerar **QR Code** (doc de referência: `CLAUDE-EVOL-QRCODE.md` no repositório).
- Workflow autoresponder com menu de serviços da DigiMarcas Thecnos.

---

## 10. Segurança — rotação de segredos

| Prioridade | Itens |
|---|---|
| **P1 (crítico)** | n8n JWT, Slack, Google OAuth, Supabase, senha de gestão OmniRoute (2 instâncias) |
| **P2 (providers)** | OpenRouter, Groq, Cohere, Mistral, Gemini, DeepSeek (script) |
| **P3 (outros)** | Anthropic, OpenAI, Pinecone, Notion, ngrok, chave de agente OmniRoute |

> Credenciais expostas em históricos devem ser tratadas como **comprometidas**.

---

## 11. Plano de execução Claude Code (do início ao fim)

Roteiro para o Claude Code rodar na máquina/pendrive. Cada passo tem verificação.

**Passo 0 — Pré-checagem**
- Confirmar OmniRoute no ar (`http://localhost:PORTA/v1/models` retorna lista).
- Confirmar `~/.minhas_chaves.env` carregado.

**Passo 1 — Mesclagem v2 dos combos**
- Ação 1: adicionar `minimax-m2.5` (OpenRouter) na **2ª posição** do `sub-barato`.
- Ação 2: adicionar `sub-premium` como **4ª referência** do `n8n-smart-combo`.
- Ação 3: `economy-volume` — **manter SEM premium** (decidido; ver seção 5.2). Nenhuma edição necessária neste combo.
- Testar os combos afetados (`sub-barato`, `n8n-smart-combo`).

**Passo 2 — Gerar `combos_max_economia_v2.json`**
- Exportar a configuração final dos 10 combos.
- Salvar em `omniroute/combos_max_economia_v2.json`.

**Passo 3 — Espelhar Windows/Docker ← v2**
- Recriar (não copiar arquivos) os combos v2 nas instâncias 20128 e 20129 via export/import.
- Conferir paridade (mesmos 10 combos, mesma ordem).

**Passo 4 — Import dos workflows no n8n do pendrive**
- Rodar scripts de importação → 16.494 workflows.
- Ativar e validar.

**Passo 5 — Credencial OmniRoute no n8n**
- Criar credencial + workflow de teste.

**Passo 6 — Evolution API / WhatsApp**
- 1ª instância + QR Code.

**Passo 7 — Commit & push via SSH**
- `git add` → `git commit` → `git push` (SSH já configurado: `Hi digimarcasthecnos!`).

**Passo 8 — Auditoria final**
- Gerar relatório de status (versão, provedores, combos, compressão, teste de chamada).

---

## 12. Modernizações candidatas (não misturar com o validado)

Seção **separada** — ideias de "última tecnologia" a avaliar **depois** que o v2 estiver 100%:

- Conectar **Antigravity** (10º provedor, via AgentBridge).
- Adicionar **Ollama** local no pendrive (modelos offline).
- **gMCPs** (socket MCP compartilhado) para reduzir memória com várias IDEs.
- **CaveFlow SKILL** (compressão de fluxo de ações) para workflows n8n.
- Revisar líderes de combo conforme novos modelos estáveis surgirem (sempre validando 1º).

---

## 13. Checklist final

**Mesclagem v2**
- [x] Ação 1 — MiniMax no `sub-barato` (via API, testado OK)
- [x] Ação 2 — sub-premium no `n8n-smart-combo` (via API, testado OK)
- [x] Ação 3 — decidido: `economy-volume` SEM premium (nenhuma edição)
- [x] `combos_max_economia_v2.json` gerado (10 combos, commit bf348f548)

**Espelhamento**
- [ ] Windows (20128) atualizado p/ v2 — **pendente** (instância não alcançável a partir do pendrive nesta sessão)
- [ ] Docker/n8n (20129) atualizado p/ v2 — **pendente** (mesmo motivo)
- [ ] Paridade conferida nos 3 ambientes — pendente da mesclagem acima

**n8n / WhatsApp**
- [x] Workflows importados: **16.153 / 16.494 (98%)** — 341 falhas remanescentes são defeitos reais nos templates de origem (nome de nó duplicado, referência a nó inexistente), não corrigíveis automaticamente sem revisão manual
- [x] Credencial OmniRoute criada (`openAiApi`, base URL `http://omniroute:20128/v1` via rede Docker `ia-net`) + workflow de teste ponta-a-ponta validado
- [x] 1ª instância WhatsApp (`digimarcas`) + QR Code — conectada (`state: open`)
- [x] *(extra, não previsto no plano original)* Workflow autoresponder com menu de serviços — criado e ativo; texto do menu é placeholder, aguardando conteúdo real da DigiMarcas Thecnos

**Segurança**
- [ ] Rotação P1 / P2 / P3 — **pendente**; achado durante a execução: `importar_templates.py` e `ativar_workflows.py` têm uma API key do n8n hardcoded (já commitada no histórico do repo) que **não é mais válida** neste n8n do pendrive — candidata a limpeza mesmo sem rotação (chave morta em texto puro no código)

**Versionamento**
- [x] Commit + push via SSH concluído (`bf348f548`, main -> origin/main)

---

*DigiMarcas Thecnos — Arquitetura Completa v2 — Confidencial. Gerado em 22/07/2026. Auditoria de execução: 23/07/2026.*
