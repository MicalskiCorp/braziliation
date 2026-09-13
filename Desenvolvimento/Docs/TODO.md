# TODO — Pendências vivas (Desenvolvimento)

> Só o que está **aberto**. Item concluído sai daqui com a data e o commit; o histórico até 2026-09-13 está em [`TODO-arquivo.md`](TODO-arquivo.md).
> **Modelo reativo:** o `@GameArchitect` lê este arquivo no Passo 0. Handoffs do `@GameCreative` chegam na primeira seção e são processados manualmente pelo usuário.
> Status: ❌ não iniciado · 🔨 em andamento · ⏸ bloqueado/aguardando · ✅ concluído (e então arquivar).

---

## Handoffs do @GameCreative

| Feature/Sistema | Referência Criativa | Prioridade | Status |
|----------------|---------------------|-----------|--------|
| *(nenhum pendente — os 7 de Blumenau foram processados em 2026-05-17)* | | | |

---

## Decisões de design — bloqueiam a demo

> Fechar com a skill `fechar-decisao` (gera um DDR em `GDD/Decisoes/`). A premissa vem antes das outras.

| Decisão | Referência | Prioridade | Status |
|---------|-----------|-----------|--------|
| Premissa: pitch, contexto do mundo, protagonista | [`premissa.md`](../../Design/Criativo/Historia/premissa.md) | Alta | ❌ |
| Inimigo básico da demo (comportamento, vida, dano) — o Autômato Abandonado já tem sprite | [`Mechanics/InimigosIA.md`](Mechanics/InimigosIA.md) | Alta | ❌ |
| Arma inicial do jogador (tipo, dano base, animação) | [`GDD/`](GDD/) | Alta | ❌ |
| Parâmetros numéricos de Crafting (slots iniciais/máximos, expansões, combinações híbridas) | [`Mechanics/Crafting.md`](Mechanics/Crafting.md) | Alta | ❌ |
| Parâmetros numéricos de Build (habilidades por receptáculo, resistências, estágios visuais) | [`Mechanics/Build.md`](Mechanics/Build.md) | Alta | ❌ |
| IDs dos materiais especiais de expansão (Artesão/Costureira/Alquimista) | [`Mechanics/Build.md`](Mechanics/Build.md) | Alta | ❌ |
| Regras de compatibilidade e composição final dos itens híbridos | [`Sistemas/Crafting.md`](Architecture/Sistemas/Crafting.md) | Alta | ❌ |
| Política de seed do sorteio híbrido (determinístico × aleatório) | [`Sistemas/Crafting.md`](Architecture/Sistemas/Crafting.md) | Média | ❌ |
| Localização e quantidade de totens | [`Mechanics/Build.md`](Mechanics/Build.md) | Média | ❌ |

---

## Unity — validação no Editor e wiring

> Compilação e testes EditMode rodam sem abrir o Editor pela skill `unity-validar`. Os itens abaixo exigem o Editor aberto (ou o MCP `unity`).

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Ativar a licença Unity Personal na máquina (Hub → Preferences → Licenses → Add). Sem isso os testes EditMode não rodam por linha de comando (`unity-validar --testes` sai com 198); a compilação já funciona | Usuário | Alta | ❌ |
| Play-teste da demo: `MainMenu` (movido para `Scenes/Menus/` em 2026-09-13) → `DemoGameplay`; animação trocando quadro, pulo só no chão, inimigo virando na ponta, ataque sem auto-dano | `@UnityDeveloper` | Alta | ❌ |
| Conectar o MCP `unity`: abrir o Editor com o pacote `com.unity.pipeline` (adicionado em 2026-09-13) e confirmar `unity status` | Usuário + `@UnityDeveloper` | Média | ❌ |
| Conferir o slicing do `SheetAutoSlicer` e gerar Animators (alavanca, sino, Autômato) | `@UnityDeveloper` | Média | ❌ |
| Prefab `Prop_FloodgateLever` em `Prefabs/Interactables/` | `@UnityDeveloper` | Média | ❌ |
| Integrar a alavanca ao sistema hídrico de Blumenau | `@GameplayEngineer` | Média | ❌ |
| Executar o `WfcMapImporter` com `Design/ArteFonte/IA/Outputs/wfc-teste/blumenau_s42.unity.json` | `@UnityDeveloper` | Média | ❌ |
| Configurar os secrets do GameCI para o workflow `unity-ci.yml` | Usuário | Média | ❌ — ver [`Tech/unity-ci.md`](Tech/unity-ci.md) |
| Conferir a matriz de colisão 2D das layers Ground/Player/Enemy | `@UnityDeveloper` | Baixa | ❌ |
| Fatiar `env_placeholder_castelo_tileset.png` e montar blockout com Tilemap | `@UnityDeveloper` | Baixa | ❌ opcional |

---

## Gameplay

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Inventário completo: capacidade, categorias por pilar, persistência no save | `@SystemsDeveloper` + `@GameplayEngineer` | Média | ⏸ depende dos números de Crafting |
| Reação a dano (stagger) e percepção por linha de visão | `@GameplayEngineer` | Média | ❌ — ver [`Mechanics/InimigosIA.md`](Mechanics/InimigosIA.md) |
| Perfis de inimigo dos arquétipos de Blumenau (skill `novo-inimigo`) | `@GameCreative` + `@GameplayEngineer` | Média | ⏸ depende do inimigo base |
| Trocar o inimigo placeholder pelo `enm_automato_idle_sheet.png` | `@GameplayEngineer` | Média | ⏸ depende do inimigo base |

---

## UI e arte

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Onda 3: veredito do lote 12 da Edith (teto de 3 lotes por ajuste) e curadoria dos thumbnails do Soldado Clérico | Usuário + `@SpriteArtist` | Média | 🔨 |
| Onda 2 restante: tilesets pedra portuguesa, cemitério/terra, mármore, periferia pós-enchente | `@SpriteArtist` | Média | ❌ |
| Clipes de ataque, dano e morte (o placeholder só tem idle/run/walk) | `@SpriteArtist` | Média | ⏸ com a arte própria |
| Prefab final do painel de crafting | `@UnityDeveloper` | Média | ❌ |
| Progressão visual da build (sprites por estágio de receptáculo) | `@SpriteArtist` + `@UnityDeveloper` | Média | ❌ |
| VFX e feedback de sinergias híbridas | `@SpriteArtist` + `@UnityDeveloper` | Média | ❌ |
| Props narrativos, ícones de crafting, VFX | `@SpriteArtist` | Baixa | ❌ |
| Pixel pass da comporta (dentes de engrenagem mais legíveis) — agora possível pelo MCP `aseprite` | `@SpriteArtist` | Baixa | ❌ opcional |
| Substituir os placeholders Gothicvania e remover `Art/ThirdParty/` + `CREDITS.md` | `@SpriteArtist` | Baixa | ⏸ quando a Onda 3 entregar personagens |
| Rampas estendidas da paleta Blumenau (16 → até 32 cores) | Usuário (arte) | Baixa | ⏸ quando a arte final pedir |

---

## Ecossistema e processo

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Avaliar as 13 skills com o plugin `skill-creator` (modo Eval) | `@AgentArchitect` | Baixa | ❌ |
---

## Sequência recomendada para a demo

1. `fechar-decisao`: premissa → inimigo base → arma inicial → números de Crafting e Build.
2. Play-teste no Editor (menu → demo) e wiring pendente da seção Unity.
3. `novo-inimigo` para o inimigo base; trocar o placeholder.
4. Inventário real no save.
5. UI e arte pendentes.
6. Checklist final da demo com o loop completo (combate + progressão + feedback).
