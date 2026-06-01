# CLAUDE-EVOL-QRCODE.md
## Missão: Resolver o QR Code do WhatsApp no Evolution API

---

## 🎯 Objetivo Final
Fazer o Evolution API v2.2.3 gerar o QR Code do WhatsApp com sucesso,
de forma que o endpoint `/instance/connect/wapp` retorne um campo `base64`
com a imagem do QR Code para escaneamento.

---

## 🖥️ Ambiente

| Item | Valor |
|------|-------|
| OS | Windows 11 + Docker Desktop (WSL2) |
| Container | `evolution_api` |
| Imagem | `atendai/evolution-api:v2.2.3` |
| URL | `http://localhost:8080` |
| API Key | `evolution-key-digimarcasthecnos` |
| Rede Docker | `n8n-local_default` |
| Baileys | v6.7.12 em `/evolution/node_modules/baileys/` |

---

## 🔴 Problema Atual

Ao criar uma instância WhatsApp, o Baileys entra em **crash loop**:
- `[ChannelStartupService]` repete a cada 3-5 segundos
- `/instance/connect/wapp` sempre retorna `{"count": 0}`
- Nenhum QR Code é gerado

### Sequência do crash:
1. Evolution API inicia limpo (sem instâncias) ✅
2. Instância criada → Baileys tenta conectar ao WhatsApp
3. WebSocket abre → WhatsApp envia server hello (binário)
4. Conexão fecha com **code 1006** (abnormal closure)
5. Baileys reinicia → loop infinito

---

## 🔍 Diagnósticos Já Realizados

```bash
# Teste WSS confirmou conectividade:
docker exec evolution_api node -e "
const WebSocket = require('/evolution/node_modules/ws');
const ws = new WebSocket('wss://web.whatsapp.com/ws/chat', {
  origin: 'https://web.whatsapp.com',
  headers: {'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0'}
});
ws.on('open', () => console.log('CONECTADO'));
ws.on('message', d => console.log('MSG recebida'));
ws.on('close', c => console.log('Fechado code:', c));
setTimeout(() => process.exit(0), 5000);
"
# Resultado: CONECTADO → MSG recebida → Fechado code: 1006
```

**Conclusão:** O WhatsApp aceita a conexão mas a fecha após o server hello.
O Baileys não consegue completar o **Noise Protocol handshake**.

### Erros nos logs do container:
```
"message":"Timed Out"
"stack":"Error: Timed Out at promiseTimeout (baileys/lib/Utils/generics.js)"
at awaitNextMessage (baileys/lib/Socket/socket.js)
at validateConnection (baileys/lib/Socket/socket.js)
statusCode: 408 "error": "Request Timeout"
```

### Configuração atual do Baileys (`/evolution/node_modules/baileys/lib/Defaults/index.js`):
```js
browser: Browsers.windows('Edge'),   // foi ubuntu/Chrome, já trocado
connectTimeoutMs: 20000,             // 20 segundos
waWebSocketUrl: 'wss://web.whatsapp.com/ws/chat'
```

---

## 📁 Arquivos Relevantes no Container

```
/evolution/node_modules/baileys/lib/
├── Defaults/index.js          ← browser, timeouts, config
├── Socket/socket.js           ← validateConnection, awaitNextMessage
├── Socket/Client/
│   └── web-socket-client.js   ← handshakeTimeout, timeout
├── Utils/generics.js          ← promiseTimeout (linha ~165)
└── WABinary/
    └── constants.js           ← protocolo binário
```

---

## 🛠️ Passos de Diagnóstico e Correção

### PASSO 1 — Inspecionar o erro exato

```bash
# Ver os logs em tempo real enquanto cria instância
docker logs evolution_api --since 1m --follow &

# Em paralelo: criar instância
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: evolution-key-digimarcasthecnos" \
  -d '{"instanceName":"wapp","qrcode":true,"integration":"WHATSAPP-BAILEYS"}'
```

### PASSO 2 — Ler o código do validateConnection

```bash
docker exec evolution_api cat /evolution/node_modules/baileys/lib/Socket/socket.js | \
  grep -n "validateConnection\|awaitNextMessage\|promiseTimeout\|connectTimeout" | head -20
```

### PASSO 3 — Ler o web-socket-client.js

```bash
docker exec evolution_api cat /evolution/node_modules/baileys/lib/Socket/Client/web-socket-client.js
```

### PASSO 4 — Verificar a versão completa dos defaults

```bash
docker exec evolution_api node -e "
const d = require('/evolution/node_modules/baileys/lib/Defaults/index.js');
console.log(JSON.stringify(d.DEFAULT_CONNECTION_CONFIG, null, 2));
"
```

