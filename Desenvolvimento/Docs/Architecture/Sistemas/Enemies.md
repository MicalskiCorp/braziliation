# Sistema: Enemies

> **Responsabilidade:** Motor de IA de inimigos — máquina de estados determinística que decide a partir de um perfil de dados. Inimigo novo é perfil, não classe.
> **Status:** ✅ Motor implementado e testado · Guia de uso: [`Mechanics/InimigosIA.md`](../../Mechanics/InimigosIA.md) · Skill: `novo-inimigo`

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `EnemyBehaviorProfile.cs` | `src/Braziliation.Game.Core/Enemies/EnemyBehaviorProfile.cs` | Números e estilo de agressão que definem um inimigo |
| `EnemySenses.cs` | `src/Braziliation.Game.Core/Enemies/EnemySenses.cs` | O que o inimigo percebe a cada passo (alvo, distância, parede, precipício, vida) |
| `EnemyBrain.cs` | `src/Braziliation.Game.Core/Enemies/EnemyBrain.cs` | Máquina de estados: sentidos + tempo → intenção |
| `EnemyProfileAsset.cs` | `Assets/Scripts/Enemies/EnemyProfileAsset.cs` | ScriptableObject que expõe o perfil no Inspector |
| `EnemyController.cs` | `Assets/Scripts/Gameplay/EnemyController.cs` | Adaptador Unity: física → sentidos; intenção → movimento/ataque |
| `EnemySpriteAnimation.cs` | `Assets/Scripts/Gameplay/EnemySpriteAnimation.cs` | Escolhe o clipe pelo estado da IA |

Testes: `EnemyBrainTests.cs` (25 casos).

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [Core](Core.md) | `GameLayers.cs`, `IDamageable.cs` | Máscaras de física e dano |

## Notas de Design

- Determinístico por construção: sem `Random` e sem relógio global — a mesma sequência de sentidos produz a mesma sequência de intenções.
- Pendências: reação a dano (stagger), percepção por linha de visão e os perfis dos arquétipos de Blumenau (bloqueados pela decisão do inimigo base).
