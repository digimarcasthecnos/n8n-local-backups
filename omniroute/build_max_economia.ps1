$ErrorActionPreference = "Stop"
$base = "C:\Projetos\digimarcas-thecnos-desenvolvimento-de-softwares\omniroute_audit"
$jwt = ((Get-Content "$base\.omni_cookie" -Raw).Trim()) -replace '^auth_token=',''
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.Cookies.Add((New-Object System.Net.Cookie("auth_token",$jwt,"/","localhost")))
$U = "http://localhost:20129/api/combos"

# limpa tudo
$existing = (Invoke-RestMethod -Uri $U -WebSession $session -TimeoutSec 15).combos
foreach($c in $existing){ try { Invoke-RestMethod -Uri "$U/$($c.id)" -Method Delete -WebSession $session -TimeoutSec 10 | Out-Null; Write-Output "deletado: $($c.name)" } catch {} }

function New-Combo($name,$desc,$models){
  $payload = @{ name=$name; description=$desc; strategy="priority"; models=$models } | ConvertTo-Json -Depth 8
  try { $r = Invoke-RestMethod -Uri $U -Method Post -WebSession $session -ContentType "application/json" -Body $payload -TimeoutSec 25; Write-Output ("CRIADO: {0,-16} membros={1}" -f $r.name,$r.models.Count) }
  catch { $resp=$_.Exception.Response; if($resp){$sr=New-Object System.IO.StreamReader($resp.GetResponseStream());Write-Output ("ERRO {0}: HTTP{1} {2}" -f $name,[int]$resp.StatusCode,$sr.ReadToEnd())}else{Write-Output ("ERRO {0}: {1}" -f $name,$_.Exception.Message)} }
}
function M($m){ @{ model=$m } }
function C($n){ @{ kind="combo-ref"; comboName=$n } }

# ===== REGRA DE OURO (max economia): GRATIS -> OpenRouter(barato) -> Codex/Copilot -> Claude(OAuth) =====

# Camada 1: CUSTO ZERO (nada ganha de $0; sempre lidera)
New-Combo "sub-gratis" "Custo ZERO: free-tier flash-lite + Cohere + Groq + gpt-oss free + Gemini AI Studio" @(
  (M "antigravity/gemini-3.1-flash-lite"),
  (M "cohere/command-r-08-2024"),
  (M "groq/qwen/qwen3-32b"),
  (M "groq/llama-3.3-70b-versatile"),
  (M "openrouter/openai/gpt-oss-120b:free"),
  (M "antigravity/gemini-3-flash-preview"),
  (M "gemini/gemini-2.0-flash")
)

# Camada 2: PAGO-BARATO com OpenRouter LIDERANDO (regra do usuario). DeepSeek nativo fica de reserva atras.
New-Combo "sub-barato" "Pago barato OpenRouter-first: Kimi K2 -> MiniMax -> DeepSeek(OR) -> Kimi K2 base -> DeepSeek nativo(reserva) -> Mistral Small" @(
  (M "openrouter/moonshotai/kimi-k2-0905"),
  (M "openrouter/minimax/minimax-m2.5"),
  (M "openrouter/deepseek/deepseek-v3.2-exp"),
  (M "openrouter/moonshotai/kimi-k2"),
  (M "deepseek/deepseek-v4-flash"),
  (M "mistral/mistral-small-latest")
)

# Camada 3: CODIGO economico (codigo barato primeiro; premium de codigo no fim)
# NOTA: gh/gpt-5.3-codex existe no catalogo mas o token Copilot NAO o expoe (HTTP400). So gh/gpt-5-mini funciona via Copilot.
New-Combo "sub-codex" "Codigo economico: Codestral -> Devstral -> DeepSeek(OR) -> Qwen3 -> gpt-oss free -> GPT-5-mini(Copilot) -> Claude Sonnet" @(
  (M "mistral/codestral-latest"),
  (M "mistral/devstral-latest"),
  (M "openrouter/deepseek/deepseek-v3.2-exp"),
  (M "groq/qwen/qwen3-32b"),
  (M "openrouter/openai/gpt-oss-120b:free"),
  (M "gh/gpt-5-mini"),
  (M "cc/claude-sonnet-4-6")
)

# Camada 4: PREMIUM PAGO (rotas nativas baratas: GPT-5-mini via Copilot + Claude via OAuth). Topo do fallback.
# NOTA: cc/claude-opus-4-8 indisponivel nesse plano; opus-4-7 e o topo que funciona.
New-Combo "sub-premium" "Premium nativo-barato: GPT-5-mini (Copilot) -> Claude Haiku -> Sonnet -> Opus 4.7 (OAuth)" @(
  (M "gh/gpt-5-mini"),
  (M "cc/claude-haiku-4-5-20251001"),
  (M "cc/claude-sonnet-4-6"),
  (M "cc/claude-opus-4-7")
)

# ===== COMBOS CENTRAIS (cada estrategia desce ate o premium = cobertura total) =====
New-Combo "n8n-smart-combo" "PRINCIPAL/COMPLETO: gratis -> barato(OR) -> codex -> premium (Claude+Codex). Cascata economica total." @(
  (C "sub-gratis"), (C "sub-barato"), (C "sub-codex"), (C "sub-premium")
)
New-Combo "reasoning-code" "CODIGO: codex -> barato(OR) -> premium (Codex+Claude no topo)." @(
  (C "sub-codex"), (C "sub-barato"), (C "sub-premium")
)
New-Combo "economy-volume" "VOLUME/custo minimo: gratis -> barato(OR) -> premium (so sobe se tudo falhar)." @(
  (C "sub-gratis"), (C "sub-barato"), (C "sub-premium")
)

Write-Output ""
Write-Output "=== ESTRUTURA FINAL ==="
$all = (Invoke-RestMethod -Uri $U -WebSession $session -TimeoutSec 15).combos
foreach($c in ($all | Sort-Object name)){
  $kinds = $c.models | ForEach-Object { if($_.kind -eq "combo-ref"){"[combo:$($_.comboName)]"}else{$_.model} }
  "{0,-16}: {1}" -f $c.name, ($kinds -join " > ")
}
