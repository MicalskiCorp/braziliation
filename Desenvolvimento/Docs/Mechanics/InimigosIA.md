# IA de Inimigos — Motor Genérico

> **Status:** ✅ Implementado (motor + inimigo básico da demo) · Criado em 2026-07-27
> Agentes: `@SystemsDeveloper` (motor C# puro) · `@GameplayEngineer` (adaptador Unity) · `@GameCreative` (arquétipos)

## Ideia central

**Um motor, muitos inimigos.** O comportamento não é reescrito por inimigo: é descrito por
dados. Criar um inimigo novo é criar um perfil, não uma classe.

A decisão fica em C# puro, sem Unity — assim ela é testável sem abrir o editor e o mesmo
cérebro serve para qualquer corpo (chão, voador, boss por fases).

```
   mundo Unity                 C# puro (Braziliation.Game.Core)
┌────────────────────┐      ┌──────────────────────────────────┐
│ EnemyController    │      │  EnemyBrain                      │
│  (adaptador)       │      │                                  │
│                    │      │   perfil (dados) ─┐              │
│  lê sensores  ─────┼─────►│  EnemySenses      ├─► máquina    │
│                    │      │                   │   de estados │
│  aplica no corpo ◄─┼──────┤  EnemyIntent   ◄──┘              │
└────────────────────┘      └──────────────────────────────────┘
```

O `EnemyController` **não decide nada**. Ele só lê o mundo (chão, parede, precipício, alvo,
vida), entrega ao cérebro, e aplica a decisão no `Rigidbody2D`.

## Peças

| Peça | Onde | Papel |
|------|------|-------|
| `EnemyBrain` | `src/Braziliation.Game.Core/Enemies/` | Máquina de estados determinística. Único lugar com regra de comportamento |
| `EnemyBehaviorProfile` | idem | Dados do arquétipo: velocidades, raios, tempos, estilo |
| `EnemySenses` / `EnemyIntent` | idem | Entrada e saída de um tick. Fronteira entre engine e lógica |
| `EnemyController` | `Assets/Scripts/Gameplay/` | Adaptador Unity: sensores por raycast + aplicação no corpo |
| `EnemyProfileAsset` | `Assets/Scripts/Enemies/` | ScriptableObject para editar o perfil no Inspector |
| `EnemySpriteAnimation` | `Assets/Scripts/Gameplay/` | Traduz o estado da IA em clipe de animação |

Testes: `Tests/Braziliation.Game.Tests/EnemyBrainTests.cs` (25 testes, incluem regressão de
"anda para sempre até cair do mapa").

## Estados

| Estado | Quando | O que faz |
|--------|--------|-----------|
| `Idle` | Sem alvo e sem patrulha (ou pausa na ponta) | Parado |
| `Patrol` | Sem alvo, com faixa de patrulha | Vai e volta entre âncora ± alcance |
| `Alert` | Acabou de avistar o alvo | Parado, encarando, durante a janela de reação |
| `Chase` | Alvo adquirido e fora do alcance de ataque | Vai na direção do alvo |
| `Reposition` | Só `Skirmisher`: alvo perto demais | Recua **sem dar as costas** |
| `Attack` | Alvo no alcance e cooldown pronto | Preparação → pulso de dano |
| `Returning` | Perdeu o alvo longe da âncora | Volta para o posto |
| `Flee` | Vida abaixo do limiar do perfil | Foge na direção oposta |
| `Dead` | Vida zerada | Não age mais |

### Regras que sustentam a leitura do jogador

- **Histerese de alvo.** Adquire no `DetectRadius`, só larga no `LoseTargetRadius` (maior).
  Sem isso o inimigo pisca entre perseguir e patrulhar na borda do raio.
- **Janela de reação.** `ReactionSeconds` entre avistar e agir. É o que dá ao jogador a
  chance de reagir; inimigo que gruda no mesmo frame lê como injusto.
- **Coleira (`LeashRadius`).** Distância máxima da âncora perseguindo. Passou, desiste e
  volta — impede puxar o mapa inteiro atrás de você.
- **Preparação de ataque (`AttackWindupSeconds`).** O golpe é telegrafado: o estado entra em
  `Attack` antes de o dano sair. É onde a animação de ataque encaixa.
- **Sensores de terreno.** Precipício e parede à frente fazem virar na patrulha e travam o
  avanço na perseguição. É o que impede o inimigo de andar para fora do mapa.

## Estilos de agressão

O estilo muda a *forma* de agir, não só os números. Dois inimigos com a mesma velocidade e o
mesmo raio se comportam diferente:

| Estilo | Comportamento | Uso pretendido em Braziliation |
|--------|---------------|-------------------------------|
| `Patroller` | Patrulha e persegue quem entra no raio | Bicho de rua, mutante de periferia |
| `Sentry` | Não patrulha; guarda um ponto e ataca quem chega | Soldado clérico de porta, torre |
| `Charger` | Espera parado; ao detectar, avança sem recuar | Investida pesada, autômato |
| `Skirmisher` | Mantém distância preferida; recua se você aproxima | Inimigo de ataque à distância |
| `Ambusher` | Imóvel até você chegar muito perto (metade do raio) | Emboscada em catacumba |

## Como adicionar um inimigo novo

1. **Sem código**, no caso comum: `Assets > Create > Braziliation > Inimigos > Perfil de
   Comportamento`, ajuste os números e o estilo, salve em `Assets/ScriptableObjects/Enemies/`.
2. No prefab do inimigo: `SpriteRenderer` + `Rigidbody2D` + `Collider2D` + `HealthComponent`
   + `EnemyController`, apontando o campo **Perfil** para o asset.
3. Camada do objeto = `Enemy`; `_groundMask` = `Ground`; `_targetMask` = `Player`.
4. Animação: `SpriteSheetAnimator` com os clipes + `EnemySpriteAnimation`.

**Quando escrever código:** só quando o comportamento não couber em nenhum estilo — por
exemplo, boss com fases, inimigo que chama reforço, padrão de tiro. O caminho é adicionar um
estilo novo ao `EnemyAggressionStyle` e o ramo correspondente em `MoveWhileEngaged`, com
teste em `EnemyBrainTests`.

## Convenções

- **Determinismo.** Sem `Random` e sem relógio global: a mesma sequência de sentidos produz
  a mesma sequência de intenções. Isso é o que torna o comportamento testável e o replay
  possível. Variação aleatória, quando entrar, deve receber seed explícita.
- **Pivot no centro-inferior.** `transform.position` é o pé do inimigo; os sensores partem daí.
- **Um tick por passo de física.** `Tick` é chamado no `FixedUpdate` com `fixedDeltaTime`.

## Pendências

| Item | Prioridade | Observação |
|------|-----------|------------|
| Definir os arquétipos reais de Blumenau e criar os `EnemyProfileAsset` correspondentes | Alta | Depende de decisão de design (ver TODO: "inimigo básico da demo") |
| Reação a dano (recuo/stagger) e estado `Stunned` | Média | Hoje levar dano não interrompe o inimigo |
| Percepção por linha de visão (hoje é só distância) | Média | Inimigo "vê" através de parede |
| Voo / nado (perfis sem gravidade) | Baixa | O cérebro já não assume chão; falta o corpo |
| Grupos e alerta em cadeia | Baixa | Um inimigo avistar acordar os vizinhos |
