# Template de Especificação de Variações (Passo 3)

Use este modelo para **personagens, inimigos e objetos com múltiplas ações/estados** — o Passo 3 do fluxo concept art → spec JSON → sprite (ver [`pipeline-sprites-programaticos.md`](pipeline-sprites-programaticos.md#fluxo-completo-da-ideia-ao-sprite-5-etapas)).

Para um prop simples (1 estado ou 1 acionamento curto), este passo é **opcional**: o campo "Animações necessárias" do [`asset-brief-template.md`](asset-brief-template.md) ou do [`context-pack-template.md`](context-pack-template.md) já basta. Use este template quando o asset tiver combate, variantes de estado ou mais de ~2 ações.

Salve como `Design/ArteFonte/IA/ContextPacks/{asset}/variations.md` — cada linha aqui vira um `output` (ou grupo de `outputs` + entrada em `sheets`) no Passo 4.

```md
# Especificação de Variações — {nome do asset}

## Concept art de origem (Passo 2)
- `Design/ArteConceitual/{categoria}/{asset}/concept.png`

## Ações/Estados

| Ação/Estado | Descrição | Frames (ver animation-guide.md) | Vira no spec JSON |
|-------------|-----------|-----------------------------------|--------------------|
| Idle | | 1 (base) | output `idle` |
| Andar/Mover | | | sheet `walk`: outputs `walk_1`..`walk_n` |
| Ataque 1 | | | sheet `attack1`: outputs `attack1_1`..`attack1_n` |
| Dano/Hurt | | | output `hurt` (ou sheet, se >1 frame) |
| Morte | | | sheet `death`: outputs `death_1`..`death_n` |
| Variante (cor/estado) | ex.: 4 estados de alerta de um marcador | 1 por variante | outputs `estado_a`, `estado_b`… (sem entrada em `sheets` — não é animação) |

## Regras de Continuidade

- Canvas e pivot **idênticos entre todos os outputs** deste asset (regra do `pipeline-sprites-programaticos.md`).
- Hitbox/pontos de interação: descrever aqui se mudam entre estados (ex.: hurtbox maior durante ataque).
- Elementos que NÃO animam: listar para reforçar o que deve ficar idêntico pixel a pixel entre frames.

## Checklist
- [ ] Toda ação do brief/GDD tem uma linha aqui
- [ ] Contagem de frames confere com `animation-guide.md`
- [ ] Mapeamento para ids de `outputs`/`sheets` está definido antes de escrever a spec JSON
```
