# Como Enviar Material de Pesquisa pelo WhatsApp

Protocolo de entrada para quem grava e manda material no grupo dedicado. Cada regra aqui veio de
um problema real da curadoria da visita ao Teatro Carlos Gomes (2026-10-11): seguir o protocolo é
o que permite ligar cada foto ao áudio certo sem adivinhar.

## Assunto: detectado sozinho, marcar é opcional

O material chega picado e intercalado: a benzedeira hoje, um museu amanhã, a benzedeira de novo
no mês que vem. **Você não precisa dizer de que assunto é cada coisa.** Na curadoria, o material é
agrupado pelo horário e o assunto de cada grupo é detectado pelo que foi dito e escrito (transcrição
dos áudios, textos, legendas), comparado com os assuntos que já existem. Você só confirma a
sugestão — e é avisado quando o mesmo horário traz conteúdo de dois assuntos.

O que ajuda a detecção (sem custar nada na hora):

- **Falar o assunto no começo do áudio** — "estou com a benzedeira", "agora na casa da Edith".
- **Legenda ou texto curto** junto de foto solta: foto sem texto e sem áudio por perto só é
  ligada ao assunto pelo horário.

**Atalho opcional** — quando quiser garantir na hora (dois assuntos no mesmo período, só fotos sem
contexto):

```
#assunto benzedeira          ← tudo o que chegar depois vai para "benzedeira"
(áudios, fotos, textos…)
#fim                         ← fecha (ou fecha sozinho depois de 12 h sem mensagem)
```

O material marcado pula a detecção. Use sempre o mesmo nome para o mesmo assunto.

## Antes de começar

1. **Uma mensagem de texto de contexto:** o que é, onde, quando e quem fala (ou diga isso no
   começo do primeiro áudio). Ex.: `Visita guiada ao Teatro Carlos Gomes, Blumenau, 11/10 — guia do teatro, visita
   pública`. A curadoria usa essa mensagem como contexto da sessão inteira.
2. **Consentimento de terceiros:** se quem fala não é você, peça autorização no começo da
   gravação ("posso usar esse relato na pesquisa do jogo?"). Sem isso, o relato entra anônimo ou
   não entra.

## Durante

| Faça | Por quê |
|---|---|
| **Um áudio por lugar ou por assunto**, começando pelo nome dele ("agora no porão, sob o palco") | O áudio vira um trecho da curadoria; dizer o lugar no começo dispensa deduzir pelo conteúdo |
| **Grave no gravador do celular e mande o arquivo** (ou grave direto no WhatsApp) | O arquivo `.m4a` do gravador traz o horário da gravação — é ele que liga as fotos ao áudio |
| **Mande as fotos como _Documento_, não como _Foto_** (📎 → Documento → escolher da galeria) | Como documento, a foto chega com o nome original da câmera (`20261011_102033.jpg`), que tem o horário. Como foto, o WhatsApp comprime e **apaga o horário** — na visita, 16 fotos tiveram de ser ligadas aos lugares só pelo que mostravam |
| **Vídeo também como Documento** | Mantém o horário e a qualidade para tirar quadros |
| **Fotografe o exterior na chegada e na saída** | Fachada, praça e estátuas viram uma seção própria ("Exterior"), mesmo sem narração |
| **Evite rosto de pessoas** em primeiro plano | Foto com rosto identificável não entra no repositório |

## Depois

1. **Uma mensagem de texto para cada destaque** que você já sabe que importa, citando a foto
   (responda à foto no WhatsApp). Ex.: `essa abertura emparedada no porão vai ser a entrada do
   túnel`. Decisão criativa dita na hora entra no handoff sem depender de memória.
2. **Mande tudo de uma vez se quiser** — o listener confirma o lote numa mensagem só.
3. Se tiver usado o atalho `#assunto`, **`#fim`** fechando.

## O que acontece com o material

O listener grava cada mensagem em `_inbox/`; o `transcrever.py` transcreve os áudios; a skill
`processar-entrevistas` monta a linha do tempo, a revisão da transcrição, o inventário de assuntos
e o de-para áudio ↔ lugar ↔ fotos, e só então grava a pesquisa. Detalhes em [index.md](index.md).
