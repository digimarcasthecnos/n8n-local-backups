# CLAUDE-N8N.md — Diagnóstico e Correção Definitiva do MCP n8n

> **Missão:** Investigar a causa raiz da falha constante do MCP n8n-DigiMarcas no Claude Desktop
> e corrigi-la de forma permanente e estável.
>
> Execute TODAS as tarefas em sequência. Não pule etapas. Documente cada resultado.

---

## Ambiente

| Item | Valor |
|------|-------|
| Usuário | `digim` \| Máquina: `VXpro` / `DIGIMARCAS-THECNOS` |
| Config MSIX | `C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json` |
| Config padrão | `C:\Users\digim\AppData\Roaming\Claude\claude_desktop_config.json` |
| Node.js | `C:\Program Files\nodejs\node.exe` (v24.14.1) |
| n8n-mcp bin | `C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\stdio-wrapper.js` |
| n8n local | `http://localhost:5678` |
| n8n público | `https://n8n.digimarcasthecnos.com` |
| Cloudflare | Serviço Windows `Cloudflared` |
| Repositório | https://github.com/czlonkowski/n8n-mcp |

---

## FASE 1 — DIAGNÓSTICO COMPLETO DO ESTADO ATUAL

### 1.1 — Estado dos serviços

```powershell
Write-Host "=== CLOUDFLARE ===" -ForegroundColor Cyan
Get-Service Cloudflared | Select-Object Name, Status, StartType

Write-Host "`n=== DOCKER / N8N ===" -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n=== N8N ACESSIVEL ===" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest "https://n8n.digimarcasthecnos.com/healthz" -UseBasicParsing
    Write-Host "OK: $($r.Content)"
} catch { Write-Host "FALHA: $($_.Exception.Message)" }

Write-Host "`n=== NODE.JS ===" -ForegroundColor Cyan
& "C:\Program Files\nodejs\node.exe" --version

Write-Host "`n=== STDIO-WRAPPER EXISTS ===" -ForegroundColor Cyan
Test-Path "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\stdio-wrapper.js"

Write-Host "`n=== N8N-MCP VERSION ===" -ForegroundColor Cyan
(Get-Content "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\package.json" |
 ConvertFrom-Json).version
```

### 1.2 — Estado do config atual

```powershell
$msixPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json"
$stdPath  = "C:\Users\digim\AppData\Roaming\Claude\claude_desktop_config.json"

foreach ($p in @($msixPath, $stdPath)) {
    Write-Host "`n=== $p ===" -ForegroundColor Yellow
    if (Test-Path $p) {
        $attrs = (Get-Item $p).Attributes
        Write-Host "IsReadOnly: $(($attrs -band [System.IO.FileAttributes]::ReadOnly) -ne 0)"
        Write-Host "Conteudo:"
        Get-Content $p -Raw
    } else {
        Write-Host "NAO EXISTE"
    }
}
```

### 1.3 — Logs do MCP (últimas 50 linhas)

```powershell
$logPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\logs\mcp-server-n8n-DigiMarcas.log"
if (Test-Path $logPath) {
    Write-Host "=== LOG MCP (ultimas 50 linhas) ===" -ForegroundColor Cyan
    Get-Content $logPath -Tail 50
} else {
    Write-Host "Log NAO encontrado em: $logPath" -ForegroundColor Red
    Write-Host "Listando todos os logs disponíveis:"
    Get-ChildItem "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\logs\" -ErrorAction SilentlyContinue
}
```

### 1.4 — Teste direto do stdio-wrapper

```powershell
# Recuperar API Key do config existente
$msixPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json"
$stdPath  = "C:\Users\digim\AppData\Roaming\Claude\claude_desktop_config.json"
$apiKey = $null

foreach ($p in @($msixPath, $stdPath)) {
    if (Test-Path $p) {
        try {
            $cfg = Get-Content $p -Raw | ConvertFrom-Json
            $k = $cfg.mcpServers.'n8n-DigiMarcas'.env.N8N_API_KEY
            if ($k -and $k.Length -gt 20) { $apiKey = $k; break }
        } catch {}
    }
}

if (!$apiKey) {
    Write-Host "API Key NAO encontrada nos configs. Gere uma em http://localhost:5678/settings/api" -ForegroundColor Red
    exit 1
}

Write-Host "API Key encontrada (primeiros 20 chars): $($apiKey.Substring(0,20))..."

