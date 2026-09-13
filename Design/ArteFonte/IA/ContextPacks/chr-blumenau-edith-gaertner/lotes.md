# Log de Lotes — chr_blumenau_edith_gaertner

> Etapa 2a do fluxo (`pipeline-ia-sprites.md`). Uma entrada por rodada de geração: seed, o que mudou, veredito depois da Etapa 2b.

## Lote 1 — seed 20260724

- **O que mudou:** primeiro lote, text-to-image puro (sem referência). Prompt completo em `context.md` §7-8.
- **Config:** `workflow-thumbnails.json`, 6 variações, 1024×1024, steps 25, CFG 6.5. Checkpoint: `sd_xl_base_1.0.safetensors` puro, sem LoRA de pixel art, sem ControlNet.
- **Veredito: REJEITAR as 6.** Nenhuma imagem é um sprite de personagem isolado. Todas saíram como ilustração/pintura anime completa — cena arquitetônica cheia (prédios, colunas, névoa, lua), personagem pequena/de corpo inteiro embutida na cena em vez de enquadramento de sprite, fundo opaco em 100% dos casos apesar de "no background, transparent background" no prompt positivo e nada equivalente no negativo. Zero traço de pixel art (sem quantização, sem dithering, sem silhueta de baixa resolução) — é ilustração digital padrão do SDXL base.
- **Diagnóstico:** o prompt em camadas (`[REGION]` com "ghost garden, cat cemetery... colonial-german timber architecture") está competindo com `[ASSET]` pela atenção do modelo, e o SDXL 1.0 base (sem LoRA de pixel art) resolve isso pintando a cena inteira em vez de isolar a personagem. "pixel art" e "transparent background" no prompt de texto não têm força suficiente sem um checkpoint/LoRA treinado pra isso — comportamento esperado de SDXL base, não bug de configuração.
- **Nota operacional:** o mesmo lote foi submetido 2x nesta sessão (b105inkek falhou por `python` apontar pro stub da MS Store; reenviado com `py` → prompt_id `af897257...`, ficou em `00007`-`00012`). Achados 6 imagens extras (`00001`-`00006`) no mesmo diretório vêm de uma submissão anterior (sessão passada, task `b192238ge` perdida) que aparentemente completou no servidor sem o cliente confirmar — mesma seed, resultado visualmente idêntico. Não afeta o veredito.
- **Arquivos movidos (2026-07-25):** as 12 imagens + `chr-blumenau-edith-gaertner.lote.json` foram movidos de `IA/Outputs/chr-blumenau-edith-gaertner/` para `IA/Rejected/chr-blumenau-edith-gaertner/`, fechando a Etapa 2b (nunca "descartar sem registro"). `Outputs/chr-blumenau-edith-gaertner/` está vazio, pronto pro lote 2.

## Lote 2 — seed 20260725

