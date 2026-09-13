# Backlog — Braziliation

> Features e onde cada uma está documentada. Atualizado pelo `@GameArchitect` a cada feature nova.
> **Pendências e decisões abertas não ficam aqui** — vivem no [`TODO.md`](../TODO.md). Esta tabela diz só em que estágio a feature está.

## Features do núcleo

| Feature | Prioridade | Estágio | Documento |
|---------|-----------|--------|---------|
| Sistema de Crafting — Receptáculos | Alta | 🔁 Lógica pronta, números em aberto | [`Mechanics/Crafting.md`](../Mechanics/Crafting.md) |
| Build do Personagem — Receptáculos e Identidade | Alta | 🔁 Lógica pronta, números em aberto | [`Mechanics/Build.md`](../Mechanics/Build.md) |
| Player — Movimentação Básica (andar, pular, colisão) | Alta | ✅ Versão da demo | [`Sistemas/Gameplay.md`](../Architecture/Sistemas/Gameplay.md) |
| Combate Básico (vida, dano, ataque corpo a corpo) | Alta | ✅ Versão da demo — arma inicial definitiva é decisão aberta | [`Sistemas/Gameplay.md`](../Architecture/Sistemas/Gameplay.md) |
| Inimigo Básico (patrulha, detecção, dano) | Alta | ✅ Motor `EnemyBrain` + inimigo placeholder — inimigo base definitivo é decisão aberta | [`Mechanics/InimigosIA.md`](../Mechanics/InimigosIA.md) |
| Primeira Cena Jogável (blockout + tilemap) | Alta | ✅ Versão da demo | [`Sistemas/Gameplay.md`](../Architecture/Sistemas/Gameplay.md) |
| HUD Básico (barra de vida, build ativa) | Média | ✅ Versão da demo | [`Sistemas/UI.md`](../Architecture/Sistemas/UI.md) |
| Bootstrap Scene (GameServiceLocator + serviços) | Alta | ✅ Concluído | [`Sistemas/Core.md`](../Architecture/Sistemas/Core.md) |

## Features de Conteúdo (Blumenau — design pronto, implementação futura)

| Feature | Prioridade | Estágio | Documento |
|---------|-----------|--------|---------|
| Blumenau — Igreja Luterana Matriz + SQ Hermann | Alta | 📋 Planejado | [`GDD/Features/Blumenau-IgrejaLuterana.md`](../GDD/Features/Blumenau-IgrejaLuterana.md) |
| Blumenau — Igreja Matriz do Centro + Podres de Ricos | Alta | 📋 Planejado | [`GDD/Features/Blumenau-IgrejaMatriz.md`](../GDD/Features/Blumenau-IgrejaMatriz.md) |
| Blumenau — Teatro Carlos Gomes + mercado negro + boss Autômato | Alta | 📋 Planejado | [`GDD/Features/Blumenau-TeatroCarlosGomes.md`](../GDD/Features/Blumenau-TeatroCarlosGomes.md) |
| Blumenau — Sistema Hídrico (4 estados) | Alta | 📋 Planejado | [`GDD/Features/Blumenau-SistemaHidrico.md`](../GDD/Features/Blumenau-SistemaHidrico.md) |
| Blumenau — Jardim de Edith + SQ-01 + Guizo de Edith | Alta | 📋 Planejado | [`GDD/Features/Blumenau-JardimEdith.md`](../GDD/Features/Blumenau-JardimEdith.md) |
| Blumenau — Mausoléu do Fundador + catacumba | Média | 📋 Planejado | [`GDD/Features/Blumenau-MausoleumFundador.md`](../GDD/Features/Blumenau-MausoleumFundador.md) |
| Blumenau — Morro do Zendron + mapas periféricos | Média | 📋 Planejado | [`GDD/Features/Blumenau-MorroZendron.md`](../GDD/Features/Blumenau-MorroZendron.md) |

## Legenda de Estágio

| Ícone | Estágio |
|-------|--------|
| 📋 | Planejado |
| 🔨 | Em desenvolvimento |
| 🔁 | Em revisão |
| ✅ | Concluído (a coluna diz se é versão da demo) |
| ⏸️ | Pausado |

---

> Ao documentar feature nova: linha com `📋 Planejado` e link para `GDD/Features/{Contexto}-{Nome}.md`.