# Validar key
try {
    $r = Invoke-RestMethod "https://n8n.digimarcasthecnos.com/api/v1/workflows?limit=1" `
         -Headers @{"X-N8N-API-KEY"=$apiKey}
    Write-Host "API Key VALIDA - $($r.data.Count) workflow(s) retornado(s)" -ForegroundColor Green
} catch {
    Write-Host "API Key INVALIDA ou n8n inacessivel: $($_.Exception.Message)" -ForegroundColor Red
}

# Testar stdio-wrapper com timeout de 15s
Write-Host "`nTestando stdio-wrapper por 15 segundos..." -ForegroundColor Cyan
$env:MCP_MODE = "stdio"
$env:LOG_LEVEL = "debug"
$env:N8N_API_URL = "https://n8n.digimarcasthecnos.com/api/v1"
$env:N8N_API_KEY = $apiKey

New-Item -ItemType Directory -Force "C:\temp" | Out-Null

$proc = Start-Process `
    -FilePath "C:\Program Files\nodejs\node.exe" `
    -ArgumentList "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\stdio-wrapper.js" `
    -RedirectStandardOutput "C:\temp\wrapper-stdout.txt" `
    -RedirectStandardError  "C:\temp\wrapper-stderr.txt" `
    -NoNewWindow -PassThru

Start-Sleep 15

if (!$proc.HasExited) {
    Write-Host "POSITIVO: Processo rodando apos 15s (servidor aguardando stdin)" -ForegroundColor Green
    $proc.Kill()
} else {
    Write-Host "PROBLEMA: Processo encerrou em menos de 15s (exit code: $($proc.ExitCode))" -ForegroundColor Red
}

Write-Host "`n--- STDOUT ---"
Get-Content "C:\temp\wrapper-stdout.txt" -ErrorAction SilentlyContinue
Write-Host "--- STDERR ---"
Get-Content "C:\temp\wrapper-stderr.txt" -ErrorAction SilentlyContinue
```

---

## FASE 2 — INVESTIGAR CAUSA RAIZ

Com base nos resultados da Fase 1, identifique qual cenário se aplica:

### Cenário A: "Server transport closed unexpectedly" em ~2-6 segundos
**Causa provável:** processo node.exe está crashando durante inicialização do stdio-wrapper.
**Investigar:**
```powershell
# Checar se stdio-wrapper é diferente de index.js
Write-Host "=== BIN do pacote ==="
(Get-Content "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\package.json" |
 ConvertFrom-Json).bin

# Tentar rodar com node diretamente e capturar exit code
$env:MCP_MODE = "stdio"; $env:LOG_LEVEL = "debug"
$env:N8N_API_URL = "https://n8n.digimarcasthecnos.com/api/v1"
$env:N8N_API_KEY = $apiKey

$proc = Start-Process `
    -FilePath "C:\Program Files\nodejs\node.exe" `
    -ArgumentList "--trace-uncaught --unhandled-rejections=throw `"C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\stdio-wrapper.js`"" `
    -RedirectStandardOutput "C:\temp\trace-out.txt" `
    -RedirectStandardError  "C:\temp\trace-err.txt" `
    -NoNewWindow -PassThru

Start-Sleep 10
if (!$proc.HasExited) { $proc.Kill() }
Write-Host "EXIT CODE: $($proc.ExitCode)"
Get-Content "C:\temp\trace-out.txt"
Get-Content "C:\temp\trace-err.txt"
```

### Cenário B: Config sendo sobrescrito pelo Claude Desktop
**Causa:** Claude Desktop remove `mcpServers` ao fechar.
**Investigar:**
```powershell
$msixPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json"
$attrs = (Get-Item $msixPath -ErrorAction SilentlyContinue).Attributes
Write-Host "IsReadOnly: $(($attrs -band [System.IO.FileAttributes]::ReadOnly) -ne 0)"
$cfg = Get-Content $msixPath -Raw | ConvertFrom-Json
Write-Host "mcpServers presente: $($null -ne $cfg.mcpServers)"
Write-Host "script correto: $($cfg.mcpServers.'n8n-DigiMarcas'.args[0] -like '*stdio-wrapper*')"
```

### Cenário C: Cloudflare para após reboot
**Causa:** StartupType não é Automatic.
```powershell
Get-Service Cloudflared | Select-Object StartType, Status
```

### Cenário D: n8n-mcp incompatível com Node.js v24
**Causa:** better-sqlite3 ou outro módulo nativo com problema.
```powershell
& "C:\Program Files\nodejs\node.exe" -e "
try {
  require('C:/Users/digim/AppData/Roaming/npm/node_modules/n8n-mcp/node_modules/better-sqlite3');
  console.log('SQLite: OK');
} catch(e) { console.error('SQLite ERRO:', e.message); }
try {
  const w = require('C:/Users/digim/AppData/Roaming/npm/node_modules/n8n-mcp/dist/mcp/stdio-wrapper.js');
  console.log('wrapper carregado OK');
} catch(e) { console.error('wrapper ERRO:', e.message); }
"
```

---

## FASE 3 — CORREÇÃO DEFINITIVA

### 3.1 — Atualizar n8n-mcp para versão mais recente

```powershell
Write-Host "Versao atual:"
(Get-Content "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\package.json" | ConvertFrom-Json).version

Write-Host "Atualizando n8n-mcp..."
npm install -g n8n-mcp@latest

Write-Host "Nova versao:"
(Get-Content "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\package.json" | ConvertFrom-Json).version

Write-Host "stdio-wrapper existe apos update:"
Test-Path "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\stdio-wrapper.js"
```

### 3.2 — Escrever config correto (método robusto)

```powershell
# Recuperar API Key
$msixPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json"
$stdPath  = "C:\Users\digim\AppData\Roaming\Claude\claude_desktop_config.json"
$apiKey = $null

foreach ($p in @($msixPath, $stdPath)) {
    if (Test-Path $p) {
        try {
            Set-ItemProperty $p -Name IsReadOnly -Value $false -ErrorAction SilentlyContinue
            $k = (Get-Content $p -Raw | ConvertFrom-Json).mcpServers.'n8n-DigiMarcas'.env.N8N_API_KEY
            if ($k -and $k.Length -gt 20) { $apiKey = $k; break }
        } catch {}
    }
}

if (!$apiKey) {
    Write-Host "ERRO: API Key nao encontrada. Informe manualmente:" -ForegroundColor Red
    $apiKey = Read-Host "Cole a API Key do n8n"
}

# Montar JSON como here-string (evita ConvertTo-Json que gera aspas simples)
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

# Validar JSON antes de salvar
try {
    $null = $json | ConvertFrom-Json
    Write-Host "JSON valido!" -ForegroundColor Green
} catch {
    Write-Host "ERRO JSON: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Salvar nos dois caminhos sem BOM
$enc = [System.Text.UTF8Encoding]::new($false)
foreach ($path in @($msixPath, $stdPath)) {
    $dir = Split-Path $path
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
    Set-ItemProperty $path -Name IsReadOnly -Value $false -ErrorAction SilentlyContinue
    [System.IO.File]::WriteAllText($path, $json, $enc)
    Set-ItemProperty $path -Name IsReadOnly -Value $true
    Write-Host "Salvo: $path" -ForegroundColor Green
}

# Verificacao final
Write-Host "`nVerificacao:" -ForegroundColor Cyan
$cfg = Get-Content $msixPath -Raw | ConvertFrom-Json
Write-Host "  script: $($cfg.mcpServers.'n8n-DigiMarcas'.args[0])"
Write-Host "  key (20 chars): $($cfg.mcpServers.'n8n-DigiMarcas'.env.N8N_API_KEY.Substring(0,20))..."
Write-Host "  IsReadOnly: $((Get-Item $msixPath).Attributes -band [IO.FileAttributes]::ReadOnly)"
```

### 3.3 — Garantir Cloudflare permanente

```powershell
Set-Service Cloudflared -StartupType Automatic
$s = Get-Service Cloudflared
if ($s.Status -ne "Running") { Start-Service Cloudflared }
Write-Host "Cloudflare: $((Get-Service Cloudflared).Status) | StartType: $((Get-Service Cloudflared).StartType)"
```

### 3.4 — Criar script de inicialização segura

```powershell
# Script que garante Cloudflare antes de abrir o Claude Desktop
$script = @'
# Garantir Cloudflare ativo antes do Claude
$svc = Get-Service Cloudflared -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -ne "Running") {
    Start-Service Cloudflared
    Start-Sleep 3
}

# Verificar se config ainda tem mcpServers (proteção contra sobrescrita)
$msixPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json"
try {
    $cfg = Get-Content $msixPath -Raw | ConvertFrom-Json
    if ($null -eq $cfg.mcpServers) {
        Write-Host "AVISO: mcpServers foi removido do config! Restaurando..." -ForegroundColor Yellow
        # Se isto acontecer, rode novamente o CLAUDE-N8N.md Fase 3
    }
} catch {}
'@

$script | Out-File "C:\Users\digim\Desktop\verificar-mcp-n8n.ps1" -Encoding UTF8
Write-Host "Script de verificacao criado em: C:\Users\digim\Desktop\verificar-mcp-n8n.ps1"
```

---

## FASE 4 — VALIDAÇÃO FINAL

### 4.1 — Fechar Claude Desktop

```powershell
# Fechar sem forçar (evita travamento)
$procs = Get-Process -Name "claude" -ErrorAction SilentlyContinue
if ($procs) {
    $procs | ForEach-Object { $_.CloseMainWindow() | Out-Null }
    Start-Sleep 4
    Get-Process -Name "claude" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "Claude Desktop encerrado"
} else {
    Write-Host "Claude Desktop nao estava rodando"
}
```

### 4.2 — Instruções para teste manual

```
IMPORTANTE: Abra o Claude Desktop MANUALMENTE (nao via script).
Aguarde o app carregar completamente.
Clique em "+ New chat".
Aguarde 15-20 segundos.
Digite: "Que ferramentas do n8n você tem disponíveis?"
```

### 4.3 — Verificar log após abrir Claude Desktop

```powershell
Start-Sleep 20
$logPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\logs\mcp-server-n8n-DigiMarcas.log"
Get-Content $logPath -Tail 30
```

**Sucesso:** Ver `Server started and connected successfully` e `tools` na resposta.
**Falha:** Ver `Server transport closed unexpectedly` — reportar o erro completo.

---

## FASE 5 — SE AINDA FALHAR: ALTERNATIVA COM npx

Se o stdio-wrapper continuar crashando, usar npx como fallback:

```powershell
# Testar se npx funciona
$env:MCP_MODE = "stdio"; $env:LOG_LEVEL = "debug"
$env:N8N_API_URL = "https://n8n.digimarcasthecnos.com/api/v1"
$env:N8N_API_KEY = $apiKey

$proc = Start-Process `
    -FilePath "C:\Program Files\nodejs\npx.cmd" `
    -ArgumentList "-y n8n-mcp" `
    -RedirectStandardOutput "C:\temp\npx-out.txt" `
    -RedirectStandardError  "C:\temp\npx-err.txt" `
    -NoNewWindow -PassThru

Start-Sleep 20
if (!$proc.HasExited) {
    Write-Host "npx funciona! Usando como fallback." -ForegroundColor Green
    $proc.Kill()

    # Atualizar config para usar npx
    $msixPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json"
    Set-ItemProperty $msixPath -Name IsReadOnly -Value $false
    $cfg = Get-Content $msixPath -Raw | ConvertFrom-Json
    $apiKey = $cfg.mcpServers.'n8n-DigiMarcas'.env.N8N_API_KEY

    $json = @"
{
  "mcpServers": {
    "n8n-DigiMarcas": {
      "command": "C:\\Program Files\\nodejs\\npx.cmd",
      "args": ["-y", "n8n-mcp"],
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
    [System.IO.File]::WriteAllText($msixPath, $json, [System.Text.UTF8Encoding]::new($false))
    Set-ItemProperty $msixPath -Name IsReadOnly -Value $true
    Write-Host "Config atualizado para usar npx"
} else {
    Write-Host "npx tambem falhou. Ver erros:" -ForegroundColor Red
    Get-Content "C:\temp\npx-err.txt"
}
```

---

## Resumo dos problemas conhecidos e soluções

| Problema | Causa | Solução |
|----------|-------|---------|
| `Server transport closed unexpectedly` em 2-6s | Script errado (`index.js` ao invés de `stdio-wrapper.js`) | Usar `dist/mcp/stdio-wrapper.js` |
| `Could not attach to MCP server` | Claude Desktop sobrescreveu config removendo `mcpServers` | `IsReadOnly = $true` no arquivo |
| Config com JSON inválido | `ConvertTo-Json` gera aspas simples | `[System.IO.File]::WriteAllText` com here-string |
| MCP para após reboot | Cloudflare não iniciou antes do Claude Desktop | `Set-Service Cloudflared -StartupType Automatic` |
| Crash por API Key inválida | Key expirada ou inválida | Validar com `Invoke-RestMethod` antes de salvar |
| `MCP error -32001: Request timed out` após 60s | `server.js` bloqueia a conexão aguardando carregar nodes.db antes de aceitar mensagens | Patch em `server.js` + `NODE_DB_PATH` explícito no config (ver seção abaixo) |

---

## PATCH OBRIGATÓRIO — Timeout MCP (re-aplicar após `npm update n8n-mcp`)

### Contexto

O `server.js` do n8n-mcp (v2.56.0+) chama `await this.ensureInitialized()` no topo de `run()`,
bloqueando a conexão do transport stdio até o `nodes.db` (87 MB) terminar de carregar.
O Claude Desktop envia `initialize` em ~148ms mas o servidor não está ouvindo — timeout em 60s.

Todos os 29 métodos que usam o banco já chamam `ensureInitialized()` individualmente,
então o `await` no `run()` é redundante. Removê-lo faz o handshake completar em <1s.

### Verificar se o patch está aplicado

```powershell
$content = Get-Content "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\server.js" -Raw
if ($content -match 'async run\(\) \{\s+const transport = new stdio_js_1') {
    Write-Host "PATCH APLICADO" -ForegroundColor Green
} else {
    Write-Host "PATCH AUSENTE — aplicar agora!" -ForegroundColor Red
}
```

### Aplicar o patch (1 linha removida)

```powershell
# Backup antes de alterar
Copy-Item "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\server.js" `
    "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\server.js.backup"

# Patch: remover "await this.ensureInitialized();" de run()
$path = "C:\Users\digim\AppData\Roaming\npm\node_modules\n8n-mcp\dist\mcp\server.js"
$content = Get-Content $path -Raw
$patched = $content -replace '(    async run\(\) \{)\r?\n        await this\.ensureInitialized\(\);', '$1'
[System.IO.File]::WriteAllText($path, $patched, [System.Text.UTF8Encoding]::new($false))

# Verificar
if ((Get-Content $path -Raw) -match 'async run\(\) \{\s+const transport = new stdio_js_1') {
    Write-Host "Patch aplicado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "ERRO: patch nao aplicado. Restaurar backup e verificar manualmente." -ForegroundColor Red
}
```

### Atualizar configs com NODE_DB_PATH explícito

Após o patch, os dois arquivos de config devem conter `NODE_DB_PATH` apontando para o banco completo.
Se o config foi resetado pelo Claude Desktop, use o script da Fase 3.2 e adicione esta linha no `env`:

```json
"NODE_DB_PATH": "C:\\Users\\digim\\AppData\\Roaming\\npm\\node_modules\\n8n-mcp\\data\\nodes.db"
```

Config final esperado (ambos os arquivos):

```json
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
        "N8N_API_KEY": "<chave em chaves-n8n.txt>",
        "NODE_DB_PATH": "C:\\Users\\digim\\AppData\\Roaming\\npm\\node_modules\\n8n-mcp\\data\\nodes.db"
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
```

### Procedimento completo após `npm install -g n8n-mcp@latest`

```powershell
# 1. Atualizar
npm install -g n8n-mcp@latest

# 2. Aplicar patch (copiar e rodar o bloco "Aplicar o patch" acima)

# 3. Encerrar processos Claude Desktop
Stop-Process -Id (Get-Process | Where-Object {
    $_.Name -eq "claude" -and $_.Path -like "*WindowsApps*"
} | Select-Object -ExpandProperty Id) -Force -Confirm:$false -ErrorAction SilentlyContinue

# 4. Verificar NODE_DB_PATH nos configs
$msixPath = "C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json"
$cfg = Get-Content $msixPath -Raw | ConvertFrom-Json
Write-Host "NODE_DB_PATH: $($cfg.mcpServers.'n8n-DigiMarcas'.env.NODE_DB_PATH)"

# 5. Abrir Claude Desktop — ferramentas devem aparecer em <5s
```

### Resultado esperado após patch

```
23 ferramentas ativas:
- 15 ferramentas de gestão (n8n_list_workflows, n8n_create_workflow, etc.)
-  8 ferramentas auxiliares (search_nodes, get_node, search_templates, etc.)
- 1.851 nós documentados no banco completo
```
