"""Log único e idempotente, compartilhado pelos projetos.

Motivo de existir: cada projeto tinha a sua versão, e duas delas adicionavam
um handler novo a cada chamada — o log saía duplicado quando o módulo era
importado mais de uma vez.
"""
from __future__ import annotations

import logging
from pathlib import Path

FORMATO = "%(asctime)s [%(levelname)s] %(message)s"


def obter_logger(nome: str = "projeto", arquivo: Path | str | None = None,
                 nivel: int = logging.INFO) -> logging.Logger:
    """Devolve o logger do projeto, com console e (opcionalmente) arquivo.

    Chamar várias vezes não multiplica handlers.
    """
    logger = logging.getLogger(nome)
    logger.setLevel(nivel)

    if not logger.handlers:
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(FORMATO))
        logger.addHandler(console)

    tem_arquivo = any(isinstance(h, logging.FileHandler) for h in logger.handlers)
    if arquivo is not None and not tem_arquivo:
        Path(arquivo).parent.mkdir(parents=True, exist_ok=True)
        de_arquivo = logging.FileHandler(arquivo, encoding="utf-8")
        de_arquivo.setFormatter(logging.Formatter(FORMATO))
        logger.addHandler(de_arquivo)

    return logger
