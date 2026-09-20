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
const ESTADO_PATH = process.env.ESTADO_PATH || path.join(__dirname, 'estado.json');
const TARGET_JID = (process.env.WHATSAPP_CHAT_JID || '').trim();
const DISCOVERY_MODE = TARGET_JID.length === 0;
// mensagem (padrao) | reacao | off — ver README, secao "Confirmacao de captura".
const CONFIRMACAO = (process.env.CONFIRMAR_CAPTURA || 'mensagem').trim().toLowerCase();
const STARTED_AT = Date.now();

// Folga para mensagem que chega fora de ordem — o corte por horario sozinho descartaria.
const FOLGA_SEGUNDOS = 120;
// Quantos messageId guardar para nao capturar a mesma mensagem duas vezes ('notify' e
// 'append' entregam a mesma coisa, e a sincronizacao repete o que ja veio).
const MAX_IDS_LEMBRADOS = 500;
// Espera antes de reconectar: sem ela, um 'close' em rajada abre varios sockets.
const ESPERA_RECONEXAO_MS = 5000;

const logger = pino({ level: process.env.LOG_LEVEL || 'warn' });

// Chaves que viajam junto da mensagem sem serem o conteudo dela. Em grupo elas vem
// na frente, e ler o tipo como "a primeira chave" fazia a mensagem ser descartada.
const ENVELOPE_KEYS = new Set(['messageContextInfo', 'senderKeyDistributionMessage']);

// Extensao por mimetype para quando o WhatsApp nao manda nome de arquivo — foto tirada
// na hora nao tem nome. Fora desta lista o arquivo e salvo como .bin, com o mimetype
// registrado no meta.json para a curadoria decidir o que fazer.
const EXT_BY_MIMETYPE = {
  'image/jpeg': '.jpg',
  'image/png': '.png',
  'image/webp': '.webp',
  'application/pdf': '.pdf',
  'application/msword': '.doc',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'application/vnd.ms-excel': '.xls',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
  'text/plain': '.txt',
  'text/csv': '.csv',
  // Audio gravado fora do WhatsApp e encaminhado chega com o formato do app de origem.
  'audio/ogg': '.ogg',
  'audio/mpeg': '.mp3',
  'audio/mp4': '.m4a',
  'audio/aac': '.aac',
  'audio/wav': '.wav',
  'audio/x-wav': '.wav',
  'audio/amr': '.amr',
};

// Marca de onde parar de ler o passado. Sem isso, um reinicio do processo comecava a
// contar de "agora" e engolia em silencio tudo que o WhatsApp entregou na fila enquanto
// o listener esteve fora do ar — justamente o material de uma entrevista recem-mandada.
function lerEstado() {
  try {
    const estado = JSON.parse(fs.readFileSync(ESTADO_PATH, 'utf8'));
    return {
      ultimoTimestamp: Number(estado.ultimoTimestamp) || 0,
      ids: Array.isArray(estado.ids) ? estado.ids : [],
    };
  } catch {
    // Primeira execucao (ou estado corrompido): parte de agora, para nao importar o
    // historico inteiro da conversa no pareamento.
    return { ultimoTimestamp: Math.floor(STARTED_AT / 1000), ids: [] };
  }
}

const estado = lerEstado();

function salvarEstado() {
  const tmp = ESTADO_PATH + '.tmp';
  // Grava em arquivo temporario e renomeia: queda no meio da escrita nao deixa um
  // estado.json truncado, que faria o listener voltar a contar de "agora".
  fs.writeFileSync(tmp, JSON.stringify(estado, null, 2));
  fs.renameSync(tmp, ESTADO_PATH);
}

function jaProcessada(msg, tsSegundos) {
  if (estado.ids.includes(msg.key.id)) return true;
  return Boolean(tsSegundos) && tsSegundos < estado.ultimoTimestamp - FOLGA_SEGUNDOS;
}

