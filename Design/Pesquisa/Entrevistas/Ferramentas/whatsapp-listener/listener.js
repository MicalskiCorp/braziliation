// Listener do WhatsApp para a pesquisa do Braziliation (ADR-009).
// Conecta na conta pessoal via protocolo multi-device do Baileys (nao-oficial) e
// grava em Entrevistas/_inbox/ tudo que chegar na conversa dedicada configurada
// em WHATSAPP_CHAT_JID. Ver README.md para setup, pareamento e modo descoberta.

require('dotenv').config();

const fs = require('fs');
const path = require('path');
const {
  default: makeWASocket,
  useMultiFileAuthState,
  downloadMediaMessage,
  DisconnectReason,
} = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const pino = require('pino');

const AUTH_DIR = process.env.AUTH_DIR || path.join(__dirname, 'auth');
const INBOX_DIR = process.env.INBOX_DIR || path.join(__dirname, '..', '..', '_inbox');
const TARGET_JID = (process.env.WHATSAPP_CHAT_JID || '').trim();
const DISCOVERY_MODE = TARGET_JID.length === 0;

const logger = pino({ level: process.env.LOG_LEVEL || 'warn' });

function sanitize(text) {
  return String(text || 'desconhecido').replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 40);
}

function captureDir(msg, sender) {
  const tsSeconds = Number(msg.messageTimestamp?.low ?? msg.messageTimestamp ?? Date.now() / 1000);
  const timestamp = new Date(tsSeconds * 1000).toISOString().replace(/[:.]/g, '-');
  const dir = path.join(INBOX_DIR, `${timestamp}__${sanitize(sender)}__${sanitize(msg.key.id)}`);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function writeMeta(dir, tipo, msg, sender) {
  fs.writeFileSync(
    path.join(dir, 'meta.json'),
    JSON.stringify(
      {
        tipo,
        remetente: sender,
        jid: msg.key.remoteJid,
        messageId: msg.key.id,
        timestamp: new Date().toISOString(),
      },
      null,
      2
    )
  );
}

async function handleMessage(sock, msg) {
  if (!msg.message || msg.key.fromMe) return;

  const sender = msg.pushName || msg.key.participant || msg.key.remoteJid;

  if (DISCOVERY_MODE) {
    console.log(`[descoberta] JID=${msg.key.remoteJid}  de=${sender}`);
    return;
  }

  if (msg.key.remoteJid !== TARGET_JID) return;

  const messageType = Object.keys(msg.message)[0];

  try {
    if (messageType === 'audioMessage' || messageType === 'pttMessage') {
      const buffer = await downloadMediaMessage(
        msg,
        'buffer',
        {},
        { logger, reuploadRequest: sock.updateMediaMessage }
      );
      const dir = captureDir(msg, sender);
      fs.writeFileSync(path.join(dir, 'audio.ogg'), buffer);
      writeMeta(dir, 'audio', msg, sender);
      console.log('Audio salvo em', dir);
    } else if (messageType === 'conversation' || messageType === 'extendedTextMessage') {
      const text = msg.message.conversation || msg.message.extendedTextMessage?.text || '';
      if (!text.trim()) return;
      const dir = captureDir(msg, sender);
      fs.writeFileSync(path.join(dir, 'mensagem.txt'), text, 'utf8');
      writeMeta(dir, 'texto', msg, sender);
      console.log('Mensagem salva em', dir);
    }
    // Outros tipos (imagem, documento, figurinha...) sao ignorados de proposito —
    // o escopo desta captura e audio/texto de entrevista.
  } catch (err) {
    console.error('Falha ao salvar mensagem', msg.key.id, err);
  }
}

async function start() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

  const sock = makeWASocket({ auth: state, logger, printQRInTerminal: false });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log('Escaneie no WhatsApp: Aparelhos conectados > Conectar um aparelho');
      qrcode.generate(qr, { small: true });
    }

    if (connection === 'close') {
      const statusCode = lastDisconnect?.error?.output?.statusCode;
      const loggedOut = statusCode === DisconnectReason.loggedOut;
      console.log('Conexao fechada.', loggedOut ? 'Deslogado — apague auth/ e escaneie de novo.' : 'Reconectando...');
      if (!loggedOut) start();
    } else if (connection === 'open') {
      console.log(
        DISCOVERY_MODE
          ? 'Conectado. Modo DESCOBERTA — mande uma mensagem de teste na conversa e copie o JID impresso aqui.'
          : `Conectado. Escutando: ${TARGET_JID}`
      );
    }
  });

  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return;
    for (const msg of messages) {
      await handleMessage(sock, msg);
    }
  });
}

start().catch((err) => {
  console.error('Erro fatal no listener:', err);
  process.exit(1);
});
