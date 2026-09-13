# GDD — Game Design Document

> O que o jogo **é**: features, decisões de design e, quando a premissa fechar, a visão e o loop principal.
> Agentes: `@GameplayEngineer` (referência de implementação) · `@GameArchitect` (features) · `@TechLead` (revisão)

## Conteúdo

| Seção | Descrição |
|-------|-----------|
| [`Features/`](Features/index.md) | 7 features de Blumenau (igrejas, teatro, sistema hídrico, Jardim de Edith, mausoléu, Morro do Zendron), documentadas e ainda não implementadas |
| `Decisoes/` | Registros de Decisão de Design (DDR) da skill `fechar-decisao` — a pasta nasce com o primeiro DDR |

## Onde vive a visão enquanto a premissa não fecha

- **Pilares e experiência-alvo:** `.github/instructions/game-vision.instructions.md`
- **Premissa, mundo e protagonista:** [`Design/Criativo/Historia/premissa.md`](../../../Design/Criativo/Historia/premissa.md) — ainda com placeholders
- **Mecânicas e sistemas:** [`../Mechanics/`](../Mechanics/index.md) e [`../Architecture/Sistemas/`](../Architecture/Sistemas/index.md)

`vision.md` (pitch, pilares, público) e `core_loop.md` nascem do DDR da premissa, não antes — sem premissa fechada eles só repetiriam placeholders. Depois, conforme a demo avançar: `levels.md` e `content_checklist.md`.

---

> Nova feature: `@GameArchitect Nova feature: {Nome}` · decisão de design: skill `fechar-decisao` (e atualizar a feature ou mecânica afetada)
