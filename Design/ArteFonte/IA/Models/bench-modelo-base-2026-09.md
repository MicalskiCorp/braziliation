# Bench de modelo base — SDXL × Z-Image Turbo — 2026-09-03

> Pergunta: **trocar o SDXL 1.0 + LoRA `pixel-art-xl` por Z-Image Turbo?**
> Recomendação anterior (pesquisa de mercado, 2026-09-02) era que sim. **O teste não confirmou.**

## Método

Prompt e seed idênticos (`20260903`), lote de 2, 1024×1024, na mesma máquina
(RTX 2060 SUPER 8 GB / 16 GB RAM). Saídas em `IA/Outputs/bench-modelo-base/`,
comparação em `ab_sdxl_vs_zimage.png`.

| | SDXL 1.0 + `pixel-art-xl` | Z-Image Turbo fp8 (sem LoRA) |
|---|---|---|
| Workflow | `workflow-thumbnails.json` | `workflow-zimage-thumbnails.json` |
| Steps / cfg | 25 / 6.5 | 8 / 1.0 |
| Tempo | **19 min 28 s** (só o sampling) | **5 min 37 s** (job inteiro) |
| Disco | já instalado | +11,7 GB (difusão 6,2 + encoder 5,3 + VAE 0,3) |

## Resultado

**Não há vencedor absoluto — eles resolvem etapas diferentes.**

**SDXL + LoRA produz pixel art de verdade.** Pixel chunky, sensação de paleta limitada,
personagem de corpo inteiro em escala aproveitável como referência de sprite. Em
compensação o detalhe fica pastoso, as proporções saíram estranhas (a segunda amostra
ficou atarracada) e a aderência ao brief é fraca — "engrenagem exposta no peito" e "lente
de vidro" mal aparecem.

**Z-Image produz ilustração excelente, não pixel art.** Aderência ao brief muito superior:
torso de latão, engrenagem exposta, lente de vidro, hastes finas e ferrugem estão todos
lá e legíveis. Mas a superfície é renderizada, não pixelada — é concept, não sprite. E o
enquadramento saiu **busto**, não corpo inteiro, o que é pior como referência de sprite.

Dois detalhes que pesam a favor do Z-Image: fez isso **sem nenhum LoRA** (não existe LoRA
de pixel art de Z-Image instalado) e em **3,5× menos tempo**.

## Veredito

**Não substituir. Somar.**

- **Etapa 2 (concept de personagem/cena)** → **Z-Image Turbo**. Aderência a prompt e
  leitura de material muito melhores, e 3,5× mais rápido. É exatamente a etapa em que se
  quer qualidade de ilustração.
- **Rota de referência pixelada** → **manter SDXL + `pixel-art-xl`**. É a única das duas
  que entrega algo com cara de sprite hoje.
- Nenhuma das duas produz asset final — o pixel pass manual continua obrigatório, como o
  pipeline já manda.

## Pendências deste bench

1. **Z-Image não foi testado com LoRA de pixel art.** Existe `PixelArtRedmond` com versão
   para Z Image. Sem esse teste, o veredito acima está incompleto: pode ser que o Z-Image
   com LoRA vença nos dois eixos.
2. **Enquadramento** — o prompt precisa de "full body, head to toe" para o Z-Image parar de
   entregar busto.
3. **O tempo não é comparação limpa.** Ver abaixo.

## Achado estrutural, mais importante que o A/B

**O gargalo desta máquina é RAM do sistema, não VRAM.**

Com os dois modelos residentes, a RAM livre caiu para **0,6 GB de 15,9 GB**. O SDXL entrou
em `dynamic VRAM loading` com 4.896 MB staged e despencou para **~47 s/step** — daí os
19 min. A VRAM estava em 6,4 GB livres de 8; não era ela o limite.

Consequências práticas:

- A comparação de tempo acima **não é limpa**: o Z-Image rodou primeiro, com mais RAM
  livre. Para medir de verdade, reiniciar o ComfyUI entre as rodadas.
- Manter dois modelos base instalados não é de graça nesta máquina. Rodar um de cada vez.
- Antes de qualquer teste de geração, fechar aplicações. 16 GB é o teto real do pipeline
  hoje — mais VRAM não resolveria isto.
