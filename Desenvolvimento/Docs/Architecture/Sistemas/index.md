# Sistemas — Módulos Técnicos do Braziliation

> Um arquivo por sistema técnico do jogo. Ligado a [`../indices/sistemas.md`](../indices/sistemas.md).
> Para criar: `@GameArchitect Novo sistema: {Nome}`
> Template: [`../../Models/ModelSistema.md`](../../Models/ModelSistema.md)

## Conteúdo

| Sistema | Responsabilidade | Status |
|---------|-----------------|--------|
| [`Core.md`](Core.md) | Inicialização, câmera e service locator | 🔨 Em Desenvolvimento |
| [`UI.md`](UI.md) | Menu, telas de save e configurações | 🔨 Em Desenvolvimento |
| [`SaveSystem.md`](SaveSystem.md) | Persistência de slots de save | 🔨 Em Desenvolvimento |
| [`Serialization.md`](Serialization.md) | Serialização JSON dos dados de jogo | 🔨 Em Desenvolvimento |
| [`Settings.md`](Settings.md) | Configurações persistentes do jogador | 🔨 Em Desenvolvimento |
| [`Storage.md`](Storage.md) | Abstração de leitura/escrita em disco | 🔨 Em Desenvolvimento |
| [`Build.md`](Build.md) | Estado da build do personagem e sinergias híbridas | 🔨 Em Desenvolvimento |
| [`Crafting.md`](Crafting.md) | Componentes, receitas, receptáculos e itens híbridos | 🔨 Em Desenvolvimento |
| [`Enemies.md`](Enemies.md) | Motor de IA de inimigos por perfil | ✅ Motor implementado |

> Cada pasta de `src/Braziliation.Game.Core/` precisa de uma página aqui — o `DocsConsistencyTests` falha se faltar.