- **O que mudou:** prompt reescrito do zero usando as 7 referências reais depositadas em `Design/ArteConceitual/ReferenciasVisuais/edith-gaertner/` (ver `fontes.md`). Duas mudanças principais em relação ao lote 1: (1) removido o bloco `[REGION]` inteiro (diagnosticado como causa raiz da rejeição — competia com `[ASSET]` e fazia o modelo pintar a cena inteira); (2) `[ASSET]` ficou muito mais concreto e específico (vestido/cabelo/pose da Edith Gaertner 1.png, tratamento translúcido/névoa dos Espectro 1-2, cor do Gato Espectral) em vez de descrição genérica. `[TECHNICAL]` reforçado várias vezes pra isolar a personagem (plain flat backdrop, single character only, no scenery/buildings/landscape). Negativo ganhou termos explícitos contra cenário/arquitetura/múltiplos personagens/portrait cropped. Prompt completo em `context.md` §7-8.
- **Config:** `workflow-thumbnails.json`, 6 variações, 1024×1024, steps 25, CFG 6.5. Mesmo checkpoint do lote 1 (`sd_xl_base_1.0.safetensors`, sem LoRA/ControlNet). Referências usadas só como embasamento textual do prompt, não plugadas em img2img.
- **Veredito: REJEITAR as 6, mas com progresso real.** Ver `chr-blumenau-edith-gaertner.lote.json` pros prompt_ids.
  - **O que funcionou (confirma o diagnóstico do lote 1):** isolamento resolvido — todas as 6 têm fundo liso, sem arquitetura/cenário, personagem centralizada. Remover `[REGION]` e reforçar `[TECHNICAL]` funcionou exatamente como esperado.
  - **Problema novo 1 — "character reference sheet" no prompt gera prancha de turnaround, não pose única:** 4 das 6 (`00013`, `00015`, `00017`, `00018`) saíram como múltiplas poses lado a lado (frente/costas/perfil) em vez de uma ilustração única; `00015` e `00017` ainda geraram painéis de texto/UI ilegíveis (o modelo interpretou "reference sheet" literalmente, incluindo campos de ficha técnica falsos).
  - **Problema novo 2 — zero tratamento espectral:** nenhuma das 6 tem translucidez, brilho azul, névoa ou qualquer leitura fantasmagórica — todas saíram como vestido de época opaco convencional. "translucent", "ghostly", "spectral", "glowing" no prompt foram ignorados a favor da descrição literal do vestido.
  - **Problema novo 3 — o gato sumiu:** nenhuma imagem mostra o gato espectral no colo, apesar de estar explícito no prompt.
  - **Problema novo 4 — leitura errada de idade/tom:** saiu como garota jovem estilo anime (`00014` inclusive interpretou "cat" como orelhas de gato/nekomimi, não o animal sendo segurado), não a mulher de ~40 anos digna e decaída da lore.
  - **Diagnóstico:** SDXL 1.0 base sem LoRA claramente prioriza substantivos concretos (vestido, tipo de roupa) sobre adjetivos de efeito visual (translúcido, espectral, brilhante) — o mesmo padrão de "o texto não tem força suficiente sem treino específico" do lote 1, agora isolado num eixo diferente (estilo/VFX em vez de composição). Composição/isolamento parece ser o único eixo que respondeu bem ao ajuste de prompt puro.

## Lote 3 — img2img, seeds 30260725-30260730 (primeiro teste ponta a ponta desse modo)

- **O que mudou:** em vez de text-to-image puro, usou `--reference-image` + `--denoise 0.55` (`workflow-img2img.json`, nunca testado ponta a ponta antes neste ambiente) pra herdar o tratamento espectral que texto sozinho não conseguiu nos lotes 1-2. Mesmo prompt base do lote 2, com "reference sheet" removido (causa das pranchas de turnaround) e negativo reforçado contra "anime schoolgirl/cat ears/turnaround/UI panel". Duas referências testadas, 3 seeds cada: `Espectro 1.jpg` (`00019`-`00021`) e `Espectro 2.png` (`00022`-`00024`).
- **Config:** `workflow-img2img.json`, 1 imagem por submissão (modo img2img não faz lote de 6), 1024×1024, steps 25, CFG 6.5, denoise 0.55.
- **Veredito: REJEITAR as 6 pro asset final, mas com o melhor resultado do teste-âncora até agora.**
  - **Espectro 1 (`00019`-`00021`) — forte:** efeito espectral finalmente presente e convincente — translucidez, brilho azul-esverdeado, partículas/glitter na dissolução do vestido em névoa. Textura ganhou um dithering/pixelização que lembra pixel art de verdade (herdado da própria referência), bem mais próximo da densidade-alvo de SotN/Blasphemous que qualquer coisa dos lotes 1-2. Fundo ficou mais limpo que o lote 1, mas ainda tem gradiente/pilares sutis, não 100% liso.
  - **Espectro 2 (`00022`-`00024`) — fraco:** denoise 0.55 preservou cenário demais da referência (caverna/ruína escura, chão com textura de pedra) — voltou a ter "cenário completo" em vez de personagem isolada, o mesmo problema do lote 1.
  - **Ainda falta em todas as 6:** o gato espectral não aparece em nenhuma — nem o denoise parcial nem o texto conseguiram inserir o elemento que não está na referência-base.
  - **Leitura:** img2img com referência certa resolve o eixo de VFX que texto puro não resolvia; mas herda a composição/cenário da referência de forma forte o suficiente pra não conseguir *adicionar* um elemento novo (o gato) que a referência não tinha.

## Lote 4 — text-to-image, seed 40260726, primeiro teste com LoRA Pixel Art XL

