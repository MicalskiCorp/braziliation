---
description: "Padrões de código C# do Braziliation: namespaces, convenções Unity, lifecycle, prefabs, ScriptableObjects e Git. Aplicado automaticamente a todos os arquivos .cs do projeto."
applyTo: "Desenvolvimento/Assets/**/*.cs,Desenvolvimento/src/**/*.cs,Desenvolvimento/Tests/**/*.cs"
---
# Coding Standards – Braziliation

## Language and engine

- **Language:** C#
- **Engine:** Unity 6 (6000.2), URP 2D
- **Input:** com.unity.inputsystem via `Braziliation.Core.GameInput` — ADR-006.
  Nunca leia `Keyboard.current`/`Mouse.current`/`Gamepad.current` em gameplay.
- **Target:** PC (Steam)

## Namespaces

Namespace raiz: `Braziliation`. Subnamespaces espelham pastas em `Assets/Scripts/`.
Organização por **domínio de sistema**, não por tipo de entidade — ver ADR-005:

| Pasta | Namespace |
|-------|-----------|
| `Core/` | `Braziliation.Core` |
| `Gameplay/` | `Braziliation.Gameplay` |
| `Build/` | `Braziliation.Build` |
| `Crafting/` | `Braziliation.Crafting` |
| `Enemies/` | `Braziliation.Enemies` |
| `UI/` | `Braziliation.UI` |

`Braziliation.Build` e `Braziliation.Crafting` existem também em
`src/Braziliation.Game.Core/` (adaptador Unity × lógica pura). Nomes de tipo não podem
colidir entre as duas camadas.

## Script layout

- **Uma responsabilidade por script.** Sem god classes.
- **Nomes:** PascalCase para types e membros públicos; camelCase para campos privados. MonoBehaviours com sufixo descritivo (`PlayerController`, `EnemyPatrol`).
- **Inspector:** Use `[Header]`, `[Tooltip]`, `[Range]` onde útil. Serialize apenas o que designers precisam ajustar. Use `[SerializeField]` — nunca `public` para campos Unity.
- **Lifecycle:** `FixedUpdate` para física; sem lógica pesada em `Update`. Use events/coroutines para lógica adiada ou pontual.

## Unity conventions

- **Pixel Perfect:** Respeite 640×360 e 32 PPU. Nenhum scaling arbitrário que quebre alinhamento de pixel.
- **Physics 2D:** Use `Rigidbody2D` e `Collider2D`; configure layers e matrix em Project Settings.
- **Prefabs:** Um prefab por entidade lógica (player, tipo de inimigo, projétil). Variants para tuning.
- **ScriptableObjects:** Para dados em tempo de design (stats, definições de item, wave configs). Estado de runtime fica em components.
- **Business logic:** Zero em MonoBehaviours de UI — eles apenas chamam serviços. Toda lógica vive em `Braziliation.Game.Core` (C# puro).

## Pure C# systems (`src/Braziliation.Game.Core/`)

- Zero dependência de `UnityEngine.*` ou `UnityEditor.*`.
- Serviços recebem todas as dependências via construtor (sem estado estático).
- Caminhos de arquivo nunca hardcoded — sempre injetados na construção.
- Serialização com `System.Text.Json` + `SaveJsonOptions.Default`.
- Mudou o schema de save? Suba `SaveSlot.CurrentSchemaVersion` **e** registre o degrau
  em `SaveMigrations.All` — ADR-007. Há teste que trava o esquecimento.

## Definição de pronto (qualquer mudança em `.cs`)

Espelho de `.claude/rules/csharp.md`. Vale para qualquer agente que toque código.

- **Core puro:** teste xUnit primeiro (contrato → falha → implementação → passa); `dotnet test` verde.
- **Script em `Assets/`:** `py .claude/skills/unity-validar/scripts/validar.py` compilando; `.meta` dos arquivos novos no commit.
- **Script novo, renomeado ou movido:** linha na "Fontes Técnicas" da ficha em `Desenvolvimento/Docs/Architecture/Sistemas/` — o `DocsConsistencyTests` cobra.
- **Atalho tomado** → `Docs/Tech/tech_debt.md`; **ponto incompleto** → `Docs/TODO.md` (nunca só `// TODO`).
- **Decisão estrutural** → ADR em `Docs/Architecture/architecture_decisions.md`.

## Git and workflow

- Siga `Docs/Tech/DevelopmentRules.md`: nomenclatura de branches, formato de commit `tipo(scope): descrição`, PR e CI.
- Não remova nem reestruture `Assets/`, `Packages/`, `ProjectSettings/` além do combinado.
