# Pesquisa de Ferramentas de IA pra Pixel Art — 2026-07-26

> Pesquisa feita durante o teste-âncora da Edith Gaertner (ver `ContextPacks/chr-blumenau-edith-gaertner/lotes.md`), quando o usuário propôs mudar o fluxo para: (1) concept art de **cena completa** (personagem posicionado no cenário, estilo do concept do Minhocão) gerado por modelo especializado → aprovação → (2) sprites de produção **separados por frames de animação** gerados por IA específica, animáveis via código.
>
> **Decisão do usuário (2026-07-26): NÃO adotar ferramentas pagas por enquanto — só free/local.** Esta página registra a pesquisa pra quando/se essa decisão for revisitada.

## Opções pagas pesquisadas (não adotadas)

### Etapa 1 — Concept art de cena: Retro Diffusion
- [retrodiffusion.ai](https://retrodiffusion.ai/) — modelo treinado do zero pra pixel art (não LoRA sobre SDXL); referência do mercado em grid/paleta/cluster corretos.
- Custo: ~$0.01/imagem via site/API (créditos pré-pagos, sem assinatura). Extensão Aseprite local: $65 único (sem animação, sem modelos top).
- Integração possível: [nó ComfyUI pra API](https://github.com/svntax/ComfyUI-RetroDiffusion-API-Node) — encaixaria no `comfy_batch.py`.

### Etapa 2 — Sprites animados: PixelLab
- [pixellab.ai](https://www.pixellab.ai/) — animação por esqueleto (articulações → frames consistentes), text-to-animation (walk/idle/attack), interpolação até 16 frames, referência de estilo por imagem (daria pra alimentar o concept aprovado), export Unity, [API REST](https://www.pixellab.ai/pixellab-api) + plugin Aseprite.
- Custo: assinatura $12–50/mês OU API pay-per-credit ($0.006–$0.042 operação padrão, Pro até $0.185). Animação limitada a 128×128 (suficiente pros nossos 64×64).
- Comparação de terceiros: [GameDev AI Hub](https://gamedevaihub.com/retro-diffusion-vs-pixellab/) — RD melhor em qualidade estática nativa, PixelLab melhor em pipeline de personagem animado.

### Nota sobre "layers"
Nenhuma dessas ferramentas entrega "layers" tipo Photoshop/Spine (partes do corpo separadas pra rig em runtime). O que entregam é **sprite sheet de frames por animação** (idle/walk/attack como sequências separadas) — que é o formato animável via código no Unity (Animator/script). Rig por partes continua sendo trabalho manual (prefab por partes, já previsto em `sprite-scale-guide.md` pra bosses).

### Como funcionaria o pagamento (dúvida respondida na sessão)
Sem nenhuma relação com a assinatura do Claude: cada serviço tem conta própria, pagamento próprio (cartão direto com eles) e API key própria. Claude Code só escreveria os scripts que usam as chaves. Estimativa no volume atual do projeto: ~$0.06 por lote de 6 concepts (RD); ~$1–3 por personagem com 3-4 animações (PixelLab pay-per-credit).

## Caminho free/local adotado (2026-07-26)

- **Etapa 1 (concept de cena):** ComfyUI local + SDXL + LoRA `pixel-art-xl` (grátis, já instalado — ver `comfyui-setup.md`). Os lotes 4/7 do teste-âncora provaram que essa stack produz pixel art coerente; pra cena completa, o prompt volta a incluir cenário (o oposto do sprite isolado) e as referências visuais reais do local (`ReferenciasVisuais/`) entram como base de descrição e/ou img2img.
- **Etapa 2 (sprites de produção):** sem IA free confiável pra animação de sprite hoje (opções open-source como Animator2D no HuggingFace são experimentais). Rota free real: concept aprovado → `pixelize.py` → pixel pass + frames manuais no Aseprite (onion skin, tags), como o pipeline já documenta. Revisitar PixelLab se/quando o volume de personagens justificar.
- Alternativa free adicional a explorar se a qualidade do LoRA atual limitar: outros checkpoints/LoRAs de pixel art gratuitos no CivitAI (ex. Pixel Art Diffusion XL) — baixar e testar localmente, mesmo processo do `pixel-art-xl`.