- **O que mudou:** usuário apontou que as imagens dos lotes 1-3 tinham artefatos e falta de coesão mesmo depois dos ajustes de prompt — pediu pra pesquisar um modelo melhor em vez de só mexer em texto. Pesquisa (`nerijs/pixel-art-xl`, LoRA pra SDXL, força 1.2, sem trigger word) levou ao download de `pixel-art-xl.safetensors` (170.5MB) pra `D:\Tools\ComfyUI\models\loras\`, wired via `LoraLoader` em `workflow-thumbnails.json` e `workflow-img2img.json` (ver `comfyui-setup.md`). Mesmo prompt exato do lote 3 (texto), só com o LoRA ativo — variável isolada de propósito.
- **Config:** `workflow-thumbnails.json` com LoRA, 6 variações, 1024×1024, steps 25, CFG 6.5.
- **Veredito: REJEITAR pro asset final, mas é o melhor resultado de qualidade técnica do teste-âncora até agora — LoRA confirmado como a correção certa.**
  - **O que funcionou:** pela primeira vez desde o lote 1, a saída é pixel art de verdade — clusters de cor legíveis, dithering, silhueta limpa, sem textura de ilustração/anime. Isolamento perfeito (fundo cinza liso, personagem centralizada) em 5/6. `00030` é o candidato mais forte visualmente: pose única, postura digna, vestido bem lido.
  - **O que ainda falta:** nenhuma tem tratamento espectral/translúcido (vestido lê como cetim/porcelana azul opaco, não fantasma) nem o gato. `00029` regrediu pro problema de prancha multi-pose do lote 2 apesar do negativo reforçado.
  - **Leitura:** o LoRA resolve o eixo técnico (densidade/coerência de pixel art) que nem prompt nem img2img sozinhos resolviam. Os eixos de conteúdo (espectro, gato) continuam resistentes a ajuste de texto puro — mesmo padrão dos lotes 1-2, agora sobre uma base tecnicamente muito melhor. Próximo passo lógico: combinar LoRA (resolve técnica) + img2img com referência Espectro (resolve VFX, comprovado no lote 3) no mesmo lote.

## Lote 5 — img2img + LoRA, seeds 50260726-50260728, base Espectro 1.jpg, denoise 0.55

- **O que mudou:** primeira combinação LoRA + img2img — soma a correção técnica do lote 4 com o VFX espectral do lote 3. Mesmo prompt de conteúdo do lote 3/4, mesma referência (Espectro 1.jpg) do lote 3.
- **Veredito: melhor resultado do teste-âncora até agora, ainda não aprovável como está.**
  - **O que funcionou:** as 3 imagens (`00031`-`00033`) combinam pixel art tecnicamente coerente (clusters, dithering limpo, herdado do LoRA) **com** o efeito espectral/translúcido de verdade (brilho azul-esverdeado frio, silhueta etérea) — primeira vez que os dois eixos aparecem juntos na mesma imagem. `00031` e `00032` (perfil/3-4) são os candidatos mais fortes.
  - **O que ainda falta:** sem o gato em nenhuma das 3. Fundo regrediu — voltou a carregar ambiente escuro com pilastras/arquitetura da própria referência Espectro 1 (o denoise 0.55 traz cenário junto, mesmo problema já visto no lote 3 com Espectro 2). `00033` inclusive trouxe um pedestal/base de estátua, herdado da composição da referência.
  - **Decisão:** teste-âncora atingiu um patamar de qualidade real pela primeira vez. Chamado o usuário pra decidir se algum candidato vira `Selected/` (gato + limpeza de fundo ficam pro pixel pass manual no Aseprite, dentro da regra do pipeline de nunca aprovar direto da IA) ou se vale mais uma rodada de geração.
  - **Decisão do usuário:** mais uma rodada, mas resolvendo fundo e gato via geração — não com denoise mais baixo (tecnicamente preservaria *mais* referência, inclusive o fundo escuro, o oposto do que precisamos), e sim compondo uma imagem-base própria: figura da Espectro 1 isolada sobre fundo cinza liso + recorte do Gato Espectral colado perto do braço, via script Python (`compose_reference.py`, `Design/ArteFonte/Ferramentas/` — avaliar se vira ferramenta permanente do pipeline). Composição salva como `edith_composite_v1.png`.

## Lote 6 — img2img + LoRA, seeds 60260726-60260728, base `edith_composite_v1.png` (figura+gato compostos), denoise 0.5/0.55/0.6

- **Veredito: REJEITAR as 3 — problema de conteúdo, não só de qualidade.**
  - **Falha grave:** ao simplificar o prompt (tirei a descrição específica do vestido de época pra dar mais peso à translucidez), as 3 imagens saíram com a personagem **sem roupa** — corpo nu translúcido, não vestido. Isso é inaceitável em qualquer contexto do projeto, e ainda mais grave tratando-se de uma personagem baseada numa pessoa histórica real (Edith Gaertner). Arquivado em `Rejected/chr-blumenau-edith-gaertner-lote6/` com esta anotação — nunca promover, nunca reusar como base de nada.
  - **Causa:** prompt simplificado demais — "translucent... skin and dress" sem a descrição concreta de peça de roupa (corte, cós, mangas) que os lotes anteriores tinham deixou o modelo livre pra interpretar "translúcido" como pele nua.
  - **Outros problemas:** o gato da composição não sobreviveu à geração em nenhuma das 3 — o denoise (0.5-0.6) foi alto o suficiente pra "esquecer" o patch colado. Fundo ficou bem mais isolado que o lote 5 (coluna cinza lisa), o que confirma que compor a base isolada funciona pro eixo de fundo — só não resolveu o eixo do gato.
  - **Correção obrigatória pro próximo lote:** reintroduzir a descrição explícita e detalhada da roupa (corte/cós/mangas/comprimento) no `[ASSET]`, e adicionar ao negativo padrão do projeto (não só deste asset): `nude, naked, bare skin, exposed breasts, nsfw`. Ver mudança em `pipeline-ia-sprites.md` (negativo-base do projeto).

## Lote 7 — text-to-image + LoRA, seed 70260726, sem imagem de referência (técnica do lote 4)

- **O que mudou:** usuário pediu pra focar na técnica do lote 4 (que foi o melhor resultado de pixel art puro) e só acrescentar espectro+gato, em vez de continuar em cima do img2img. Também perguntou se as referências reais (`Edith Gaertner 1-2.png`) estavam sendo usadas — resposta: não, só influenciaram texto até agora, nunca entraram como imagem. Prompt reescrito puxando detalhe mais preciso da `Edith Gaertner 1.png` (corte do vestido, cabelo) e da pose real dela segurando o gato erguido perto do ombro (não cradled no colo, como eu tinha descrito antes). Vestido descrito com corte/cós/mangas/comprimento explícitos (correção do lote 6) + negativo com termos de nudez.
- **Config:** `workflow-thumbnails.json` com LoRA, 6 variações, 1024×1024, sem `--reference-image`.
- **Veredito: REJEITAR as 6 pro asset final — técnica bateu o nível do lote 4, mas espectro e gato nunca apareceram juntos na mesma imagem.**
  - `00037`: tem o gato! Mas ele saiu como bicho opaco de porte médio ao lado dela (não translúcido, não erguido/segurado) — sem efeito espectral nela também (pele/pele opaca, não fantasma).
  - `00038`: melhor efeito espectral do lote (translúcido azul-branco convincente, pixel art limpo) — mas sem gato.
  - `00039`: regrediu pro problema de 2 poses lado a lado (frente/costas) apesar do negativo já ter "multiple views/turnaround sheet".
  - `00040`/`00042`: pixel art limpo, roupa cobrindo direito (correção da nudez funcionou), mas sem espectro nem gato — saíram como NPC comum "viva".
  - `00041`: sem gato — a IA substituiu por um item (orbe/chama brilhante na mão), não o animal pedido.
  - **Leitura:** confirma um padrão novo — mesmo com LoRA + técnica boa, o modelo consegue acertar **um** elemento de conteúdo específico por geração (ou o gato, ou o espectro), mas não os dois combinados de forma confiável em texto puro, nem com prompt bastante detalhado. Nenhum dos 42 geradas até agora (lotes 1-7) tem espectro+gato+roupa+isolamento todos corretos ao mesmo tempo.

---

## Mudança de fluxo (2026-07-26) — teste-âncora pausado no formato atual

Decisão do usuário: `00038` reconhecido como melhor resultado até aqui, mas o fluxo muda antes de fechar — o concept art passa a ser de **cena completa** (Edith posicionada no Jardim do Cemitério dos Gatos, como o concept do Minhocão), e o sprite isolado com frames de animação vira etapa posterior à aprovação do concept. Pesquisa de ferramentas especializadas (Retro Diffusion pra concept, PixelLab pra animação) feita e documentada em `IA/Models/pesquisa-ferramentas-2026-07.md` — **decisão: só free/local por enquanto** (stack atual ComfyUI+SDXL+LoRA pra concept de cena; Aseprite manual pra frames). Ver seção nova em `pipeline-ia-sprites.md#mudança-de-fluxo-2026-07-26`.

