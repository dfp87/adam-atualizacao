"""Leitura e padronização da planilha de entrada.

O que muda em relação ao `utils.py` anterior:

1. `tratar_valor` virou `nucleo.texto.para_numero`, que entende tanto
   "1.847,00" quanto "1,847.00". O anterior removia todos os pontos e trocava a
   vírgula: um valor no formato internacional (1.234,56 escrito como 1,234.56)
   era lido como 123456
2. `dataFato` deixa de ser convertida para texto no meio do caminho e volta a
   ser data; o texto "dd/mm/aaaa" é montado só na hora de enviar o payload
3. a função que descobre a coluna de id informa qual rótulo usou, em vez de
   escolher em silêncio
"""
from __future__ import annotations

import pandas as pd

from nucleo.texto import para_numero

# Rótulos aceitos, na ordem de preferência
COLUNAS_ID = ("idDevedor", "idIndividuo", "idTCE", "idGenerico", "id")
COLUNAS_VALOR = ("Valor do Registro", "valorOriginal", "Valor", "valor", "VALOR")

COLUNAS_SAIDA = ("id", "dataFato", "indicativoDebitoCredito", "valorOriginal")


def ler_excel(arquivo) -> pd.DataFrame:
    """Lê a planilha enviada pelo usuário."""
    return pd.read_excel(arquivo)


def _primeira_coluna(df: pd.DataFrame, candidatas) -> str:
    for coluna in candidatas:
        if coluna in df.columns:
            return coluna
    raise ValueError("Nenhuma das colunas esperadas foi encontrada: %s. "
                     "Colunas do arquivo: %s" % (list(candidatas), list(df.columns)))


def _converter_datas(serie: pd.Series) -> pd.Series:
    """Converte datas aceitando o formato brasileiro; se falhar, tenta o outro."""
    convertida = pd.to_datetime(serie, dayfirst=True, errors="coerce")
    if convertida.isna().any():
        alternativa = pd.to_datetime(serie, dayfirst=False, errors="coerce")
        if alternativa.notna().sum() > convertida.notna().sum():
            convertida = alternativa
    if convertida.isna().any():
        exemplo = serie[convertida.isna()].iloc[0]
        raise ValueError("Data não reconhecida na coluna dataFato: %r" % (exemplo,))
    return convertida


def preprocessar(df: pd.DataFrame) -> pd.DataFrame:
    """Devolve as quatro colunas que o cálculo usa, padronizadas.

    Convenção de sinal (mantida do app): valor negativo é crédito ('C'),
    positivo ou zero é débito ('D'); o valor enviado é sempre positivo.
    """
    dados = df.copy()

    coluna_id = _primeira_coluna(dados, COLUNAS_ID)
    valores_id = dados[coluna_id].astype(str).str.strip()
    if coluna_id != "id":
        dados = dados.drop(columns=["id"], errors="ignore")
        dados = dados.rename(columns={coluna_id: "id"})
    dados["id"] = valores_id

    if "dataFato" not in dados.columns:
        raise ValueError("Coluna 'dataFato' não encontrada. Colunas do arquivo: %s"
                         % list(dados.columns))
    dados["dataFato"] = _converter_datas(dados["dataFato"])

    coluna_valor = _primeira_coluna(dados, COLUNAS_VALOR)
    valores = dados[coluna_valor].apply(para_numero)

    dados["indicativoDebitoCredito"] = valores.apply(lambda v: "C" if v < 0 else "D")
    dados["valorOriginal"] = valores.abs()

    return dados[list(COLUNAS_SAIDA)]


def diagnostico(df: pd.DataFrame) -> dict:
    """O que foi reconhecido na planilha — para mostrar ao usuário e no log."""
    bruto = df.copy()
    info = {"colunas_arquivo": list(bruto.columns), "linhas": len(bruto)}
    try:
        info["coluna_id"] = _primeira_coluna(bruto, COLUNAS_ID)
    except ValueError:
        info["coluna_id"] = None
    try:
        info["coluna_valor"] = _primeira_coluna(bruto, COLUNAS_VALOR)
    except ValueError:
        info["coluna_valor"] = None
    if "dataFato" in bruto.columns:
        datas = pd.to_datetime(bruto["dataFato"], dayfirst=True, errors="coerce")
        info["datas_invalidas"] = int(datas.isna().sum())
    return info
