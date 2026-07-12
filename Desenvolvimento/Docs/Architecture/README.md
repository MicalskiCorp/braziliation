# Architecture — Braziliation

Esta pasta guarda a documentação de **arquitetura técnica**: limites de sistema, fluxo de dados e estrutura recomendada do projeto.

> Índice navegável completo em [`index.md`](index.md) — este arquivo é uma visão geral introdutória.

## Propósito

- Definir **limites de módulo**: Core, Player, Enemies, Combat, Inventory, World, UI, Utils.
- Documentar **fluxo de dados** e dependências (quem chama quem, eventos, interfaces).
- Descrever a **estrutura recomendada do projeto Unity** (ver `Assets/AssetsStructure.md`).
- Apoiar **agentes de IA** e futuros desenvolvedores com um "mapa" claro do código.

## Conteúdo

- [`index.md`](index.md) — índice navegável desta pasta (Sistemas, indices, motor, ADRs, Assets).
- [`Assets/AssetsStructure.md`](Assets/AssetsStructure.md) — layout recomendado sob `Assets/` e o que cada pasta contém.
- [`Sistemas/`](Sistemas/index.md) — fichas técnicas de cada sistema do jogo.
- [`architecture_decisions.md`](architecture_decisions.md) — ADRs (decisões de arquitetura aceitas).

## Uso

- `@TechLead` mantém estes docs, define limites de sistema e registra ADRs.
- `@UnityDeveloper` e `@GameplayEngineer` posicionam código novo conforme `Assets/AssetsStructure.md` e os limites de sistema definidos aqui.
- `@GameArchitect` mantém `Sistemas/` e `indices/` sincronizados com o código-fonte (ver `indices/protocolo-comunicacao.md`).
- Decisões estruturais significativas viram entrada em `Docs/Architecture/architecture_decisions.md`.
