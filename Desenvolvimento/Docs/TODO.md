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
| Localização das benzedeiras (uma por região; a casa é o checkpoint?) e do ponto único do Monge João Maria — quando houver mapa | [DDR-001](GDD/Decisoes/DDR-001-benzedeira-npc.md) · [DDR-002](GDD/Decisoes/DDR-002-monge-joao-maria-papel.md) | Média | ❌ |

---

## Unity — validação no Editor e wiring

> Compilação e testes EditMode rodam sem abrir o Editor pela skill `unity-validar`. Os itens abaixo exigem o Editor aberto (ou o MCP `unity`).

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| *(nenhum pendente — o blockout do castelo foi concluído em 2026-11-04)* | | | |

---

## Gameplay

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Inventário completo: capacidade, categorias por pilar, persistência no save | `@SystemsDeveloper` + `@GameplayEngineer` | Média | ⏸ depende dos números de Crafting |
| Reação a dano (stagger) e percepção por linha de visão | `@GameplayEngineer` | Média | ❌ — ver [`Mechanics/InimigosIA.md`](Mechanics/InimigosIA.md) |
| Perfis de inimigo dos arquétipos de Blumenau (skill `novo-inimigo`) | `@GameCreative` + `@GameplayEngineer` | Média | ⏸ depende do inimigo base |
| Trocar o inimigo placeholder pelo `enm_automato_idle_sheet.png` — o código já trocou (`DemoSceneVisuals` aponta o autômato), falta a cena: o `Enemy_Demo` da `DemoGameplay.unity` ainda guarda sprite e sheets do cão do Gothicvania, e o `DemoSceneBootstrap` reaproveita o objeto. Trocar no próprio objeto, no Editor (sprite, `ResourcePath` dos clipes, collider); **não** usar `Braziliation > Demo > Create or Update Fixed Demo Scene`, que recria a cena do zero e apaga o que entrou nela depois | `@GameplayEngineer` | Média | ⏸ depende do inimigo base |
| Hit-stop, tremor e empurrão no `PlayerCombat`/`HealthComponent` lendo os `eventos` do JSON lateral do sheet (`congela`, `tremor`, `amp` — ADR-016); hoje o combate não tem nenhuma resposta de impacto. Lógica de tempo no core, MonoBehaviour só aplica | `@GameplayEngineer` | Média | ❌ — formato em [`animacao-por-esqueleto.md`](../../Design/GuiasDeArte/animacao-por-esqueleto.md) |

---