function lembrarId(msg) {
  estado.ids.push(msg.key.id);
  if (estado.ids.length > MAX_IDS_LEMBRADOS) {
    estado.ids = estado.ids.slice(-MAX_IDS_LEMBRADOS);
  }
  salvarEstado();
}

function avancarMarca(tsSegundos) {
  if (tsSegundos <= estado.ultimoTimestamp) return;
  estado.ultimoTimestamp = tsSegundos;
  salvarEstado();
}

function sanitize(text) {
  return String(text || 'desconhecido').replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 40);
}

function extensionFor(mimetype, fileName) {
  const fromName = path.extname(String(fileName || '')).toLowerCase();
  if (/^\.[a-z0-9]{1,8}$/.test(fromName)) return fromName;
  const mime = String(mimetype || '').split(';')[0].trim().toLowerCase();
  return EXT_BY_MIMETYPE[mime] || '.bin';
}

// Documento com legenda, mensagem efemera e "ver uma vez" chegam embrulhados num
// FutureProofMessage — o conteudo real fica um ou mais niveis abaixo.
function unwrap(message) {
  const inner =
    message.documentWithCaptionMessage?.message ||
    message.ephemeralMessage?.message ||
    message.viewOnceMessage?.message ||
    message.viewOnceMessageV2?.message;
  return inner ? unwrap(inner) : message;
}

function contentTypeOf(message) {
  return Object.keys(message).find((key) => !ENVELOPE_KEYS.has(key));
}

function timestampSegundos(msg) {
  return Number(msg.messageTimestamp?.low ?? msg.messageTimestamp ?? 0);
}

