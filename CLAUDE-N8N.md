# CLAUDE-N8N.md — Configuração MCP n8n para Claude Desktop

> Instruções completas para o Claude Code configurar o MCP do n8n no Claude Desktop (Windows 11).
> Execute todas as tarefas em sequência, verificando cada resultado antes de prosseguir.

---

## Ambiente

- **Usuário:** `digim` | Máquina: VXpro
- **Config MSIX (caminho correto):** `C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`
- **Config padrão (secundário):** `C:\Users\digim\AppData\Roaming\Claude\claude_desktop_config.json`
- **Node.js:** `C:\Program Files\nodejs\node.exe` (v24.14.1)
- **Script MCP correto:** `C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\stdio-wrapper.js`
- **n8n API:** `https://n8n.digimarcasthecnos.com/api/v1`
- **Repositório n8n-mcp:** https://github.com/czlonkowski/n8n-mcp

---

## TAREFA 1 — Recuperar API Key do n8n

Tente extrair a API Key de qualquer config existente:

```powershell
# Tentar caminho MSIX primeiro
$msixPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json"
$stdPath  = "C:\Users\digim\AppData\Roaming\Claude\claude_desktop_config.json"

foreach ($p in @($msixPath, $stdPath)) {
    if (Test-Path $p) {
        Set-ItemProperty $p -Name IsReadOnly -Value $false -ErrorAction SilentlyContinue
        $raw = Get-Content $p -Raw -ErrorAction SilentlyContinue
        Write-Host "=== $p ===" 
        Write-Host $raw
    }
}
```

Identifique o valor de `N8N_API_KEY` nos arquivos acima.
Se não houver nenhum arquivo com a key, acesse `http://localhost:5678/settings/api` no navegador para gerar uma nova.

---

## TAREFA 2 — Verificar pré-requisitos

```powershell
# Node.js
& "C:\Program Files\nodejs\node.exe" --version

# Script stdio-wrapper existe?
Test-Path "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\stdio-wrapper.js"

# Cloudflare
Get-Service Cloudflared | Select-Object Name, Status, StartType

# Docker/n8n
docker ps --filter "name=n8n_app" --format "{{.Names}}: {{.Status}}"

# n8n acessível
Invoke-WebRequest -Uri "https://n8n.digimarcasthecnos.com/healthz" -UseBasicParsing | Select-Object StatusCode
```

Se `stdio-wrapper.js` não existir: `npm install -g n8n-mcp`
Se Cloudflare parado: `Start-Service Cloudflared; Set-Service Cloudflared -StartupType Automatic`

---

## TAREFA 3 — Validar API Key

Substitua `SUA_KEY_AQUI` pela key encontrada na Tarefa 1:

```powershell
$key = "SUA_KEY_AQUI"
try {
    $r = Invoke-RestMethod -Uri "https://n8n.digimarcasthecnos.com/api/v1/workflows?limit=1" `
         -Headers @{"X-N8N-API-KEY"=$key} -Method GET
    Write-Host "API Key VALIDA - workflows encontrados: $($r.data.Count)"
} catch {
    Write-Host "API Key INVALIDA ou n8n inacessivel: $($_.Exception.Message)"
}
```

---

## TAREFA 4 — Escrever config JSON correto

**IMPORTANTE:** Use este método de escrita direta com here-string para evitar JSON inválido.
Substitua `SUA_KEY_AQUI` pela key validada na Tarefa 3.

```powershell
$apiKey = "SUA_KEY_AQUI"

$json = @"
{
  "mcpServers": {
    "n8n-DigiMarcas": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": ["C:\\Users\\digim\\AppData\\Roaming\\npm\\node_modules\\n8n-mcp\\dist\\mcp\\stdio-wrapper.js"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "https://n8n.digimarcasthecnos.com/api/v1",
        "N8N_API_KEY": "$apiKey"
      }
    }
  },
  "preferences": {
    "remoteToolsDeviceName": "digimarcas-thecnos",
    "coworkWebSearchEnabled": true,
    "coworkScheduledTasksEnabled": true,
    "ccdScheduledTasksEnabled": true
  }
}
"@

# Validar que o JSON gerado é válido ANTES de salvar
try {
    $null = $json | ConvertFrom-Json
    Write-Host "JSON valido!"
} catch {
    Write-Host "ERRO: JSON invalido - $($_.Exception.Message)"
    exit 1
}