Estado dos lotes 1-7: todos em `Rejected/`. `00038` fica como referência técnica do que a stack local produz de melhor em sprite isolado — vai ser útil de novo na etapa de produção pós-concept.

## Lote 8 — seed 80260726 — PRIMEIRO LOTE DO NOVO FLUXO: concept de cena completa

- **O que mudou:** não é mais sprite isolado — é a cena canônica da lore (`Edith-Gaertner.md`): Edith sentada no banco natural de raiz de uma árvore enorme, no Jardim do Cemitério dos Gatos, cercada pelos gatos espectrais, com as lápides nomeadas. Cenário descrito a partir das fotos reais do local (`ReferenciasVisuais/edith-gaertner/Cemitério dos gatos 1-2`): lápides retangulares de concreto com plaquetas, estátua branca de gata com filhote sobre pedestal de pedra bruta, trilha de cascalho, banco, vegetação subtropical densa, troncos musgosos — transposto pro mood do jogo (noite, luz espectral azul-fria, névoa baixa). Text-to-image + LoRA (sem img2img: a foto real é diurna/tropical viva, denoise alto pra virar noite espectral perderia a composição de qualquer forma — a foto serve de fonte da descrição textual precisa).
- **Config:** `workflow-thumbnails.json` com LoRA `pixel-art-xl`, 6 variações, 1024×1024, steps 25, CFG 6.5.
- **Veredito: REJEITAR as 6 (`00043`-`00048`), mas o cenário atingiu o melhor nível do projeto.** Mood noturno espectral, lápides, estátua de gato branca, árvores enormes com raízes, vegetação densa, névoa — tudo presente e com leitura Blasphemous-like convincente. **A Edith não apareceu em nenhuma das 6** — só gatos (alguns bem colocados) e estátuas. Mesmo padrão dos lotes anteriores: o modelo atende um foco por vez, e com `[SCENE]` detalhado primeiro, o personagem perdeu a disputa de atenção. Próximo lote: personagem em primeiro no prompt (SDXL pesa mais os primeiros tokens), cenário condensado. Arquivado em `Rejected/chr-blumenau-edith-gaertner-lote8/`.

