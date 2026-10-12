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
const {
  extensionFor,
  unwrap,
  contentTypeOf,
  jaProcessada,
  lembrarId,
  avancarMarca,
  estado,
  tamanhoLegivel,
  resumoDoLote,
  lerComandoAssunto,
  assuntoVigente,
  ehEcoDeConfirmacao,
  confirmacoesEnviadas,
} = listener;

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

// --- confirmacao na conversa ---
teste('tamanho legivel em KB e MB', () => {
  assert.strictEqual(tamanhoLegivel(26266), '26 KB');
  assert.strictEqual(tamanhoLegivel(3 * 1024 * 1024), '3,0 MB');
});

teste('REGRESSAO: a confirmacao nao e capturada como anotacao', () => {
  const corpo = '✅ Áudio recebido (1,8 MB) — na fila de transcrição';
  confirmacoesEnviadas.add(corpo);
  // O eco da propria conta tem que ser reconhecido, senao o listener confirma a
  // confirmacao e entra em loop de mensagens.
  assert.strictEqual(ehEcoDeConfirmacao({ key: { fromMe: true } }, corpo), true);
  // Mesmo texto vindo de outra pessoa nao e eco — nao pode sumir da captura.
  assert.strictEqual(ehEcoDeConfirmacao({ key: { fromMe: false } }, corpo), false);
  // Anotacao de verdade da propria conta segue capturada.
  assert.strictEqual(ehEcoDeConfirmacao({ key: { fromMe: true } }, 'o Rudolf falou da enchente'), false);
  confirmacoesEnviadas.delete(corpo);
});

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

// --- resumo do lote de confirmacoes ---
const MB = 1024 * 1024;
teste('lote de um item mantem o aviso individual', () => {
  const texto = 'Documento recebido: ata-1889.pdf (1,2 MB) — na fila de curadoria';
  assert.strictEqual(
    resumoDoLote([{ categoria: 'documento', bytes: 1.2 * MB, texto, assunto: 'teatro-carlos-gomes' }]),
    texto + '\n📂 Assunto: teatro-carlos-gomes'
  );
});

teste('lote grande vira uma mensagem so, por categoria e com o total', () => {
  const itens = [
    ...Array.from({ length: 10 }, () => ({ categoria: 'audio', bytes: 6 * MB, texto: 'a', assunto: 'teatro' })),
    ...Array.from({ length: 16 }, () => ({ categoria: 'imagem', bytes: MB, texto: 'i', assunto: 'teatro' })),
    { categoria: 'anotacao', texto: 'n', assunto: 'teatro' },
  ];
  assert.strictEqual(
    resumoDoLote(itens),
    'Lote de 27 itens recebido e validado:\n' +
      '• 10 áudios (60,0 MB) — na fila de transcrição\n' +
      '• 16 imagens (16,0 MB) — na fila de curadoria\n' +
      '• 1 anotação — na fila de curadoria\n' +
      '📂 Assunto: teatro\n' +
      '💡 Fotos enviadas como *Documento* mantêm o horário da câmera (📎 → Documento).'
  );
});

teste('lote sem foto comum nao traz a dica de envio', () => {
  const resumo = resumoDoLote([{ categoria: 'documento', bytes: MB }, { categoria: 'audio', bytes: MB }]);
  assert.ok(!resumo.includes('💡'), 'documento ja preserva o horario — dica so atrapalha');
});

teste('resumo de lote enviado e reconhecido como eco', () => {
  const corpo = '✅ ' + resumoDoLote([{ categoria: 'imagem', bytes: MB }, { categoria: 'imagem', bytes: MB }]);
  confirmacoesEnviadas.add(corpo);
  assert.strictEqual(ehEcoDeConfirmacao({ key: { fromMe: true } }, corpo), true);
  confirmacoesEnviadas.delete(corpo);
});

// --- assunto da coleta (#assunto / #fim) ---
teste('#assunto abre com slug sem acento, #fim fecha, texto comum nao e comando', () => {
  assert.deepStrictEqual(lerComandoAssunto('#assunto Benzedeira Dona Zélia'), { acao: 'abrir', assunto: 'benzedeira-dona-zelia' });
  assert.deepStrictEqual(lerComandoAssunto('#Assunto: Edith Gaertner\nlevar o caderno'), { acao: 'abrir', assunto: 'edith-gaertner' });
  assert.deepStrictEqual(lerComandoAssunto('#fim'), { acao: 'fechar' });
  assert.strictEqual(lerComandoAssunto('#assunto'), null, 'sem nome nao abre assunto');
  assert.strictEqual(lerComandoAssunto('falamos do #assunto ontem'), null, 'so vale no comeco da mensagem');
  assert.strictEqual(lerComandoAssunto('✅ 📂 Assunto *x* aberto — até #fim'), null, 'o proprio aviso nao vira comando');
});

teste('assunto expira depois de 12 h sem nada chegar', () => {
  const aberto = { slug: 'benzedeira', desde: 1000, ultimo: 1000 };
  assert.strictEqual(assuntoVigente(aberto, 1000 + 3600), 'benzedeira');
  assert.strictEqual(assuntoVigente(aberto, 1000 + 13 * 3600), null, '#fim esquecido nao pode contaminar o proximo assunto');
  assert.strictEqual(assuntoVigente(null, 1000), null);
});

teste('aviso mostra o assunto marcado e nao cobra marca de quem nao usou', () => {
  assert.ok(resumoDoLote([{ categoria: 'audio', texto: 'a', assunto: 'benzedeira' }]).includes('📂 Assunto: benzedeira'));
  assert.strictEqual(
    resumoDoLote([{ categoria: 'audio', texto: 'Áudio recebido', assunto: null }]),
    'Áudio recebido',
    'sem #assunto o assunto e detectado na curadoria — o aviso nao cobra nada'
  );
  const misto = resumoDoLote([
    { categoria: 'audio', texto: 'a', assunto: 'teatro' },
    { categoria: 'audio', texto: 'b', assunto: 'benzedeira' },
  ]);
  assert.ok(misto.includes('📂 Assunto: teatro') && misto.includes('📂 Assunto: benzedeira'), 'lote misto mostra os dois');
  assert.strictEqual(
    resumoDoLote([{ categoria: 'anotacao', texto: '📂 Assunto *x* aberto', assunto: 'x', comando: true }]),
    '📂 Assunto *x* aberto',
    'o aviso de abertura nao repete o assunto'
  );
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