function captureDir(msg, sender) {
  const tsSeconds = timestampSegundos(msg) || Math.floor(Date.now() / 1000);
  const timestamp = new Date(tsSeconds * 1000).toISOString().replace(/[:.]/g, '-');
  const dir = path.join(INBOX_DIR, `${timestamp}__${sanitize(sender)}__${sanitize(msg.key.id)}`);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function writeMeta(dir, tipo, msg, sender, extras = {}) {
  fs.writeFileSync(
    path.join(dir, 'meta.json'),
    JSON.stringify(
      {
        tipo,
        remetente: sender,
        jid: msg.key.remoteJid,
        messageId: msg.key.id,
        timestamp: new Date().toISOString(),
        ...extras,
      },
      null,
      2
    )
  );
}

function tamanhoLegivel(bytes) {
  if (!bytes) return null;
  const mb = bytes / (1024 * 1024);
  return mb >= 1 ? `${mb.toFixed(1).replace('.', ',')} MB` : `${Math.round(bytes / 1024)} KB`;
}

// Texto das confirmações mandadas há pouco. A confirmação volta no upsert como mensagem
// de texto da própria conta: se o listener a capturasse, mandaria confirmação da
// confirmação — loop de mensagens na conta do usuário. O id é registrado depois do envio,
// tarde demais se o eco chegar antes; por isso o texto entra aqui ANTES de sair.
const confirmacoesEnviadas = new Set();

function ehEcoDeConfirmacao(msg, texto) {
  return Boolean(msg.key.fromMe) && confirmacoesEnviadas.has(texto.trim());
}

// Aviso de volta na própria conversa, para dar para conferir no celular que a captura
// pegou — sem isso o único sinal de vida é o listener.log, no PC.
async function confirmar(sock, msg, texto) {
  if (DISCOVERY_MODE || CONFIRMACAO === 'off') return;
  try {
    if (CONFIRMACAO === 'reacao') {
      // Reação não vira mensagem nova na conversa: mais discreto quando há outra gente
      // no grupo, e o listener não precisa se proteger do próprio aviso.
      await sock.sendMessage(TARGET_JID, { react: { text: '✅', key: msg.key } });
      return;
    }
    const corpo = `✅ ${texto}`;
    confirmacoesEnviadas.add(corpo);
    setTimeout(() => confirmacoesEnviadas.delete(corpo), 60000);
    const enviada = await sock.sendMessage(TARGET_JID, { text: corpo }, { quoted: msg });
    if (enviada?.key?.id) lembrarId(enviada);
  } catch (err) {
    // Falhar o aviso não pode invalidar a captura, que já está gravada em disco.
    console.error('Falha ao confirmar na conversa:', err.message);
  }
}

async function handleMessage(sock, msg) {
  if (!msg.message) return;

  const sender = msg.key.fromMe ? 'eu' : (msg.pushName || msg.key.participant || msg.key.remoteJid);

  if (DISCOVERY_MODE) {
    console.log(`[descoberta] JID=${msg.key.remoteJid}  de=${sender}`);
    return;
  }

  // Na conversa dedicada vale também o que a própria conta envia — é o caso de uso
  // principal (o usuário grava a entrevista e manda o áudio). Fora dela, nada é lido.
  if (msg.key.remoteJid !== TARGET_JID) return;

  const content = unwrap(msg.message);
  const messageType = contentTypeOf(content);
  if (!messageType) return;

  // O download precisa da mensagem já desembrulhada para achar as chaves de mídia.
  const baixar = () =>
    downloadMediaMessage(
      { key: msg.key, message: content },
      'buffer',
      {},
      { logger, reuploadRequest: sock.updateMediaMessage }
    );

  const media = content[messageType] || {};
  const mimetype = String(media.mimetype || '').toLowerCase();
  // Áudio mandado como arquivo (gravado noutro app e encaminhado) chega como documento —
  // é entrevista igual, e tem que ir para a transcrição, não para a pilha de documentos.
  const ehAudio =
    messageType === 'audioMessage' ||
    messageType === 'pttMessage' ||
    (messageType === 'documentMessage' && mimetype.startsWith('audio/'));

  try {
    if (ehAudio) {
      const ext = extensionFor(media.mimetype, media.fileName);
      // Voz do WhatsApp é sempre ogg/opus; formato que não reconheço fica como .ogg, que
      // o faster-whisper abre mesmo assim (ele sniffa o conteúdo, não confia na extensão).
      const arquivo = 'audio' + (ext === '.bin' ? '.ogg' : ext);
      const buffer = await baixar();
      const dir = captureDir(msg, sender);
      fs.writeFileSync(path.join(dir, arquivo), buffer);
      writeMeta(dir, 'audio', msg, sender, {
        arquivo,
        mimetype: media.mimetype || null,
        nomeOriginal: media.fileName || null,
      });
      console.log('Audio salvo em', dir);
      const tamanho = tamanhoLegivel(buffer.length);
      await confirmar(sock, msg, `Áudio recebido${tamanho ? ` (${tamanho})` : ''} — na fila de transcrição`);
    } else if (messageType === 'imageMessage' || messageType === 'documentMessage') {
      const ehImagem = messageType === 'imageMessage';
      const arquivo = (ehImagem ? 'imagem' : 'documento') + extensionFor(media.mimetype, media.fileName);
      const buffer = await baixar();
      const dir = captureDir(msg, sender);
      fs.writeFileSync(path.join(dir, arquivo), buffer);
      // A legenda costuma ser o contexto da foto ("a placa que te falei") — sem ela a
      // curadoria fica olhando uma imagem solta.
      const legenda = String(media.caption || '').trim();
      if (legenda) fs.writeFileSync(path.join(dir, 'legenda.txt'), legenda, 'utf8');
      // meta.json por último: é ele que marca a pasta como capturada por inteiro, e o
      // transcrever.py pula pasta sem meta para não pegar download pela metade.
      writeMeta(dir, ehImagem ? 'imagem' : 'documento', msg, sender, {
        arquivo,
        mimetype: media.mimetype || null,
        nomeOriginal: media.fileName || media.title || null,
      });
      console.log(ehImagem ? 'Imagem salva em' : 'Documento salvo em', dir);
      const tamanho = tamanhoLegivel(buffer.length);
      const nome = media.fileName || media.title;
      await confirmar(
        sock,
        msg,
        ehImagem
          ? `Imagem recebida${tamanho ? ` (${tamanho})` : ''} — na fila de curadoria`
          : `Documento recebido${nome ? `: ${nome}` : ''}${tamanho ? ` (${tamanho})` : ''} — na fila de curadoria`
      );
    } else if (messageType === 'conversation' || messageType === 'extendedTextMessage') {
      const text = content.conversation || content.extendedTextMessage?.text || '';
      if (!text.trim()) return;
      if (ehEcoDeConfirmacao(msg, text)) return;
      const dir = captureDir(msg, sender);
      fs.writeFileSync(path.join(dir, 'mensagem.txt'), text, 'utf8');
      writeMeta(dir, 'texto', msg, sender);
      console.log('Mensagem salva em', dir);
      await confirmar(sock, msg, 'Anotação recebida — na fila de curadoria');
    }
    // Figurinha, vídeo, contato e localização seguem fora do escopo da captura.
  } catch (err) {
    console.error('Falha ao salvar mensagem', msg.key.id, err);
  }
}

// Carregada uma vez só: reabrir a cada reconexão criava um segundo objeto de sessão
// escrevendo na mesma pasta auth/.
let sessao = null;
let reconectando = false;

async function start() {
  if (!sessao) sessao = await useMultiFileAuthState(AUTH_DIR);
  const { state, saveCreds } = sessao;

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
      // Uma reconexão por vez: 'close' pode disparar mais de uma vez na mesma queda, e
      // cada chamada de start() abria um socket novo — todos vivos, capturando em dobro.
      if (!loggedOut && !reconectando) {
        reconectando = true;
        setTimeout(() => {
          reconectando = false;
          start().catch((err) => console.error('Falha ao reconectar:', err));
        }, ESPERA_RECONEXAO_MS);
      }
    } else if (connection === 'open') {
      console.log(
        DISCOVERY_MODE
          ? 'Conectado. Modo DESCOBERTA — mande uma mensagem de teste na conversa e copie o JID impresso aqui.'
          : `Conectado. Escutando: ${TARGET_JID}`
      );
    }
  });

  // 'append' traz o que foi enviado por outro aparelho da própria conta. O estado em disco
  // (estado.json) diz até onde já foi lido: descarta o histórico que chega na sincronização
  // sem descartar o que entrou na fila enquanto o listener esteve fora do ar.
  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify' && type !== 'append') return;

    let maiorTs = 0;
    for (const msg of messages) {
      const ts = timestampSegundos(msg);
      if (ts > maiorTs) maiorTs = ts;
      if (jaProcessada(msg, ts)) continue;
      await handleMessage(sock, msg);
      if (!DISCOVERY_MODE && msg.key.remoteJid === TARGET_JID) lembrarId(msg);
    }

    // A marca de tempo só avança depois do lote inteiro. Avançar a cada mensagem faria a
    // primeira de uma sincronização (que chega fora de ordem) cortar as seguintes.
    if (!DISCOVERY_MODE && maiorTs) avancarMarca(maiorTs);
  });
}

// Só conecta quando rodado direto. Sob `require` o arquivo vira módulo, para o
// teste-regras.js exercitar as regras de corte sem abrir socket nenhum.
if (require.main === module) {
  start().catch((err) => {
    console.error('Erro fatal no listener:', err);
    process.exit(1);
  });
}

module.exports = {
  extensionFor,
  unwrap,
  contentTypeOf,
  jaProcessada,
  lembrarId,
  avancarMarca,
  estado,
  tamanhoLegivel,
  ehEcoDeConfirmacao,
  confirmacoesEnviadas,
};