## Lote 9 — seed 90260726 — concept de cena, personagem primeiro no prompt

- **O que mudou:** ordem do prompt invertida — a Edith (sentada na raiz, gato no colo, brilho espectral) abre o prompt como sujeito principal; cenário do Cemitério condensado num bloco menor depois. Negativo ganhou "empty scene, no people, unpopulated". Mesma config do lote 8.
- **Veredito: MELHOR LOTE DO PROJETO — inversão do prompt destravou a cena.** Pela primeira vez personagem + gato + árvore + mood aparecem juntos:
  - `00049`: Edith sentada nas raízes da árvore gigante, véu/xale, gato branco ao lado, mãos recolhidas, jardim escuro com lua — composição e melancolia muito próximas da lore.
  - `00052`: Edith sentada na raiz **com o gato branco literalmente no colo** (a cena canônica), árvore enorme enquadrando — mas fundo azul chapado, quase sem cenário.
  - `00053`: Edith sentada com gato branco ao lado, floresta profunda com partículas espectrais — melhor profundidade de cenário.
  - `00054`: figura sentada no banco de raiz segurando algo brilhante, lua enorme, trilha — mood forte, mas leitura mais "encapuzada" que "cabelo preso".
  - `00050`/`00051`: mais fracas (figura lê como estátua/monge, pouco identificável como a Edith).
  - **Gaps comuns vs. lore/brief:** cabeça com véu/capuz em vez de coque baixo; translucidez parcial (ela lê sólida); lápides nomeadas e estátua da gata (das fotos reais) ausentes na maioria; só 1 gato em vez de vários.
- **Decisão do usuário:** iterar lote 10 corrigindo os gaps. Lote 9 arquivado em `Rejected/chr-blumenau-edith-gaertner-lote9/` (manter — melhores referências de composição do projeto até aqui).

## Lote 10 — seed 100260726 — concept de cena, refinamento dos gaps do lote 9

