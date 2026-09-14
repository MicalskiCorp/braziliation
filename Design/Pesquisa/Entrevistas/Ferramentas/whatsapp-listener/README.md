# whatsapp-listener

Bot local que fica logado no WhatsApp (protocolo multi-device via
[Baileys](https://github.com/WhiskeySockets/Baileys), não-oficial) e grava em
`../../_inbox/` tudo que chegar numa conversa dedicada — pensado para captar
entrevistas de pesquisa gravadas esporadicamente. Contexto completo: ADR-009 e
`../index.md`.

## ⚠️ Antes de rodar

- **Não é a API oficial do WhatsApp.** Usar automação numa conta pessoal viola os Termos
  de Serviço. O risco de bloqueio é considerado baixo em uso pessoal, volume baixo (uma
  conversa, mensagens esporádicas) e número próprio, mas **não é zero** e não há garantia
  de recuperação da conta se acontecer. Se possível, use um número secundário dedicado a
  isso, não o principal.
- A sessão pareada (pasta `auth/`) e tudo que cai em `_inbox/` é dado pessoal/de
  terceiros — nunca commitado (ver `.gitignore` na raiz do repo).

## Setup

```bash
cd Design/Pesquisa/Entrevistas/Ferramentas/whatsapp-listener
npm install
cp .env.example .env
```

## Primeira execução — descobrir o JID da conversa

Deixe `WHATSAPP_CHAT_JID` vazio no `.env` na primeira vez:

```bash
node listener.js
```

1. Um QR code aparece no terminal. No celular: **WhatsApp → Configurações → Aparelhos
   conectados → Conectar um aparelho** e escaneie.
2. Conectado, o listener entra em **modo descoberta**: manda uma mensagem de teste na
   conversa que você quer usar para entrevistas (consigo mesmo ou um grupo privado) e o
   terminal imprime o JID dela (`5547999999999@s.whatsapp.net` para conversa individual,
   `120363...@g.us` para grupo).
3. Copie esse JID para `WHATSAPP_CHAT_JID` no `.env` e reinicie — a partir daí só essa
   conversa é capturada.

## Rodando de verdade

```bash
node listener.js
```

Cada mensagem nova na conversa configurada vira uma pasta em `../../_inbox/`:
`{timestamp}__{remetente}__{messageId}/` com `audio.ogg` (voz) ou `mensagem.txt`
(texto) + `meta.json`. Mensagens enviadas enquanto o listener está offline chegam
normalmente na reconexão — é a fila do próprio WhatsApp que segura, não este script.

## Manter sempre ligado (PC de casa)

Sem isso o listener só captura enquanto o terminal estiver aberto. Duas opções simples
no Windows:

- **pm2** (`npm i -g pm2`): `pm2 start listener.js --name entrevistas-braziliation`,
  depois `pm2 save` e configurar o `pm2-startup` correspondente para sobreviver a reboot.
- **Agendador de Tarefas do Windows**: ação "Iniciar um programa" apontando para `node`
  com argumento `listener.js` nesta pasta, gatilho "ao fazer logon", opção "reiniciar em
  caso de falha".

## Perdeu a sessão / trocou de número

Apague a pasta `auth/` e rode `node listener.js` de novo para gerar um QR code novo.