## UI e arte

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Slots de save por `SaveLoadStatus`: pagar a dívida "UI de slots trata `Corrupt` e `FromNewerBuild` como slot vazio" ([`Tech/tech_debt.md`](Tech/tech_debt.md)) pelo contrato de [`Sistemas/UI.md`](Architecture/Sistemas/UI.md) › Estado do slot. **Core:** `SaveLoadResult.CanOverwrite` (lista positiva `Empty`/`Ok`/`Migrated`/`Corrupt`), com xUnit escrito antes: um `[Theory]` com os 6 status e um teste que quebra se surgir status novo. **UI:** `SaveSlotsView` passa a usar `LoadDetailed` e registra no log os status bloqueados; `SaveSlotEntryView.Bind` recebe `SaveLoadResult`, ganha `unavailableSlotIndicator`, `statusLabel` e os textos, e define `interactable` por `IsUsable`/`CanOverwrite`. Nenhuma cena para religar: o `SaveSlotsPanel` ainda não tem entradas. Para fechar: `dotnet test` e `unity-validar` verdes, `CanOverwrite` na ficha `SaveSystem.md`, a frase "A UI de slots ainda trata…" do ADR-007 atualizada e a entrada removida do `tech_debt.md` | `@UnityDeveloper` + `@SystemsDeveloper` | Alta | ❌ |
| pxfx onda 1 — combate: portar e reescalar impacts, melee, projectiles, explosions, spawn, status e o resto de fire (90 arquivos), com paridade OK na escala 1, `--escala 2.5` corrigida e aprovação pelo [`vfx-guide.md`](../../Design/GuiasDeArte/vfx-guide.md) (skill `vfx`) | `@SpriteArtist` | Média | 🔨 `fire/torch` portado — ver [`pxfx/index.md`](../../Design/ArteFonte/Ferramentas/pxfx/index.md) |
| pxfx onda 2 — mundo: water, weather, lightning, scifi, critters, nature, ice (89 arquivos) | `@SpriteArtist` | Baixa | ⏸ depois da onda 1 |
| pxfx onda 3 — sobrenatural: holy, shadow, arcane redesenhados para lendas e clero (37 arquivos) | `@SpriteArtist` | Baixa | ⏸ depois da onda 2 |
| pxfx onda 4 — interface: ui, pickups, transitions (36 arquivos); ao fechar, remover `Ferramentas/vendor/pixelfx/` (o aviso MIT fica) | `@SpriteArtist` | Baixa | ⏸ depois da onda 3 |
| Armas na mão do esqueleto: portar os `WEAPONS` do `rig.js` (espada, lança, martelo, pistola, lançador...) e a busca de cotovelo de quem segura — as atuações da biblioteca pedem arma | `@SpriteArtist` | Média | ❌ |
| Decidir a camada emissiva do VFX: o brilho aditivo e a fumaça translúcida do `pxfx` reprovam no `palette_check`; opções: máscara emissiva do sprite no URP 2D, exceção de paleta para VFX, ou exportar sem luz | Usuário (arte) | Média | ❌ — contexto no [`vfx-guide.md`](../../Design/GuiasDeArte/vfx-guide.md) |
| Afinar os modelos do esqueleto por criatura ao criar cada uma: proporções do quadrúpede (Lobisomem) e da serpente (Minhocão, Boitatá), taxa de órfãos da transferência de pele (1,5% no teste) | `@SpriteArtist` | Baixa | ⏸ junto com cada personagem |
| Tirar os placeholders CC0 do Gothicvania do projeto quando a arte própria os substituir: remover `Assets/Art/ThirdParty/Gothicvania/`, a entrada no `Desenvolvimento/CREDITS.md`, a seção de terceiros do [`indices/assets.md`](Architecture/indices/assets.md), a lista `Legado` do `PixelScale` (vira constante de 48) e o `TilesetAutoSlicer` (só atua em `ThirdParty/`). Bloqueios por asset: herói (3 arquivos) ← protagonista; chão e tileset do castelo (o `CastleBlockoutEditor` fixa os nomes de sprite do Gothicvania) ← tile de topo e quina do `gen_tileset.py` (`Tech/tech_debt.md`); fundo ← ainda sem asset nem pendência; cão (3 arquivos) ← item do inimigo placeholder em Gameplay | `@SpriteArtist` + `@UnityDeveloper` | Baixa | ⏸ depende da premissa (protagonista) e do tile de borda |

---

## Ecossistema e processo

| Item | Responsável | Prioridade | Status |
|------|-------------|-----------|--------|
| Avaliar a janela de compactação do ADR-015 na página Tokens da Central depois de ~5 execuções com janela nas filas Unity, Gameplay e UI e arte: manter, ajustar ou voltar ao `auto`; e decidir se vale o passo seguinte por mod (esforço por requisição, saídas grandes encurtadas) | @TechLead | Média | ❌ Não iniciado |

---

## Sequência recomendada para a demo

1. `fechar-decisao`: premissa → inimigo base → arma inicial → números de Crafting e Build.
2. Play-teste no Editor (menu → demo) e wiring pendente da seção Unity.
3. `novo-inimigo` para o inimigo base; trocar o placeholder.
4. Inventário real no save.
5. UI e arte pendentes.
6. Checklist final da demo com o loop completo (combate + progressão + feedback).