- **O que mudou:** mesma estrutura de prompt do lote 9 (personagem primeiro), com 4 correções: (1) "hair in a low bun, no hood, no veil, head uncovered" explícito + "hood, veil, nun habit" no negativo; (2) translucidez reforçada ("semi-transparent, background faintly visible through her"); (3) lápides nomeadas + estátua branca da gata reintroduzidas no bloco de cena, agora com menos competição (cenário já provou que sai); (4) "several small glowing spectral cats" reforçado com posição concreta ("on the gravestones and around her feet").
- **Veredito: os 3 gaps principais melhoraram; 2 candidatos fortes.**
  - **Melhorou:** translucidez dela agora convincente (lê como espectro branco-azulado); gatos presentes em 4 das 6; lápides/cruzes de volta à cena; mood mantido.
  - `00060` (candidato mais forte): Edith sentada nas raízes da árvore gigante, **2 gatos** (branco ao lado, cinza abaixo), cruzes de cemitério ao fundo, translucidez boa — a cena canônica mais completa até aqui.
  - `00056`: gato praticamente no colo dela, árvore + ruínas de cemitério com profundidade — segunda melhor.
  - `00057`: ela + gato branco na plataforma de pedra com chuva — boa, um pouco "estátua".
  - `00055`/`00058`: leitura de estátua de túmulo em vez de fantasma; `00058` com fundo incompleto (bordas brancas).
  - `00059`: regressão — virou estátua de gato gigante, sem a Edith.
  - **Gaps restantes:** cabelo ainda solto/longo (coque baixo não pegou em nenhuma); leitura levemente "estátua" em vez de "espírito" em metade delas.
- **Decisão do usuário:** `00060` muito bom, mas pediu 3 ajustes antes de promover — (1) confirmou que as fotos reais ainda não estão entrando como imagem no fluxo (só texto) — reconferi `Cemitério dos gatos 2.png` e o fundo real é um **bambuzal** (troncos altos claros em anéis), não a copa genérica que saiu; (2) o rabo do gato cinza/azulado embaixo-esquerda está solto do corpo (artefato de anatomia da IA); (3) pediu névoa espectral azul-clara envolvendo ambiente+gatos+personagem pra reforçar o dark fantasy.

## Lote 11 — img2img sobre 00060, seed 110260726, denoise 0.45

- **O que mudou:** primeira vez usando um resultado anterior do *mesmo* asset como base de img2img (não uma referência externa). Prompt: bambuzal explícito no fundo (baseado em `Cemitério dos gatos 2.png`), névoa espectral azul-clara reforçada sobre toda a cena (não só nela). Aviso registrado: denoise moderado tende a preservar o rabo solto do gato (defeito já presente na imagem-base) — se não corrigir, fica anotado como ajuste manual pro pixel pass.
- **Veredito: nenhum dos 3 pedidos atendido — mesmo padrão de "img2img não adiciona o que não está na base".**
  - Bambuzal: não apareceu, fundo continua árvore genérica de copa larga.
  - Rabo solto: "corrigido" removendo o gato inteiro — só sobrou o gato branco, perdendo a composição de 2 gatos que era um dos pontos fortes do `00060`.
  - Névoa unificada: sem diferença visível clara.
  - Translucidez e qualidade geral se mantiveram boas (herdado do `00060`).
  - **Leitura:** confirma pro concept de cena o mesmo limite já visto nos sprites isolados — denoise moderado preserva estrutura mas não incorpora elementos novos com força. Pra esses 3 ajustes específicos, texto puro (novo lote do zero) tende a funcionar melhor que img2img sobre uma imagem que não tem esses elementos.
- **Decisão do usuário:** lote 12 — texto puro do zero, sem img2img, com bambuzal/névoa/2 gatos explicitados desde o início do prompt.

## Lote 12 — text-to-image + LoRA, seed 120260726, sem imagem de referência

- **O que mudou:** volta ao text-to-image puro (técnica que melhor incorpora elemento novo). `[SCENE]` reescrito com bambuzal como primeiro elemento de cenário (troncos altos claros em anéis, densos, baseado em `Cemitério dos gatos 2.png`). `[ATMOSPHERE]` novo bloco dedicado à névoa espectral azul-clara envolvendo tudo. Dois gatos especificados individualmente com descrição anatômica completa cada um ("a small white spectral cat... a second small grey-blue spectral cat, its tail clearly attached and visible connecting to its body") pra evitar tanto o desaparecimento quanto o defeito de anatomia.
- **Veredito:** _(preencher após inspeção — Etapa 2b)_