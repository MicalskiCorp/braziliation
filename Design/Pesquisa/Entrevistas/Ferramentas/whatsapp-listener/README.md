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

> O npm 11 bloqueia por padrão os scripts de instalação da Baileys (checagem da versão do Node)
> e do protobufjs e avisa com `allow-scripts`. Não são necessários: as dependências carregam sem
> eles (validado em 2026-09-14, Node 24).

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
`{timestamp}__{remetente}__{messageId}/`, sempre com `meta.json` mais o conteúdo:

| Mandou no WhatsApp | Vira na pasta | `tipo` no `meta.json` |
|---|---|---|
| Áudio / mensagem de voz | `audio.ogg` | `audio` |
| Áudio gravado noutro app e encaminhado | `audio.mp3` / `.m4a`… (formato de origem) | `audio` |
| Texto | `mensagem.txt` | `texto` |
| Foto (câmera ou galeria) | `imagem.jpg` (extensão conforme o mimetype) | `imagem` |
| Documento (PDF, DOCX, TXT…) | `documento.pdf` (extensão conforme o arquivo) | `documento` |

Imagem e documento com legenda gravam também `legenda.txt`, e o `meta.json` ganha
`arquivo`, `mimetype` e `nomeOriginal` (o nome que o arquivo tinha no WhatsApp; foto
tirada na hora não tem). Figurinha, vídeo, contato e localização continuam ignorados.

Mensagens enviadas enquanto o listener está offline chegam normalmente na reconexão — é a
fila do próprio WhatsApp que segura, não este script. O `estado.json` (fora do git) guarda até
onde já foi lido, então **reiniciar o processo não perde a fila**: o listener retoma da última
mensagem processada em vez de recomeçar do "agora". Ele também não captura a mesma mensagem
duas vezes — guarda os últimos 500 `messageId`.

## Confirmação de captura

Por padrão o listener responde na própria conversa quando grava algo — é o jeito de
conferir pelo celular que pegou, sem abrir o `listener.log` no PC:

> ✅ Documento recebido: ata-1889.pdf (1,2 MB) — na fila de curadoria

A resposta cita a mensagem original, então num grupo movimentado dá para ver a qual delas
se refere. Controlado por `CONFIRMAR_CAPTURA` no `.env`:

| Valor | Efeito |
|---|---|
| `mensagem` (padrão) | Responde com o texto acima, citando a mensagem original |
| `reacao` | Só reage com ✅ na mensagem — discreto, não polui um grupo com outras pessoas |
| `off` | Não avisa nada |

> A confirmação volta para o próprio listener como mensagem de texto da conta. Ela é
> reconhecida e descartada — sem isso ele capturaria o próprio aviso e confirmaria a
> confirmação, em loop. Há teste de regressão para esse caso.
>
> Vale lembrar que isto faz a conta **enviar** mensagem, não só receber. É mais automação
> visível numa integração não-oficial (ver o aviso lá em cima): se o grupo tiver outras
> pessoas ou você quiser pegar leve, `reacao` faz o mesmo trabalho com menos ruído.

## Testes

```bash
node teste-regras.js
```

Exercita as regras puras — extensão de arquivo por mimetype, desembrulho de documento com
legenda, e o corte que decide o que já foi processado (inclusive o caso de regressão do
reinício de processo). Não abre socket nem toca no `estado.json` real.

## Manter sempre ligado (PC de casa)

Sem isso o listener só captura enquanto o terminal estiver aberto. No PC de casa ele roda
pelo **Agendador de Tarefas do Windows** (escolhido em 2026-09-14 — nada instalado global):

- Tarefa **"Braziliation - Listener de entrevistas"**, gatilho "ao fazer logon", ação
  `conhost.exe --headless iniciar-listener.cmd` (sem janela).
- [`iniciar-listener.cmd`](iniciar-listener.cmd) reinicia o `node listener.js` 30 s depois de
  qualquer queda e grava tudo em `listener.log` (fora do git), rotacionando para
  `listener.log.1` acima de 20 MB — a Baileys loga cada erro de rede e o arquivo cresce rápido. É lá que se confere se está
  vivo: `Conectado. Escutando: …` e uma linha `Audio salvo em …` / `Mensagem salva em …` /
  `Imagem salva em …` / `Documento salvo em …` por captura.
- Parar/iniciar à mão: `Stop-ScheduledTask` / `Start-ScheduledTask -TaskName "Braziliation -
  Listener de entrevistas"`. **Nunca rode `node listener.js` no terminal com a tarefa ativa** —
  duas instâncias com o mesmo `auth/` derrubam uma à outra.
- Alternativa não usada: **pm2** (`npm i -g pm2` + `pm2-windows-startup`).

## Perdeu a sessão / trocou de número

Apague a pasta `auth/` e rode `node listener.js` de novo para gerar um QR code novo.
