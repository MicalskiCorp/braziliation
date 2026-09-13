# Sistema: Gameplay

> **Responsabilidade:** MonoBehaviours de jogo — movimento e combate do jogador, vida, queda, câmera, animação por spritesheet e montagem da cena de demo.
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `PlayerController.cs` | `Assets/Scripts/Gameplay/PlayerController.cs` | Andar, pular e interagir; implementa `IStatReceiver` |
| `PlayerCombat.cs` | `Assets/Scripts/Gameplay/PlayerCombat.cs` | Ataque corpo a corpo em área curta |
| `PlayerSpriteAnimation.cs` | `Assets/Scripts/Gameplay/PlayerSpriteAnimation.cs` | Liga o estado do `PlayerController` aos clipes e espelha o sprite |
| `HealthComponent.cs` | `Assets/Scripts/Gameplay/HealthComponent.cs` | Vida e dano de player e inimigos; implementa `IDamageable` |
| `FallRespawn.cs` | `Assets/Scripts/Gameplay/FallRespawn.cs` | Devolve ao spawn quem cai abaixo do limite do mapa |
| `SimpleCameraFollow.cs` | `Assets/Scripts/Gameplay/SimpleCameraFollow.cs` | Follow da câmera ortográfica da demo |
| `SpriteSheetAnimator.cs` | `Assets/Scripts/Gameplay/SpriteSheetAnimator.cs` | Animação por troca de quadro montada em runtime a partir do sheet fatiado |
| `DemoSceneBootstrap.cs` | `Assets/Scripts/Gameplay/DemoSceneBootstrap.cs` | Monta em runtime a cena mínima: locator, build, chão, player, inimigo e HUD |
| `DemoAutoBootstrapper.cs` | `Assets/Scripts/Gameplay/DemoAutoBootstrapper.cs` | Garante o bootstrap de demo em cenas que não são de menu |
| `DemoSceneVisuals.cs` | `Assets/Scripts/Gameplay/DemoSceneVisuals.cs` | Fonte única de aparência e geometria da demo (runtime e cena fixa) |

Os adaptadores de inimigo (`EnemyController.cs`, `EnemySpriteAnimation.cs`) moram nesta pasta, mas são documentados em [Enemies](Enemies.md).

## Features que Usam Este Sistema

| Feature | Arquivo | Relação |
|---------|---------|---------|
| *(nenhuma documentada ainda)* | — | — |

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [Core](Core.md) | `GameInput.cs`, `GameLayers.cs`, `IDamageable.cs`, `IStatReceiver.cs` | Input pelo action map, layers nomeadas e contratos de dano/atributo |
| [Build](Build.md) | `PlayerBuildController.cs` | Envia ao `PlayerController` os atributos calculados pela build |
| [Enemies](Enemies.md) | `EnemyController.cs` | Inimigo da demo |
| [UI](UI.md) | `SimpleHealthHud.cs`, `CanvasHealthHud.cs` | HUD de vida lê o `HealthComponent` |

## Parâmetros Configuráveis

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|-------------|-----------|
| *(a documentar — dependem das decisões de arma inicial e inimigo base no `TODO.md`)* | — | — | — |

## Notas de Design

- Os scripts `Demo*` são andaime da demo com placeholders CC0; saem quando houver cena de nível real.
- `HealthComponent` emite `OnHealthChanged` no `Awake` — ver `Tech/tech_debt.md`.
