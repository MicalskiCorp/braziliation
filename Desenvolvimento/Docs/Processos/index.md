# Manual de Processos do Braziliation

> Os 44 processos do projeto, camada por camada: quem executa, como se aciona, o passo a passo, o que lê e escreve, e onde a entrega é travada. Cada arquivo aponta a fonte canônica (agente ou skill) — o manual resume, a fonte manda.

## Camadas

| Camada | Área | Processos | Arquivo |
|---|---|:-:|---|
| Pesquisa | Design | 6 | [`pesquisa.md`](pesquisa.md) |
| Criativo | Design | 10 | [`criativo.md`](criativo.md) |
| Arte | Design (lateral) | 7 | [`arte.md`](arte.md) |
| Documentação | Desenvolvimento | 7 | [`documentacao.md`](documentacao.md) |
| Implementação | Desenvolvimento | 9 | [`implementacao.md`](implementacao.md) |
| Orquestração | Transversal | 5 | [`orquestracao.md`](orquestracao.md) |

Critério de onde cada procedimento mora (modo, skill, script, teste, hook, regra ou fork): [`modo-skill-ou-regra.md`](modo-skill-ou-regra.md).

## Como as camadas se encadeiam

```
Pesquisa       @Historiador · `Design/Pesquisa/`
Criativo       @GameCreative · `Design/Criativo/`
Documentação   @GameArchitect · `Desenvolvimento/Docs/`
Implementação  Gameplay · Unity · Systems · Test · QA

Arte (lateral) @SpriteArtist + usuário · recebe pedido do Criativo, entrega em `Assets/Art/`
Orquestração (transversal) @AgentArchitect + @TechLead · sessões, auditorias, agentes, ADRs
```

## Regras que valem em todas as camadas

- **Modelo reativo** — Nenhum agente invoca outro. Cada camada escreve no TODO da seguinte e o usuário aciona.
- **Rotas de handoff** — Pesquisa→Criativo, Criativo→Documentação, Documentação→Implementação. Nunca pular camada sem pedido.
- **Fonte única de status** — Pendência vive só no TODO da camada; roadmap e backlog apenas linkam.
- **Aprovação humana** — Pesquisa armazenada, concept art, DDR e ADR só avançam com aprovação explícita do usuário.
- **Leitura econômica** — Índice primeiro, busca pelo tema depois; nunca abrir pasta inteira. Tetos verificados pelo `TokenBudgetTests`.

---

Ao mudar um modo de agente ou uma skill, atualize o arquivo da camada aqui. Catálogo de skills, travas e MCPs: [`../Tech/processos.md`](../Tech/processos.md).
