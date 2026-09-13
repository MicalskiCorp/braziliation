# Game Design Document (GDD) – Braziliation

Esta pasta guarda o que o jogo **é**: features, decisões de design e, quando a premissa for fechada, a visão e o loop principal. É a referência de `@GameplayEngineer`, `@TechLead` e `@GameArchitect` ao implementar ou revisar.

## O que existe hoje

| Onde | Conteúdo |
|------|----------|
| [`Features/`](Features/index.md) | 7 features de Blumenau (igrejas, teatro, sistema hídrico, Jardim de Edith, mausoléu, Morro do Zendron), todas documentadas e ainda não implementadas |
| `Decisoes/` | Registros de Decisão de Design (DDR), criados pela skill `fechar-decisao` — a pasta nasce com o primeiro DDR |

## Onde vive a visão enquanto a premissa não fecha

- **Pilares e experiência-alvo:** `.github/instructions/game-vision.instructions.md`
- **Premissa, mundo e protagonista:** `Design/Criativo/Historia/premissa.md` — ainda com placeholders
- **Mecânicas e sistemas:** [`../Mechanics/`](../Mechanics/index.md) e [`../Architecture/Sistemas/`](../Architecture/Sistemas/index.md)

## O que ainda vai existir

`vision.md` (pitch, pilares, público) e `core_loop.md` (explorar → combater → progredir) serão escritos a partir do DDR da premissa, não antes: sem premissa fechada, eles só repetiriam placeholders. Depois deles, conforme a demo avançar: `levels.md` (estrutura de mundo) e `content_checklist.md` (o que está desenhado × implementado).

## Uso

- Decisão de design mudou? Registrar num DDR (`fechar-decisao`) e atualizar a feature ou a mecânica afetada.
- Mudança na visão de alto nível: manter `game-vision.instructions.md` em sincronia.
