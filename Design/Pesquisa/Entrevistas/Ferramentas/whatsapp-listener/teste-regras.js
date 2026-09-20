// Testes das regras puras do listener — extensao de arquivo, desembrulho de mensagem e,
// principalmente, o corte que decide o que ja foi processado. Nao abre socket nem toca no
// WhatsApp: o listener so conecta quando rodado direto (require.main).
//
//     node teste-regras.js
//
// O estado vai para um arquivo temporario via ESTADO_PATH, definido antes do require para
// o dotenv nao sobrescrever — o estado.json de verdade nao e tocado.

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const ESTADO_TESTE = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'listener-teste-')), 'estado.json');
process.env.ESTADO_PATH = ESTADO_TESTE;

const listener = require('./listener.js');
const { extensionFor, unwrap, contentTypeOf, jaProcessada, lembrarId, avancarMarca, estado } = listener;

const agora = Math.floor(Date.now() / 1000);
const msg = (id, ts) => ({ key: { id, remoteJid: 'x@g.us' }, messageTimestamp: ts });

const casos = [];
const teste = (nome, fn) => casos.push([nome, fn]);

// --- extensao de arquivo ---
teste('foto sem nome usa o mimetype', () => assert.strictEqual(extensionFor('image/jpeg', null), '.jpg'));
teste('pdf pelo nome do arquivo', () => assert.strictEqual(extensionFor('application/pdf', 'ata-1889.pdf'), '.pdf'));
teste('docx pelo mimetype', () =>
  assert.strictEqual(
    extensionFor('application/vnd.openxmlformats-officedocument.wordprocessingml.document', null),
    '.docx'
  ));
teste('mimetype com codecs ainda resolve', () => assert.strictEqual(extensionFor('audio/ogg; codecs=opus', null), '.ogg'));
teste('audio encaminhado de outro app', () => assert.strictEqual(extensionFor('audio/mpeg', 'entrevista.mp3'), '.mp3'));
teste('tipo desconhecido vira .bin', () => assert.strictEqual(extensionFor('application/x-sei-la', null), '.bin'));

// --- formato da mensagem ---
teste('documento com legenda e desembrulhado', () =>
  assert.strictEqual(
    contentTypeOf(unwrap({ documentWithCaptionMessage: { message: { documentMessage: {} } } })),
    'documentMessage'
  ));
teste('envelope de grupo nao vira o tipo da mensagem', () =>
  assert.strictEqual(contentTypeOf({ senderKeyDistributionMessage: {}, imageMessage: {} }), 'imageMessage'));

// --- corte de ja-processada (o bug do reinicio) ---
teste('estado novo parte de agora, sem importar o historico', () => {
  assert.ok(estado.ultimoTimestamp >= agora - 5, 'marca inicial deveria ser ~agora');
  assert.ok(jaProcessada(msg('ANTIGA', agora - 3600), agora - 3600), 'mensagem de 1h atras deveria ser ignorada');
});

teste('mensagem nova e processada e nao repete', () => {
  const nova = msg('NOVA', agora + 10);
  assert.strictEqual(jaProcessada(nova, agora + 10), false);
  lembrarId(nova);
  avancarMarca(agora + 10);
  assert.strictEqual(jaProcessada(nova, agora + 10), true, 'mesma mensagem nao pode ser capturada duas vezes');
});

teste('mensagem fora de ordem dentro da folga ainda passa', () =>
  assert.strictEqual(jaProcessada(msg('ATRASADA', agora - 60), agora - 60), false));

teste('REGRESSAO: o que chegou com o listener fora do ar nao e descartado no reinicio', () => {
  // Estado gravado por uma execucao anterior que parou as 12h.
  const parouEm = agora - 7200;
  fs.writeFileSync(ESTADO_TESTE, JSON.stringify({ ultimoTimestamp: parouEm, ids: [] }));

  // Processo reinicia: a segunda instancia le o estado do disco em vez de Date.now().
  delete require.cache[require.resolve('./listener.js')];
  const reiniciado = require('./listener.js');

  assert.strictEqual(reiniciado.estado.ultimoTimestamp, parouEm, 'deveria retomar de onde parou');
  // Entrevista mandada no meio da queda, 1h depois da parada:
  const naFila = msg('DA_FILA', parouEm + 3600);
  assert.strictEqual(
    reiniciado.jaProcessada(naFila, parouEm + 3600),
    false,
    'mensagem da fila do WhatsApp nao pode ser descartada no reinicio'
  );
  // E o historico antigo continua fora:
  assert.strictEqual(reiniciado.jaProcessada(msg('VELHA', parouEm - 86400), parouEm - 86400), true);
});

teste('estado corrompido nao trava o listener', () => {
  fs.writeFileSync(ESTADO_TESTE, '{ isso nao e json');
  delete require.cache[require.resolve('./listener.js')];
  const recuperado = require('./listener.js');
  assert.ok(recuperado.estado.ultimoTimestamp > 0, 'deveria cair no padrao em vez de explodir');
});

let falhas = 0;
for (const [nome, fn] of casos) {
  try {
    fn();
    console.log('  ok   ' + nome);
  } catch (err) {
    falhas++;
    console.log('  FALHA ' + nome + '\n         ' + err.message);
  }
}
fs.rmSync(path.dirname(ESTADO_TESTE), { recursive: true, force: true });
console.log(`\n${casos.length - falhas}/${casos.length} passaram`);
process.exit(falhas ? 1 : 0);
