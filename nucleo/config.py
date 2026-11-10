"""Parâmetros por linha de comando e por variável de ambiente.

Motivo de existir: caminhos, URLs, limites e pausas estavam escritos dentro do
código nos quatro projetos — trocar a lista de entrada do ColetorSEI exigia
editar o arquivo; o GSISTE tinha caminhos absolutos de uma máquina específica.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path


def criar_parser(descricao: str, prog: str | None = None) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(prog=prog, description=descricao,
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)


def parametro(parser: argparse.ArgumentParser, nome: str, prefixo: str, padrao=None,
              tipo=str, ajuda: str = ""):
    """Acrescenta um argumento cujo padrão vem do ambiente (PREFIXO_NOME)."""
    chave = "%s_%s" % (prefixo.upper(), nome.upper().replace("-", "_"))
    padrao = os.environ.get(chave, padrao)
    if tipo is Path and padrao is not None:
        padrao = Path(padrao)
    elif tipo is int and padrao is not None:
        padrao = int(padrao)
    elif tipo is bool and padrao is not None:
        padrao = str(padrao).lower() in {"1", "true", "sim", "yes"}
    return parser.add_argument("--" + nome, type=tipo, default=padrao, help=ajuda)


def valor(nome: str, prefixo: str, padrao, tipo=None):
    """Valor vindo do ambiente (PREFIXO_NOME) convertido para `tipo`, ou o padrão.

    É o mesmo mecanismo do `parametro`, para quem não usa linha de comando:
    número, booleano, caminho ou texto. Ambiente vazio conta como não definido.
    """
    chave = "%s_%s" % (prefixo.upper(), nome.upper().replace("-", "_"))
    bruto = os.environ.get(chave)
    if bruto is None or bruto == "":
        return padrao
    if tipo is None or tipo is str:
        return bruto
    if tipo is Path:
        return Path(bruto)
    if tipo is bool:
        return str(bruto).strip().lower() in {"1", "true", "sim", "yes", "s"}
    return tipo(bruto)


def caminho(nome: str, prefixo: str, padrao: str) -> Path:
    """Caminho vindo do ambiente (PREFIXO_NOME) ou o padrão."""
    return valor(nome, prefixo, Path(padrao), Path)


def preparar_pastas(*pastas: Path | str) -> None:
    for pasta in pastas:
        if pasta:
            Path(pasta).mkdir(parents=True, exist_ok=True)
