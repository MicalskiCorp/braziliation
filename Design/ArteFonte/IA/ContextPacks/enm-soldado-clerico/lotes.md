# Lotes de difusão — Soldado Mercenário Clérico (`enm-soldado-clerico`)

> Rota C (difusão) deste asset. A versão jogável de hoje **não** veio daqui: veio da rota A
> (programática), em `enm_soldado_clerico.spec.json` + `montagem.py`. Este arquivo existe para
> fechar o único lote de difusão que o asset teve, como manda a regra "nenhuma imagem descartada
> sem linha no `lotes.md`".

## Lote 1 — text-to-image, seed 20260712, SDXL 1.0 **sem LoRA**

- **Config:** `workflow-thumbnails.json`, `sd_xl_base_1.0.safetensors`, 6 variações, 1024×1024.
  Prompt e negativo completos em `soldado-clerico-thumbs.lote.json`. `prompt_id`
  `b1778ea5-28f6-4ffa-b610-63860b961851`.
- **Contexto de data:** 2026-07-12 — **antes** do LoRA `pixel-art-xl` (que só entrou no lote 4 da
  Edith, 2026-07-25) e antes da mudança de fluxo de 2026-07-26 (concept passa a ser de cena
  completa). O lote nasceu com a stack que o projeto já aposentou.

### Veredito da curadoria (2026-11-04): REJEITAR as 6. Nenhuma vai para `Selected/`.

**Três motivos, qualquer um bastaria:**

1. **Não é pixel art.** As 6 saíram como ilustração pintada de concept de personagem — linha fina,
   sombreado suave, textura de aquarela digital. É a mesma falha que o lote 1-3 da Edith teve e
   que só o LoRA `pixel-art-xl` corrigiu. Como referência de sprite não serve: não há cluster de
   cor nem silhueta de leitura em 1×.
2. **Violam o próprio negativo do lote.** `multiple views, turnaround sheet, character reference
   sheet` estava no negativo, e 5 das 6 saíram exatamente como prancha de turnaround, com
   miniaturas de costas/perfil, grade de acessórios e até blocos de texto ilegível (`text` também
   estava no negativo). Só `00002` é figura única.
3. **Fora do brief em conteúdo.** Todas leem como soldado europeu genérico de 1ª Guerra — capote,
   chapéu de aba, fuzil de ferrolho. Falta o que define o personagem: **nenhuma** tem iconografia
   clerical, **nenhuma** tem escudo de engrenagem giratória, e **nenhuma** tem a sucata doméstica
   que virou a direção do asset (porta de fogão no peito, tampa de panela como ombreira, cano de
   chaminé, panela de ágata). Nada de brasileiro e nada de Blumenau além do viés germânico, que
   saiu por acaso do vocabulário "clockpunk/colonial-german" do prompt.

**O que vale guardar como referência de figurino** (e só isso): `00001`, pela leitura de capote
longo com bandoleira e chapéu de aba larga, e `00002`, pelo volume de armadura clockpunk encaixada
sobre o corpo — é a única que sugere "peças amarradas por cima de uma pessoa", que é a ideia certa,
ainda que em chave de mecha e não de sucata de cozinha.

### Encaminhamento

O asset **não ficou parado esperando este lote**: em 2026-10-07 a rota A entregou uma versão muito
mais pesquisada e muito mais fiel ao lugar — Pickelhaube com tufo de pena, gola de loden, suspensórios
com edelvais, calção de couro e meias de cano alto, com a sucata de cozinha por cima (ver `historico`
em `enm_soldado_clerico.pagina.json`, 4 entradas). Nada nos 6 thumbnails acrescenta a isso.

**Proposta ao usuário:** encerrar a rota C deste inimigo e tratar a versão programática como o
concept canônico, em vez de gastar um lote novo de difusão.

**Decisão do usuário (2026-11-05):** a arte desta fase é exemplo e primeiro teste — inclusive a
versão programática. Nenhum lote novo agora; o usuário retoma o asset depois, item a item, e aí
decide a rota (com o ADR-016, personagem e inimigo passam a nascer pelo esqueleto do `pxfx`).

- **Destino:** as 6 arquivadas em `Rejected/enm-soldado-clerico-thumbs-lote1/`.
