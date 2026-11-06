---
name: estrutura
description: "Mapa de navegação do Braziliation (`estrutura.md` na raiz): diz onde fica cada coisa e o que não ler, para ir direto ao arquivo. Acione ANTES da primeira busca ou leitura feita para localizar algo no repositório — Glob, Grep, ls ou find atrás de script, doc, TODO, dívida, ADR, regra, agente, skill, asset, cena, paleta ou ferramenta; 'onde fica', 'onde está', 'achar o arquivo' — e antes de criar, mover ou renomear arquivo ou pasta. Não acione se o mapa já foi lido nesta sessão, nem quando o pedido já traz o caminho exato."
user-invocable: false
---

**Antes de procurar qualquer coisa, leia o [`estrutura.md`](../../../estrutura.md) da raiz, uma vez por sessão.** Se ele já está nesta conversa, não releia: use o que já foi lido.

O mapa é a fonte única de "onde fica". Ele aponta para os índices que o projeto já mantém (fichas de sistema, roteadores `index.md`, TODOs, `AssetsStructure.md`) e diz o que nunca vale ler. Cada `Glob` ou `Grep` às cegas é uma rodada a mais relendo o contexto inteiro.

## Como proceder

1. **Ache a linha** da §2 do mapa que responde ao que você procura e abra o arquivo com `Read`.
   - Se a linha aponta para um índice (`index.md` ou ficha de sistema), leia o índice e vá ao arquivo que ele lista.
2. **O mapa não responde?** Faça um `Grep` restrito à pasta da área mais próxima, com `glob` ou `type`, e nunca na raiz.
   - Se o caminho achado for estável (pasta ou arquivo canônico), acrescente a linha na §2 do mapa.
3. **Respeite a §3 ("Não ler").** Arquivo gerado, histórico congelado, gabarito de terceiros e YAML de cena só se consultam por `Grep`, e só quando o pedido for sobre eles.
4. **Vai criar, mover ou renomear?** Siga a linha da §4 do mapa e, quando ela citar uma skill (`novo-adr`, `nova-cidade`, `novo-asset`, `novo-inimigo`, `novo-agente`, `gerir-todo`, `handoff`), use a skill.
   - Pasta nova de 1º ou 2º nível ganha linha no mapa.

As restrições de busca (`path` sempre, nunca a raiz, nada de `**/*.ext` solto) estão na regra `.claude/rules/busca-com-filtro.md`, que carrega em toda sessão. O detalhe está na §1 do mapa.
