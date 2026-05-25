$script = @"
docker compose -f C:\n8n-local\docker-compose.yml up -d
"@
$script | Out-File "C:\n8n-local\iniciar_n8n.bat" -Encoding ascii

# Adicionar ao startup do Windows
$startup = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
Copy-Item "C:\n8n-local\iniciar_n8n.bat" "$startup\iniciar_n8n.bat"
echo "Startup configurado!"