### PASSO 5 — Tentar correções em ordem de prioridade

**Correção A: Aumentar timeout para 120s**
```bash
docker exec evolution_api sed -i \
  's/connectTimeoutMs: 20000/connectTimeoutMs: 120000/' \
  /evolution/node_modules/baileys/lib/Defaults/index.js
```

**Correção B: Mudar browser fingerprint para macOS/Safari**
```bash
docker exec evolution_api sed -i \
  "s/Browsers.windows('Edge')/Browsers.macOS('Safari')/" \
  /evolution/node_modules/baileys/lib/Defaults/index.js
```

**Correção C: Verificar e ajustar handshakeTimeout no web-socket-client.js**
```bash
# Ler o arquivo completo para entender a configuração WSS
docker exec evolution_api cat \
  /evolution/node_modules/baileys/lib/Socket/Client/web-socket-client.js
```

**Correção D: Adicionar headers adicionais ao WebSocket**
```bash
# Verificar se há opção de customizar headers no WebSocket
docker exec evolution_api grep -n "headers\|userAgent\|origin" \
  /evolution/node_modules/baileys/lib/Socket/Client/web-socket-client.js
```

### PASSO 6 — Reiniciar e testar após cada correção

```bash
# Após qualquer mudança nos arquivos:
docker restart evolution_api
sleep 20

# Deletar instância antiga
curl -X DELETE http://localhost:8080/instance/delete/wapp \
  -H "apikey: evolution-key-digimarcasthecnos"
sleep 3

# Criar nova instância
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: evolution-key-digimarcasthecnos" \
  -d '{"instanceName":"wapp","qrcode":true,"integration":"WHATSAPP-BAILEYS"}'

# Aguardar e verificar QR Code (tentar por 2 minutos)
for i in $(seq 1 24); do
  sleep 5
  RESULT=$(curl -s http://localhost:8080/instance/connect/wapp \
    -H "apikey: evolution-key-digimarcasthecnos")
  echo "Tentativa $i: $(echo $RESULT | head -c 100)"
  if echo "$RESULT" | grep -q "base64"; then
    echo "🎉 QR CODE GERADO!"
    # Salvar QR Code
    echo $RESULT | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
img = d['base64'].split(',')[-1]
with open('/tmp/qrcode.png','wb') as f:
    f.write(base64.b64decode(img))
print('Salvo em /tmp/qrcode.png')
"
    break
  fi
done
```

---

## ✅ Critério de Sucesso

O endpoint retornar algo como:
```json
{
  "base64": "data:image/png;base64,iVBORw0KGgo...",
  "count": 1
}
```

Se `base64` estiver presente → **SUCESSO!**
Copiar o arquivo `/tmp/qrcode.png` para `C:/n8n-local/qrcode.png`

---

## 📊 Estado do Projeto (contexto geral)

Este QR Code é o **último passo** de um projeto maior:

| Item | Status |
|------|--------|
| 16.494 workflows n8n importados | ✅ |
| 24 credenciais configuradas | ✅ |
| 6.805 workflows com IDs atualizados | ✅ |
| n8n rodando em localhost:5678 | ✅ |
| Evolution API rodando em localhost:8080 | ✅ |
| **WhatsApp QR Code** | 🔴 PENDENTE |

---

## 🚨 Notas Importantes

1. **NÃO use `--force-recreate`** sem antes deletar a instância `wapp` do banco —
   isso causará o crash loop imediatamente ao tentar reconectar
2. Mudanças em `/evolution/node_modules/` são **temporárias** (perdidas no force-recreate)
3. O container usa **Alpine Linux** → usar `apk add` para instalar pacotes
4. `git` pode ser instalado com: `apk update && apk add git`
5. Node.js v20.17.0 está disponível no container

---

## 💡 Abordagens Alternativas (se as correções acima falharem)

1. **Inspecionar o Noise Protocol** em `socket.js` — verificar se o handshake
   inicial está correto para o protocolo atual do WhatsApp
2. **Testar com pairing code** — se o endpoint existir em v2.2.3:
   ```bash
   curl -X POST http://localhost:8080/instance/pairingCode/wapp \
     -H "Content-Type: application/json" \
     -H "apikey: evolution-key-digimarcasthecnos" \
     -d '{"phoneNumber":"5511960373203"}'
   ```
3. **Adicionar variável SERVER_URL** com a URL do ngrok:
   `https://katherine-exaggerated-cami.ngrok-free.dev`
4. **Verificar se há alguma variável de ambiente** que force o QR Code
   (ex: `QRCODE_LIMIT`, `WA_BUSINESS_TOKEN`, etc.)

