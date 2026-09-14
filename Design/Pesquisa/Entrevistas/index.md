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
   → _inbox/                          (áudio .ogg ou texto bruto, um item por pasta)
   → Ferramentas/transcrever.py       (faster-whisper, local, sem API)
   → _pendente-curadoria/             (transcrito, aguardando curadoria)
   → skill `processar-entrevistas`    (@Historiador, dentro do Claude Code)
   → _processado/                     (arquivado com o resultado da curadoria)
```

## Pastas

| Pasta | Conteúdo |
|-------|----------|
| `_inbox/` | Captura crua do listener — `audio.ogg` ou `mensagem.txt` + `meta.json` |
| `_pendente-curadoria/` | Já transcrito, aguardando o `@Historiador` (skill `processar-entrevistas`) |
| `_processado/` | Arquivado após curadoria, com `resultado` no `meta.json` |
| `Ferramentas/` | Código do listener e do transcritor — ver `Ferramentas/whatsapp-listener/README.md` |

## Como usar

1. Rodar `Ferramentas/whatsapp-listener/` no PC de casa (sempre ligado, pareado uma vez via QR code).
2. Mandar a entrevista para a conversa dedicada — gravada direto no WhatsApp ou enviada de outro app. Funciona de qualquer lugar: o listener recebe quando o PC volta a ficar online, sem precisar de acesso remoto.
3. Rodar `py Ferramentas/transcrever.py` quando quiser processar o que chegou.
4. Invocar a skill `processar-entrevistas` (ou pedir ao `@Historiador` "processar entrevistas") para curar o lote.

## Riscos conhecidos

- Baileys é integração não-oficial — risco (considerado baixo em uso pessoal, mas não nulo) de bloqueio da conta usada. Ver `Ferramentas/whatsapp-listener/README.md`.
- Entrevista com terceiros exige confirmar consentimento antes de aprovar o relato (regra na skill `processar-entrevistas`).
