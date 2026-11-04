// `claude plugin test Central/mod-economia` — roda no pre-commit quando o mod muda (ADR-015).
import { expect, mock, test } from 'claude-code/testing'

const CENTRAL = { CENTRAL_EXECUCAO: '20261104-120152-dev-unity-67bb', CENTRAL_FILA: 'Unity' }
// Num teste, `$.session.compact` leva o evento inteiro: o gatilho e a conversa sendo compactada.
const CONVERSA = [
  { role: 'user' as const, text: 'executar: ligar o CameraScaler', toolUses: [] },
  { role: 'assistant' as const, text: 'Feito o primeiro passo.', toolUses: [] },
]
const RESUMO = [{ role: 'user' as const, text: 'resumo', toolUses: [] }]

// Abaixo do mod, este hook faz o papel do motor: anota as instruções que chegaram e devolve o resumo.
function motor(on: Parameters<Parameters<typeof test>[1]>[1], anotar: (i: string | undefined) => void) {
  on('session.compact', (_, e) => {
    anotar(e.instructions)
    return { messages: RESUMO }
  })
}

test('a compactação automática de uma execução da Central guarda o contrato', async ($, on) => {
  let visto: string | undefined
  mock.env(on, CENTRAL)
  motor(on, i => (visto = i))

  await $.session.compact({ trigger: 'auto', messages: CONVERSA })

  expect(visto).toContain('execução 20261104-120152-dev-unity-67bb')
  expect(visto).toContain('«Unity»')
  expect(visto).toContain('```resultado```')
  expect(visto).toContain('unity-validar')
})

test('a instrução do /compact continua na frente', async ($, on) => {
  let visto: string | undefined
  mock.env(on, CENTRAL)
  motor(on, i => (visto = i))

  await $.session.compact({ trigger: 'manual', instructions: 'foco no CameraScaler', messages: CONVERSA })

  expect(visto?.startsWith('foco no CameraScaler')).toBe(true)
  expect(visto).toContain('execução 20261104-120152-dev-unity-67bb')
})

test('subagente compacta sem as instruções da execução', async ($, on) => {
  let visto: string | undefined = 'não chamado'
  mock.env(on, CENTRAL)
  motor(on, i => (visto = i))

  await $.session.compact({ trigger: 'auto', agentId: 'a1', messages: CONVERSA })

  expect(visto).toBeUndefined()
})

test('fora da Central o mod não muda nada', async ($, on) => {
  let visto: string | undefined = 'não chamado'
  mock.env(on, {})
  motor(on, i => (visto = i))

  await $.session.compact({ trigger: 'auto', messages: CONVERSA })

  expect(visto).toBeUndefined()
})
