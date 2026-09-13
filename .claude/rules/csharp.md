---
paths:
  - "Desenvolvimento/Assets/**/*.cs"
  - "Desenvolvimento/src/**/*.cs"
  - "Desenvolvimento/Tests/**/*.cs"
---

# Padrões de código C# — Braziliation

Espelha `.github/instructions/coding-standards.instructions.md` (Copilot). Ao mudar um,
mude o outro.

## Contexto

C# · Unity 6 (6000.2) URP 2D · New Input System · alvo PC (Steam) · 640×360 @ 32 PPU.

## Namespaces reais

Namespace raiz `Braziliation`. Layout por domínio conforme ADR-005 (que substituiu o
ADR-003). Script novo vai para a pasta do domínio, não do tipo de entidade.

| Camada | Pasta | Namespace |
|--------|-------|-----------|
| Unity | `Assets/Scripts/Core/` | `Braziliation.Core` |
| Unity | `Assets/Scripts/Gameplay/` | `Braziliation.Gameplay` |
| Unity | `Assets/Scripts/Build/` | `Braziliation.Build` |
| Unity | `Assets/Scripts/Crafting/` | `Braziliation.Crafting` |
| Unity | `Assets/Scripts/Enemies/` | `Braziliation.Enemies` |
| Unity | `Assets/Scripts/UI/` | `Braziliation.UI` |
| Core puro | `src/.../SaveSystem/` | `Braziliation.SaveSystem` |
| Core puro | `src/.../Settings/` | `Braziliation.Settings` |
| Core puro | `src/.../Storage/` | `Braziliation.Storage` |
| Core puro | `src/.../Enemies/` | `Braziliation.Enemies` |

`Braziliation.Build` e `Braziliation.Crafting` existem nas **duas** camadas (adaptador
Unity + lógica pura). Ao adicionar tipo nesses namespaces, confira que o nome não colide
com um tipo da DLL — a ambiguidade só aparece em tempo de compilação no Unity.

## Regras de script

- Uma responsabilidade por script. Sem god classes.
- PascalCase para tipos e membros públicos; `_camelCase` para campos privados.
- `[SerializeField]` sempre; **nunca** campo `public` para expor no Inspector.
- `[Header]`, `[Tooltip]`, `[Range]` onde ajudam o designer. Serialize só o que se ajusta.
- `FixedUpdate` para física. Nada pesado em `Update`.
- Zero lógica de negócio em MonoBehaviour de UI — UI chama serviço.

## Core puro (`src/Braziliation.Game.Core/`)

- **Zero** `using UnityEngine.*` ou `UnityEditor.*`. Isso é verificável e não negociável:
  é o que mantém o core testável sem editor e portável para outra engine.
- Dependências por construtor. Sem estado estático.
- Caminho de arquivo nunca hardcoded — sempre injetado.
- Serialização com `System.Text.Json` + `SaveJsonOptions.Default`.
- Alvo `netstandard2.1`, `LangVersion 10.0` — não use sintaxe de C# mais nova.

## Testes

xUnit (`[Fact]` / `[Theory]`). NUnit foi removido. Test doubles em `TestDoubles.cs`.
Todo serviço novo em `src/` nasce com teste de happy path + edge case + falha.

## Definição de pronto (qualquer mudança em `.cs`)

Vale para qualquer agente ou sessão que toque código — por isso vive aqui, e não repetida em
cada agente.

- **Core puro:** teste xUnit primeiro (contrato → falha → implementação → passa); `dotnet test` verde.
- **Script em `Assets/`:** skill `unity-validar` compilando; `.meta` dos arquivos novos no commit (`meta-check`).
- **Script novo, renomeado ou movido:** linha na "Fontes Técnicas" da ficha em
  `Desenvolvimento/Docs/Architecture/Sistemas/` — o `DocsConsistencyTests` cobra.
- **Atalho tomado** → `Docs/Tech/tech_debt.md`; **ponto incompleto** → `Docs/TODO.md` (nunca só `// TODO`).
- **Decisão estrutural** → ADR pela skill `novo-adr`.

## Unity

- Pixel perfect: 640×360, 32 PPU. Nenhum scaling arbitrário que quebre alinhamento.
- `Rigidbody2D`/`Collider2D`; layers via `GameLayers`, nunca índice mágico.
- Um prefab por entidade lógica; Variants para tuning.
- ScriptableObject para dado de design; estado de runtime fica em componente.
- **Input:** use o action map de `Assets/InputSystem_Actions.inputactions`. Não adicione
  polling novo de `Keyboard.current`/`Mouse.current`/`Gamepad.current` — isso quebra
  rebind, Steam Input e Steam Deck.
