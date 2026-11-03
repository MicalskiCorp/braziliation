"""Proteção de um servidor local que roda agentes (ADR-012, invariante 8).

Escutar só em 127.0.0.1 não basta: qualquer site aberto no navegador consegue mandar requisição
para `localhost`, e um domínio que resolve para 127.0.0.1 (DNS rebinding) consegue até ler a
resposta. Por isso:
- `Host` precisa ser o da Central — barra o rebinding;
- toda ação (método que não é GET/HEAD) exige o token da página no cabeçalho `X-Central-Token`
  — um site de fora não consegue ler a página para obtê-lo;
- `Origin` e `Sec-Fetch-Site`, quando vêm, precisam ser da própria Central;
- CSP sem script inline e sem frame: texto renderizado nunca vira código.
"""
from __future__ import annotations

import secrets

CABECALHOS = [
    (b"content-security-policy",
     b"default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; "
     b"frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none'"),
    (b"x-content-type-options", b"nosniff"),
    (b"referrer-policy", b"no-referrer"),
    (b"x-frame-options", b"DENY"),
    (b"cache-control", b"no-store"),
]


class Protecao:
    def __init__(self, app, porta: int, hosts_extra: tuple[str, ...] = (), token: str | None = None):
        self.app = app
        self.token = token or secrets.token_urlsafe(32)
        self.hosts = {f"127.0.0.1:{porta}", f"localhost:{porta}", *hosts_extra}
        self.origens = {f"http://{h}" for h in self.hosts}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        cab = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
        motivo = self._recusa(scope["method"], cab)
        if motivo:
            corpo = f"Recusado pela Central: {motivo}".encode("utf-8")
            await send({"type": "http.response.start", "status": 403,
                        "headers": [(b"content-type", b"text/plain; charset=utf-8")] + CABECALHOS})
            await send({"type": "http.response.body", "body": corpo})
            return

        async def enviar(msg):
            if msg["type"] == "http.response.start":
                msg = {**msg, "headers": list(msg.get("headers", [])) + CABECALHOS}
            await send(msg)

        await self.app(scope, receive, enviar)

    def _recusa(self, metodo: str, cab: dict) -> str:
        if cab.get("host") not in self.hosts:
            return "host desconhecido"
        origem = cab.get("origin")
        if origem and origem not in self.origens:
            return "origem de outro site"
        if cab.get("sec-fetch-site") == "cross-site":
            return "requisição de outro site"
        if metodo not in ("GET", "HEAD") and not secrets.compare_digest(cab.get("x-central-token", ""), self.token):
            return "ação sem o token da página"
        return ""
