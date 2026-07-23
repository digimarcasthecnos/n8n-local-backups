# PROMPT DE EXECUÇÃO — Claude Code

> Cole o texto abaixo (a partir de "Você é o Claude Code…") no Claude Code, na raiz do projeto onde estão o `ARQUITETURACOMPLETA.md` e a pasta `omniroute/`. Ele manda o Claude Code executar o projeto do início ao fim, com checkpoints.

---

Você é o Claude Code, executor técnico do projeto **DigiMarcas Thecnos**. Sua tarefa é implementar a **Arquitetura Completa v2** de ponta a ponta.

## Fonte da verdade

Leia **primeiro e por inteiro** o arquivo `ARQUITETURACOMPLETA.md` desta pasta. Ele é a especificação oficial. A configuração de combos alvo está descrita na **seção 5** e deve ser exportada para `omniroute/combos_max_economia_v2.json`.

## Ambiente

- OmniRoute **v3.8.48** rodando localmente (pendrive MX Linux; portas: pendrive local, Windows 20128, Docker/n8n 20129).
- Chaves de API em `~/.minhas_chaves.env` (já existe; **nunca** imprima os valores das chaves, só use).
- SSH do GitHub já configurado (`Hi digimarcasthecnos!`). Repositório: `git@github.com:digimarcasthecnos/n8n-local-backups.git`.

## Regras invioláveis

1. **Regra de ouro:** nunca deixe um modelo *"thinking"* liderar um combo (ele estoura tokens e devolve vazio sem cair no fallback).
2. **Estratégia de todo combo:** *Prioridade* (fallback sequencial).
3. **Nunca exponha** conteúdo de chaves/segredos no output ou em commits.
4. **Teste cada combo** afetado após editar; se um degrau falhar por *timeout* ou janela de limite, **reteste uma vez** antes de concluir que há defeito.
5. **Não copie arquivos de banco** entre instâncias — espelhamento é por **recriação** (export/import de config).
6. **Modo automático:** execute os passos reversíveis (0, 1, 2, 4, 5, 6, 8) **em sequência, sem parar**. **Pare e peça confirmação APENAS** nos 3 pontos irreversíveis: **(a)** qualquer `git push`; **(b)** qualquer rotação de segredo (seção 10); **(c)** antes de alterar as instâncias Windows/Docker (Passo 3). Fora esses, siga adiante sozinho, reportando o resultado de cada passo.

## Execução (siga o "Plano de execução" da seção 11 do MD)

**Passo 0 — Pré-checagem.** Confirme OmniRoute no ar (`/v1/models` retorna lista) e `~/.minhas_chaves.env` carregado. Reporte o status.

**Passo 1 — Mesclagem v2 dos combos.**
- Ação 1: adicionar `minimax-m2.5` (OpenRouter) na **2ª posição** do `sub-barato`.
- Ação 2: adicionar `sub-premium` como **4ª referência** do `n8n-smart-combo`.
- Ação 3: `economy-volume` **fica SEM** premium — nenhuma edição.
- Teste `sub-barato` e `n8n-smart-combo`. Reporte o placar (degraus OK/erro).

**Passo 2 — Gerar `omniroute/combos_max_economia_v2.json`** com os 10 combos finais.

**Passo 3 — Espelhar Windows (20128) e Docker/n8n (20129) para o v2** por recriação (export/import). Confira paridade: mesmos 10 combos, mesma ordem. *(Peça confirmação antes de tocar nessas instâncias.)*

**Passo 4 — Importar os 16.494 workflows** no n8n do pendrive usando os scripts do repositório (`importar_templates.py` / `2_corrigir_e_importar.py` / `ativar_workflows.py`). Reporte quantos importaram/ativaram.

**Passo 5 — Credencial OmniRoute no n8n** (tipo OpenAI API, Base URL do gateway, chave de agente Bearer) + workflow de teste ponta-a-ponta.

**Passo 6 — Evolution API / WhatsApp:** criar 1ª instância + gerar QR Code (referência: `CLAUDE-EVOL-QRCODE.md`).

**Passo 7 — Commit & push via SSH.** *(Peça confirmação antes do push.)* Mensagem sugerida: `feat: arquitetura v2 (mesclagem combinatória) + combos_max_economia_v2`.

**Passo 8 — Auditoria final.** Gere um relatório curto: versão, provedores ativos, 10 combos, compressão, e 1 teste de chamada por combo central. Atualize o checklist da seção 13 do MD.

## Formato de resposta

Execute os passos reversíveis **em sequência, sem parar**, reportando ao final de cada um: **o que fez** e **o resultado do teste** (placar OK/erro). **Só interrompa e aguarde meu "ok"** nos 3 pontos irreversíveis: **push** (Passo 7), **rotação de segredos** (seção 10) e **alterar Windows/Docker** (Passo 3).

Comece agora pelo **Passo 0** e siga direto até o Passo 2; pare no Passo 3 para eu confirmar o espelhamento das outras instâncias.
