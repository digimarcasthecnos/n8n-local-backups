# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Local n8n automation environment running via Docker Compose on Windows 11 (machine `VXpro`, user `digim`). Services: n8n (port 5678), PostgreSQL 15, Redis 7, Evolution API (port 8080). Exposed externally via Cloudflare Tunnel at `n8n.digimarcasthecnos.com`.

n8n is also integrated into Claude Desktop as an MCP server (`n8n-DigiMarcas`). See `CLAUDE-N8N.md` for the full MCP setup history and troubleshooting guide.

## Stack management

```powershell
# Start all services
docker compose -f C:\n8n-local\docker-compose.yml up -d

# Stop
docker compose -f C:\n8n-local\docker-compose.yml down

# Check status
docker ps --filter "name=n8n_app" --format "{{.Names}}: {{.Status}}"

# n8n logs
docker logs n8n_app --tail 50
```

Autostart on boot is configured via `iniciar_n8n.bat` in the Windows Startup folder (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`). The script in `auto_inicializacao_n8n.py` creates/registers this bat.

## n8n API access

- Local: `http://localhost:5678/api/v1`
- Public: `https://n8n.digimarcasthecnos.com/api/v1`
- API Key and other credentials are in `chaves-n8n.txt`

```powershell
# Quick API health check
Invoke-RestMethod -Uri "https://n8n.digimarcasthecnos.com/api/v1/workflows?limit=1" `
  -Headers @{"X-N8N-API-KEY"="<key from chaves-n8n.txt>"} -Method GET
```

## Python utility scripts

All scripts use `http://localhost:5678` and embed the API key directly.

| Script | Purpose |
|--------|---------|
| `dedup.py` | Finds and deletes duplicate workflows (keeps most recently updated) |
| `importar_templates.py` | Bulk-imports JSON workflows from `n8n_templates/Novos_templates_para_analisar_e_importar_no_n8n/` |
| `auto_inicializacao_n8n.py` | Creates `iniciar_n8n.bat` and registers it in Windows Startup |

Run with: `python <script>.py`

## MCP server (Claude Desktop)

The n8n-mcp package exposes n8n tools to Claude Desktop via stdio. Critical details:
- **Correct script:** `dist/mcp/stdio-wrapper.js` (not `dist/index.js`)
- **Config path (MSIX):** `C:\Users\digim\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`
- **Config must be set read-only** after writing, or Claude Desktop will overwrite it on exit
- Cloudflare Tunnel (`Get-Service Cloudflared`) must be running for MCP to connect

Full setup procedure and troubleshooting in `CLAUDE-N8N.md`.

## Cloudflare Tunnel

```powershell
Get-Service Cloudflared          # check status
Start-Service Cloudflared        # start if stopped
Set-Service Cloudflared -StartupType Automatic  # ensure autostart
```

## Environment

Credentials and config values are in `.env` (Docker) and `chaves-n8n.txt` (API keys). The `client_secret_*.json` file is the Google OAuth credential for integrations configured inside n8n.
