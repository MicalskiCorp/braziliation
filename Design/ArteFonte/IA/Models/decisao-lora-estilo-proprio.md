# Dossiê de decisão — treino de LoRA de estilo próprio

> Preparado pelo `@TechLead` em 2026-11-03 para o item **"Decidir o treino de LoRA de estilo
> próprio: RunPod por hora × Scenario (US$ 15/mês) × SDXL local em 8 GB"**
> (`Desenvolvimento/Docs/TODO.md` § Ecossistema e processo, responsável: Usuário).
>
> **Status: DECIDIDO em 2026-11-03 — o responsável aprovou a recomendação deste dossiê
> (opção 1).** A decisão vigente é o
> [**ADR-014**](../../../../Desenvolvimento/Docs/Architecture/ADR/ADR-014.md):
> não treinar antes do gate; quando treinar, GPU alugada por hora com pesos e inferência locais;
> Scenario descartado. O gate também está escrito em
> [`pipeline-ia-fundamentos.md § Quando Treinar um LoRA`](../../../GuiasDeArte/pipeline-ia-fundamentos.md#gate-do-projeto-adr-014-2026-11-03).
> Este arquivo fica como o **raciocínio por trás** do ADR — nada aqui foi contratado nem instalado.
>
> Preços e limites dos serviços pagos **não foram verificados nesta sessão** (sem acesso web) —
> os números abaixo são ordem de grandeza e o registro original do TODO. Confirmar no site antes
> de qualquer contratação.

## A pergunta tem duas camadas

O item mistura dois eixos, e isso muda a conversa:

1. **Treinar um LoRA de estilo próprio agora, sim ou não?** (pergunta de dataset e de etapa do projeto)
2. **Se sim, treinar onde?** RunPod e SDXL local são a mesma rota (`kohya_ss`, pesos nossos) em
   máquinas diferentes. **Scenario não é "onde treinar"** — é trocar a rota de geração por um SaaS,
   e isso reverteria a decisão vigente de 2026-07-26 (*só free/local*, em
   [`pesquisa-ferramentas-2026-07.md`](pesquisa-ferramentas-2026-07.md)).

## Gate que o próprio pipeline já define

[`pipeline-ia-fundamentos.md` § Quando Treinar um LoRA](../../../GuiasDeArte/pipeline-ia-fundamentos.md#quando-treinar-um-lora):
treinar só com **30 a 80 imagens aprovadas do próprio Braziliation**, separadas por categoria
(personagens/NPCs, props e máquinas, tiles e cenários, VFX/UI). Antes disso: prompt fixo, paleta
fixa, img2img e pixel pass manual.

**Onde o projeto está hoje** (contagem no disco em 2026-11-03, `Assets/Art/` sem `ThirdParty/`,
cruzada com [`indices/assets.md`](../../../../Desenvolvimento/Docs/Architecture/indices/assets.md)):

| Categoria do gate | Imagens próprias aprovadas | Observação |
|---|---|---|
| Personagens/NPCs | **0** | Edith está no lote 12 sem veredito; Soldado Clérico com 6 thumbnails sem curadoria; Hermann não começou |
| Inimigos | 5 arquivos (1 sheet de idle + 4 variantes do Autômato) | em substituição pela arte gótica 96×96 — há passe de continuidade pendente |
| Props e máquinas | 13 | o acervo real, quase todo da rota programática (specs JSON) |
| Tiles e cenários | 3 tilesets procedurais + 8 frames de fundo do menu | tiles são sheets, não amostras de estilo independentes |
| VFX/UI | 1 (`ui_item_pingente_gato`) | — |

Soma: **29 PNGs próprios**, e a categoria que a rota de difusão mais precisa — personagem e
inimigo — tem dataset praticamente **vazio**. O gate numérico do pipeline não está atingido, e o
gate qualitativo (variedade por categoria) está muito longe.

## Restrição de máquina (medida, não estimada)

Do [bench de 2026-09-03](bench-modelo-base-2026-09.md): RTX 2060 SUPER 8 GB VRAM / 16 GB RAM de
sistema. Com dois modelos base residentes sobraram **0,6 GB de 15,9 GB de RAM** e o SDXL caiu para
~47 s/step. **O teto desta máquina é RAM do sistema, não VRAM** — e mais VRAM não resolveria.
Treino é inferência + otimizador + cache de latentes na *mesma* máquina que roda o Unity, o
ComfyUI e a sessão de desenvolvimento.

## As três opções

### A — RunPod por hora (`kohya_ss` em GPU alugada)

| | |
|---|---|
| O que é | Aluga-se uma GPU de 24 GB por hora, roda-se o treino, baixa-se o `.safetensors` |
| Custo | Por hora de uso, **só quando treina**. Ordem de grandeza US$ 0,3–0,8/h em GPU de 24 GB; um LoRA SDXL com 30–80 imagens costuma levar 1–3 h → **~US$ 1–3 por treino**, mais centavos/GB/mês se guardar dataset em volume de rede. *Confirmar preços no site.* |
| Onde ficam os pesos | **Nossos.** O arquivo entra em `models/loras/` ao lado do `pixel-art-xl` |
| Impacto no pipeline | **Zero.** `comfy_batch.py`, os workflows, `pixelize.py`, paleta travada e o registro em `lotes.md` continuam iguais — muda só qual LoRA o `LoraLoader` carrega |
| Risco | Curva de setup (imagem com kohya, upload do dataset, hiperparâmetros). Config errada custa *mais um treino*, não uma mensalidade |
| Reversível? | Totalmente — pára-se de alugar e o LoRA treinado continua funcionando offline |

### B — Scenario (US$ 15/mês)

| | |
|---|---|
| O que é | SaaS de game asset com treino de *style model* gerenciado e geração no site/API |
| Custo | **Recorrente**, independente de uso. US$ 15/mês é o número registrado no TODO; plano, limites de geração e política de treino **não verificados** |
| Onde ficam os pesos | No fornecedor. Export de pesos normalmente **não** é oferecido → *lock-in* |
| Impacto no pipeline | **Alto.** A geração sai do ComfyUI: alpha nativo (`workflow-sprite-alpha.json`), quantização em paleta travada, seeds registradas e o fluxo de `Outputs/Selected/Rejected` teriam de ser refeitos em volta de uma API externa |
| Risco | Dataset de arte própria sobe para servidor de terceiro (checar os termos sobre uso do material para treino do fornecedor); reverte a decisão de 2026-07-26 |
| Ganho real | Menos engenharia: treino que "só funciona", sem ajuste de hiperparâmetro, e modelos de pixel art já afinados |

### C — Treino local, SDXL em 8 GB

| | |
|---|---|
| O que é | `kohya_ss` nesta máquina: batch 1, AdamW8bit/Adafactor, gradient checkpointing, cache de latentes em disco, text encoder congelado, 768–1024 |
| Custo | US$ 0 em dinheiro |
| Onde ficam os pesos | Nossos, local |
| Impacto no pipeline | Zero, como em A |
| Risco | **Alto contra o gargalo medido.** Cabe na VRAM com truques, mas briga pela RAM de sistema que já é o teto; o treino ocupa a máquina de trabalho por horas e tende a ser instável/lento. Cada tentativa custa uma noite, não US$ 2 |

## Critérios de desempate

- **Custo:** A é o único em que o gasto acompanha o uso. B paga mesmo em mês sem arte. C não paga dinheiro, paga tempo.
- **Lock-in:** A e C mantêm pesos e inferência nossos. B move a etapa mais criativa do pipeline para fora e torna a volta caríssima.
- **Proveniência legal:** a regra do pipeline exige dataset próprio/licenciado, e a proveniência do dataset do `pixel-art-xl` **não é confirmada** ([`comfyui-setup.md`](comfyui-setup.md)). Um LoRA treinado só com arte aprovada do Braziliation **resolve essa dúvida** — é o argumento mais forte *a favor* de treinar, um dia.
- **ADR-013:** nenhuma das três muda a declaração da Steam — continua *Pre-Generated AI content*.
- **Modelo base:** LoRA é treinado **para uma base**. Com o A/B SDXL × Z-Image aberto, treinar
  agora é apostar a base antes de escolher a base — um LoRA de SDXL não serve no Z-Image.

## Recomendação do `@TechLead`

**Não treinar agora; manter a rota vigente (prompt fixo + paleta travada + img2img + pixel pass) e
fixar o gate de reabertura. Quando reabrir, rota A (RunPod por hora). Scenario descartado.**

Motivo: o que falta hoje não é GPU nem dinheiro — é **dataset**. Treinar com 13 props
programáticos e zero personagem ensinaria ao modelo exatamente o que o projeto já sabe fazer sem
ele, e nada do que falta. E a base ainda não está escolhida.

**Gate de reabertura** (quando os três valerem, o item volta ao TODO como tarefa de execução):

1. ≥ 30 imagens próprias aprovadas no grid 48 PPU, das quais **≥ 10 de personagem/inimigo** com pixel pass fechado;
2. A/B SDXL × Z-Image resolvido — a base do LoRA decidida;
3. ≥ 2 personagens com sheet de animação aprovado (para o LoRA ter noção de pose, não só de material).

Scenario sai da mesa por três razões somadas: mensalidade sem relação com uso, pesos
não-exportáveis e substituição de um pipeline local que já funciona e está documentado. Se algum
dia a decisão de "só free/local" cair, o candidato pago que faz mais sentido não é treino de
estilo — é a etapa de *animação* (PixelLab), que é a que o pipeline realmente não cobre.

## Encaminhamento (feito em 2026-11-03)

Recomendação aceita pelo responsável. Executado na mesma sessão:

1. **ADR-014** registrado em `Desenvolvimento/Docs/Architecture/ADR/ADR-014.md` (nenhum ADR substituído);
2. gate escrito em `pipeline-ia-fundamentos.md § Quando Treinar um LoRA` (no `pipeline-ia-sprites.md` até a divisão de 2026-11-09) — § "Gate do projeto (ADR-014)";
3. regra curta em `.claude/rules/arte.md`, que é o que toda sessão de arte carrega;
4. linha **removida** do `Desenvolvimento/Docs/TODO.md` (baixa da camada de Desenvolvimento = o commit);
5. lista de ADRs vigentes atualizada em `Desenvolvimento/Docs/Processos/documentacao.md` § D5.

Quem reabre o assunto é o **gate**, não um item de TODO: quando `indices/assets.md` mostrar os
≥ 30 assets com ≥ 10 de personagem/inimigo, o `@TechLead` reabre pelo ADR-014.
