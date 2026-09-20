# Entrevistas — Captura de Pesquisa via WhatsApp

Pipeline que alimenta a pesquisa do `@Historiador` com entrevistas e conversas
esporádicas (historiadores locais, quem viveu ou ouviu as lendas) gravadas numa
conversa dedicada do WhatsApp. Decisão registrada em
[ADR-009](../../../Desenvolvimento/Docs/Architecture/architecture_decisions.md#adr-009-captura-de-entrevistas-de-pesquisa-via-whatsapp-baileys--whisper-local).

> Áudio bruto e transcrição ficam fora do git (dado pessoal/de terceiros) — só o
> material já curado e aprovado entra em `Design/Pesquisa/Estados/` ou `Temas/`.

## Pipeline

```
WhatsApp (conversa dedicada)
   → Ferramentas/whatsapp-listener/   (Node.js + Baileys, roda no PC de casa)
   → _inbox/                          (áudio, texto, imagem ou documento — um item por pasta)
   → Ferramentas/transcrever.py       (faster-whisper + extração de texto, local, sem API)
   → _pendente-curadoria/             (preparado, aguardando curadoria)
   → skill `processar-entrevistas`    (@Historiador, dentro do Claude Code)
   → _processado/                     (arquivado com o resultado da curadoria)
```

## O que cada tipo de mensagem vira

| Mandou no grupo | Capturado como | Preparado por `transcrever.py` |
|---|---|---|
| Áudio / voz | `audio.ogg` | `transcricao.txt` (faster-whisper, local) |
| Texto | `mensagem.txt` | — |
| Foto | `imagem.jpg` (+ `legenda.txt`) | — · a curadoria lê a imagem direto no Claude Code |
| PDF / DOCX / TXT | `documento.pdf` (+ `legenda.txt`) | `texto-documento.txt` (pdfplumber / python-docx) |

PDF escaneado (só imagem, sem camada de texto) não tem OCR automático — o
`texto-documento.txt` sai com um aviso e a curadoria abre o arquivo direto. Figurinha,
vídeo, contato e localização não são capturados.

O arquivo bruto **fica no projeto** (`_inbox/` → `_pendente-curadoria/` → `_processado/`,
fora do git). Imagem ou documento aprovado na curadoria é copiado para
`../Fontes/Arquivos/` — é só essa cópia que entra no git e pode ser usada pelo projeto.

## Pastas

| Pasta | Conteúdo |
|-------|----------|
| `_inbox/` | Captura crua do listener — `audio.ogg`, `mensagem.txt`, `imagem.*` ou `documento.*` + `meta.json` |
| `_pendente-curadoria/` | Já transcrito/extraído, aguardando o `@Historiador` (skill `processar-entrevistas`) |
| `_processado/` | Arquivado após curadoria, com `resultado` no `meta.json` |
| `Ferramentas/` | Código do listener e do transcritor — ver `Ferramentas/whatsapp-listener/README.md` |

## Como usar

1. Rodar `Ferramentas/whatsapp-listener/` no PC de casa (sempre ligado, pareado uma vez via QR code).
2. Mandar a entrevista para a conversa dedicada — áudio gravado direto no WhatsApp, texto, foto de documento ou PDF. Funciona de qualquer lugar: o listener recebe quando o PC volta a ficar online, sem precisar de acesso remoto.
3. Rodar `py Ferramentas/transcrever.py` quando quiser processar o que chegou.
4. Invocar a skill `processar-entrevistas` (ou pedir ao `@Historiador` "processar entrevistas") para curar o lote.

## Riscos conhecidos

- Baileys é integração não-oficial — risco (considerado baixo em uso pessoal, mas não nulo) de bloqueio da conta usada. Ver `Ferramentas/whatsapp-listener/README.md`.
- Entrevista com terceiros exige confirmar consentimento antes de aprovar o relato (regra na skill `processar-entrevistas`).
- Sem OCR no pipeline: foto de documento e PDF escaneado dependem da leitura na curadoria.
- O listener precisa estar rodando para receber, mas **reinício não perde fila** — a retomada
  vive em `Ferramentas/whatsapp-listener/estado.json` (fora do git). Apagar esse arquivo faz o
  listener recomeçar do "agora".