# Salvar nos dois caminhos
$paths = @(
    "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json",
    "C:\Users\digim\AppData\Roaming\Claude\claude_desktop_config.json"
)

foreach ($path in $paths) {
    $dir = Split-Path $path
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
    Set-ItemProperty $path -Name IsReadOnly -Value $false -ErrorAction SilentlyContinue
    [System.IO.File]::WriteAllText($path, $json, [System.Text.UTF8Encoding]::new($false))
    Set-ItemProperty $path -Name IsReadOnly -Value $true
    Write-Host "Salvo e protegido: $path"
    
    # Verificar
    $verify = Get-Content $path -Raw | ConvertFrom-Json
    Write-Host "  -> mcpServers presente: $($null -ne $verify.mcpServers)"
    Write-Host "  -> API Key presente: $($verify.mcpServers.'n8n-DigiMarcas'.env.N8N_API_KEY.Length -gt 10)"
}
```

---

## TAREFA 5 — Fechar Claude Desktop corretamente

```powershell
# Fechar pelo processo (sem force para não travar)
Get-Process -Name "claude" -ErrorAction SilentlyContinue | ForEach-Object {
    $_.CloseMainWindow() | Out-Null
}
Start-Sleep 3

# Verificar se fechou
$procs = Get-Process -Name "claude" -ErrorAction SilentlyContinue
if ($procs) {
    Write-Host "Processos ainda rodando: $($procs.Count) - forcando encerramento"
    $procs | Stop-Process -Force
    Start-Sleep 2
} else {
    Write-Host "Claude Desktop fechado com sucesso"
}
```

---

## TAREFA 6 — Verificar logs após reabrir

Reabra o Claude Desktop MANUALMENTE (não via script para evitar travamento).
Abra um novo chat e aguarde 15 segundos. Depois execute:

```powershell
$logPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\logs\mcp-server-n8n-DigiMarcas.log"

if (Test-Path $logPath) {
    Get-Content $logPath -Tail 20
} else {
    Write-Host "Log nao encontrado - Claude Desktop ainda nao carregou o MCP"
}
```

**Sucesso esperado:**
```
[info] Server started and connected successfully
[info] Message from server: {"tools":[...
```

**Falha:**
```
Server transport closed unexpectedly
Server disconnected
```

---

## TAREFA 7 — Diagnóstico se ainda falhar

```powershell
# Testar stdio-wrapper diretamente
$configPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json"
$cfg = Get-Content $configPath -Raw | ConvertFrom-Json

$env:MCP_MODE = "stdio"
$env:LOG_LEVEL = "debug"
$env:N8N_API_URL = $cfg.mcpServers.'n8n-DigiMarcas'.env.N8N_API_URL
$env:N8N_API_KEY = $cfg.mcpServers.'n8n-DigiMarcas'.env.N8N_API_KEY

New-Item -ItemType Directory -Force "C:\temp" | Out-Null

$proc = Start-Process `
    -FilePath "C:\Program Files\nodejs\node.exe" `
    -ArgumentList "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\stdio-wrapper.js" `
    -RedirectStandardOutput "C:\temp\mcp-stdout.txt" `
    -RedirectStandardError "C:\temp\mcp-stderr.txt" `
    -NoNewWindow -PassThru

Start-Sleep 12

if (!$proc.HasExited) {
    Write-Host "Processo ainda rodando apos 12s - isso e POSITIVO (servidor aguardando stdin)"
    $proc.Kill()
} else {
    Write-Host "Processo encerrou em menos de 12s - possivel erro"
}

Write-Host "=== STDOUT ==="
Get-Content "C:\temp\mcp-stdout.txt" -ErrorAction SilentlyContinue
Write-Host "=== STDERR ==="
Get-Content "C:\temp\mcp-stderr.txt" -ErrorAction SilentlyContinue
```

---

## Checklist final

- [ ] `stdio-wrapper.js` existe
- [ ] API Key válida (Tarefa 3 retornou "VALIDA")
- [ ] JSON salvo com `[System.IO.File]::WriteAllText` (sem BOM, sem aspas simples)
- [ ] Ambos os caminhos salvos e read-only
- [ ] Cloudflare Running e Automatic
- [ ] Docker n8n Up
- [ ] Log mostra "Server started and connected successfully"
