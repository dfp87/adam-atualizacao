"""Acesso a Google Sheets com a credencial fora do código.

Motivo de existir: o ADAM repetia o mesmo bloco de abrir planilha em três
arquivos, e a credencial morava dentro do projeto (`.streamlit/secrets.toml`),
com um `gitignore.txt` sem ponto que nunca a protegeu.

Aqui a credencial entra por parâmetro, por variável de ambiente
(`GOOGLE_SERVICE_ACCOUNT`, com o JSON inteiro, ou `GOOGLE_APPLICATION_CREDENTIALS`,
com o caminho do arquivo) ou pelo `st.secrets`, quando existir.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ESCOPOS = ("https://www.googleapis.com/auth/spreadsheets",
           "https://www.googleapis.com/auth/drive")

VARIAVEL_JSON = "GOOGLE_SERVICE_ACCOUNT"
VARIAVEL_ARQUIVO = "GOOGLE_APPLICATION_CREDENTIALS"


class CredencialAusente(RuntimeError):
    """A credencial do Google não foi encontrada.

    É um `RuntimeError` de propósito: quem chama de dentro de uma aplicação
    (Streamlit, por exemplo) consegue tratar com `except Exception`. Um
    `SystemExit` atravessaria qualquer tratamento e encerraria o processo.
    """


def credencial(valor=None) -> dict:
    """Resolve a credencial de serviço: dict, JSON em texto, caminho ou ambiente."""
    if isinstance(valor, dict):
        return valor
    if isinstance(valor, str) and valor.strip().startswith("{"):
        return json.loads(valor)
    if isinstance(valor, (str, Path)) and Path(str(valor)).is_file():
        return json.loads(Path(valor).read_text(encoding="utf-8"))

    if os.environ.get(VARIAVEL_JSON):
        return json.loads(os.environ[VARIAVEL_JSON])
    if os.environ.get(VARIAVEL_ARQUIVO):
        return json.loads(Path(os.environ[VARIAVEL_ARQUIVO]).read_text(encoding="utf-8"))

    try:                                        # Streamlit (opcional)
        import streamlit as st
        bruto = st.secrets["gcp_service_account"]
        return json.loads(bruto) if isinstance(bruto, str) else dict(bruto)
    except Exception as erro:
        raise CredencialAusente(
            "Credencial do Google não encontrada. Defina %s (JSON) ou %s (caminho do arquivo). "
            "Último erro: %s" % (VARIAVEL_JSON, VARIAVEL_ARQUIVO, erro)
        ) from erro


def cliente(valor=None):
    """Cliente gspread autenticado."""
    import gspread
    from google.oauth2.service_account import Credentials

    return gspread.authorize(Credentials.from_service_account_info(credencial(valor), scopes=list(ESCOPOS)))


def abrir_planilha(nome_ou_id: str, valor=None):
    """Abre a planilha pelo nome ou pelo id da URL."""
    return cliente(valor).open_by_key(nome_ou_id) if _parece_id(nome_ou_id) else cliente(valor).open(nome_ou_id)


def aba(nome_ou_id: str, nome_aba: str | None = None, valor=None):
    """Aba da planilha (a primeira, se não for dito qual)."""
    planilha = abrir_planilha(nome_ou_id, valor)
    return planilha.worksheet(nome_aba) if nome_aba else planilha.sheet1


def acrescentar(nome_ou_id: str, linhas: list[list], nome_aba: str | None = None, valor=None) -> int:
    """Acrescenta linhas ao fim da aba e devolve quantas entraram."""
    planilha_aba = aba(nome_ou_id, nome_aba, valor)
    if isinstance(linhas, (list, tuple)) and linhas and not isinstance(linhas[0], (list, tuple)):
        linhas = [linhas]
    planilha_aba.append_rows([list(l) for l in linhas], value_input_option="USER_ENTERED")
    return len(linhas)


def _parece_id(valor: str) -> bool:
    return bool(valor) and " " not in str(valor) and len(str(valor)) >= 25
