"""`python -m central` — sobe a Central em http://127.0.0.1:8765 (ADR-012)."""
import logging
import logging.handlers
import sys

import uvicorn

from . import config
from .app import criar_app


def main() -> None:
    config.ESTADO.mkdir(parents=True, exist_ok=True)
    manipuladores = [logging.handlers.RotatingFileHandler(config.ESTADO / "central.log", maxBytes=5_000_000,
                                                          backupCount=2, encoding="utf-8")]
    if sys.stderr is not None:          # pythonw (tarefa agendada) não tem console
        manipuladores.append(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO, handlers=manipuladores,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = criar_app()
    print(f"Central do Braziliation em http://{config.HOST}:{config.PORTA}  (Ctrl+C encerra)")
    uvicorn.run(app, host=config.HOST, port=config.PORTA, log_config=None, access_log=False)


if __name__ == "__main__":
    main()
