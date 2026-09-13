# Sistemas — Módulos Técnicos do Braziliation

> Um arquivo por sistema técnico do jogo. **É o índice de scripts do projeto:** a seção "Fontes Técnicas" de cada ficha lista os `.cs` do sistema.
> Para criar: `@GameArchitect Novo sistema: {Nome}`
> Template: [`../../Models/ModelSistema.md`](../../Models/ModelSistema.md)

## Conteúdo

| Sistema | Responsabilidade | Status |
|---------|-----------------|--------|
| [`Core.md`](Core.md) | Inicialização, câmera, service locator, input, layers e contratos | 🔨 Em Desenvolvimento |
| [`Gameplay.md`](Gameplay.md) | Player, vida, queda, câmera, animação e cena de demo | 🔨 Em Desenvolvimento |
| [`UI.md`](UI.md) | Menu, telas de save e configurações, HUDs | 🔨 Em Desenvolvimento |
| [`SaveSystem.md`](SaveSystem.md) | Persistência de slots de save e migrações | 🔨 Em Desenvolvimento |
| [`Serialization.md`](Serialization.md) | Serialização JSON dos dados de jogo | 🔨 Em Desenvolvimento |
| [`Settings.md`](Settings.md) | Configurações persistentes do jogador | 🔨 Em Desenvolvimento |
| [`Storage.md`](Storage.md) | Abstração de leitura/escrita em disco | 🔨 Em Desenvolvimento |
| [`Build.md`](Build.md) | Estado da build do personagem e sinergias híbridas | 🔨 Em Desenvolvimento |
| [`Crafting.md`](Crafting.md) | Componentes, receitas, receptáculos e itens híbridos | 🔨 Em Desenvolvimento |
| [`Enemies.md`](Enemies.md) | Motor de IA de inimigos por perfil | ✅ Motor implementado |
| [`Editor.md`](Editor.md) | Ferramentas do Unity Editor (import, sheets, WFC, cenas) | 🔨 Em Desenvolvimento |

> O `DocsConsistencyTests` falha se uma pasta de `src/Braziliation.Game.Core/` não tiver ficha aqui **ou** se algum `.cs` de `src/`, `Assets/Scripts/` ou `Assets/Editor/` não aparecer (entre crases) na "Fontes Técnicas" de alguma ficha.
