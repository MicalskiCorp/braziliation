// Mod de economia de tokens da Central do Braziliation (ADR-015).
//
// O que pesa numa execução longa é o contexto relido a cada requisição. A Central compacta mais
// cedo nas filas de sessão longa, pela variável CLAUDE_CODE_AUTO_COMPACT_WINDOW: é o único jeito
// de compactar no meio de um turno, porque `$.session.compact` recusa enquanto um turno roda.
// Este mod cuida do que só um mod faz: o que o resumo guarda. Sem ele, o resumo genérico pode
// perder a lista de itens, as decisões pedidas ao responsável e a checagem que faltava — e a
// execução termina sem o bloco de resultado ou sem o unity-validar.
//
// Só age dentro da Central: sem CENTRAL_EXECUCAO no ambiente, passa adiante sem mudar nada.
// Não aprova nem bloqueia ferramenta nenhuma (ADR-012, travas intactas).
import type { Register } from 'claude-code'

export function instrucoes(execucao: string, fila: string): string {
  return [
    `Esta conversa é a execução ${execucao} da Central do Braziliation${fila ? `, fila «${fila}»` : ''}.`,
    'O resumo precisa guardar, sem perder nada:',
    '1. a lista exata dos itens pedidos e a situação de cada um (feito, em andamento, precisa-decisao, bloqueado);',
    '2. cada arquivo criado, alterado ou apagado, com o caminho;',
    '3. as perguntas e decisões pendentes com o responsável, e o que ele já respondeu;',
    '4. as checagens que ainda faltam (unity-validar depois do último .cs em Assets/, dotnet test, meta-check, paletas);',
    '5. onde o trabalho parou e qual é o próximo passo.',
    'Saída longa de ferramenta não entra no resumo: só a conclusão e o caminho do arquivo, que pode ser lido de novo.',
    'Lembre no resumo que a mensagem final leva o bloco ```resultado``` com todos os itens e que commit e push são proibidos.',
  ].join('\n')
}

export const register: Register = on => {
  on('session.compact', async ($, e, next) => {
    // Subagente compacta a própria conversa: os itens da execução não são dele.
    if (e.agentId !== undefined) return next(e)
    const execucao = await $.env.get('CENTRAL_EXECUCAO')
    if (!execucao) return next(e)
    const fila = (await $.env.get('CENTRAL_FILA')) ?? ''
    const nossas = instrucoes(execucao, fila)
    return next({ ...e, instructions: e.instructions ? `${e.instructions}\n\n${nossas}` : nossas })
  })
}
