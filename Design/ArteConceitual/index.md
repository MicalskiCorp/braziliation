# Arte Conceitual — Braziliation

> Referências visuais para assets, sprites e cenários.
> Consultar ao definir direção de arte ou criar novos sprites.

## Conteúdo

| Pasta | Descrição |
|-------|-----------|
| [`Cidades/`](Cidades/index.md) | Arte conceitual de cidades e ambientes urbanos |
| [`Monstros/`](Monstros/index.md) | Legado de criaturas e bosses; novas artes devem ir para `Criaturas/` |
| [`Criaturas/`](Criaturas/) | Criaturas, inimigos e bosses novos |
| [`Personagens/`](Personagens/) | Personagens jogáveis, NPCs e figuras narrativas |
| [`Props/`](Props/) | Objetos, máquinas, relíquias e itens de cenário |
| [`Paletas/`](Paletas/) | Estudos visuais de paleta por região, clima e facção |
| [`ReferenciasVisuais/`](ReferenciasVisuais/index.md) | Apoio visual pra qualquer asset (fotos reais, material, mood, anatomia) — insumo pré-concept art |

## Regra de Uso

- Arte conceitual explora visual, composição e atmosfera.
- Asset final para Unity deve seguir os guias em [`../GuiasDeArte/`](../GuiasDeArte/index.md).
- Sprites finais entram em `Desenvolvimento/Assets/Art/`, não nesta pasta.

## Três tipos de conteúdo nesta pasta

1. **Mood board / key art** (`Cidades/`, `Monstros/` legado) — pintura ampla, atmosfera e composição de uma cidade ou criatura; não é referência de silhueta pixel a pixel e não deve alimentar spec JSON diretamente (estilo pictórico, gradiente suave — incompatível com as regras de `pipeline-ia-sprites.md`).
2. **Concept art de asset** (`Personagens/`, `Criaturas/`, `Props/`) — é o **Passo 2** do fluxo concept art → spec JSON → sprite (ver [`pipeline-sprites-programaticos.md`](../GuiasDeArte/pipeline-sprites-programaticos.md#fluxo-completo-da-ideia-ao-sprite-5-etapas)): referência na escala do asset, silhueta legível, que serve de base real para o Passo 4 (spec JSON) e, na rota C, para condicionamento por imagem (ControlNet/IP-Adapter).
3. **Referências visuais de apoio** (`ReferenciasVisuais/`) — fotos/ilustrações reais de pessoas/lugares/fatos, mas também material, mood, anatomia ou composição pra assets fictícios; usado **antes** do Passo 2, como insumo pra montar um prompt mais fiel, não como concept art em si. Ver [`ReferenciasVisuais/index.md`](ReferenciasVisuais/index.md).

### Convenção do concept art de asset (Passo 2)

- Pasta: `{categoria}/{asset-slug}/concept.png` (+ variações no mesmo diretório, se houver: `concept_v2.png`, etc.).
- Aprovação: `{categoria}/{asset-slug}/concept.md` com os campos mínimos:

```md
# Concept Art — {asset}

- Referência criativa (Passo 1): `Design/Criativo/...`
- Motor usado: ComfyUI (SDXL/Flux) | outro
- Data:
- Status: proposto | aprovado
- Aprovado em:
- Observações:

## Contexto usado na geração

> Transcrever tudo que foi levado em consideração — é o que permite o usuário aprovar com visibilidade total, não só olhar a imagem final.

- Trecho de lore/aparência usado (copiado de `Design/Criativo/.../{asset}.md`, seção "Aparência" se for `ModelPersonagem.md`):
- Prompt positivo:
- Prompt negativo:
- Seed:
- Referência de imagem usada (`--reference-image`), se houver, e denoise:
- Variações geradas (quantas, onde estão em `ArteFonte/IA/Outputs/`):
- Motivo da escolha da variação aprovada:
```

- Ao aprovar, mover a entrada correspondente de `Design/Criativo/TODO.md` (seção "Concept Art Pendente") para "Concluído" e registrar em `Desenvolvimento/Docs/Architecture/indices/assets.md`.

### Regra de retenção pós-aprovação

Após aprovar, manter em `{categoria}/{asset-slug}/` **apenas**: (1) o arquivo aprovado (`concept.png`) e (2) o original/referência prévia, se existir e for diferente do aprovado (ex.: mood board legado usado como base de geração). **Remover** as iterações rejeitadas em `Design/ArteFonte/IA/Outputs/{asset}*/` — não acumular histórico de tentativas descartadas depois que a decisão final foi tomada.

---

> Estilo do projeto: Pixel Art de alta densidade · Dieselpunk pós-apocalíptico
> Ver direção de arte completa em [`../GuiasDeArte/direcao-de-arte.md`](../GuiasDeArte/direcao-de-arte.md)
