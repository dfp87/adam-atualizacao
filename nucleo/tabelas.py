"""Leitura de CSV e planilhas tolerante ao que aparece na prática.

Motivo de existir: o GSISTE tinha detecção de encoding e separador embutida no
`main.py` e o ColetorSEI fazia a sua própria leitura, cada um com um conjunto
diferente de tentativas. Aqui as tentativas são as mesmas para todos.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

ENCODINGS = ("utf-8-sig", "utf-8", "cp1252", "latin-1")
SEPARADORES = (";", ",", "\t", "|")


def detectar_encoding(caminho: Path | str, amostra: int = 256 * 1024) -> str:
    """Primeiro encoding que decodifica a amostra sem erro."""
    dados = Path(caminho).read_bytes()[:amostra]
    for codificacao in ENCODINGS:
        try:
            dados.decode(codificacao)
            return codificacao
        except UnicodeDecodeError:
            continue
    return "latin-1"                                    # sempre decodifica


def detectar_separador(texto: str) -> str:
    """Separador com a contagem mais estável nas primeiras linhas."""
    linhas = [l for l in texto.splitlines()[:20] if l.strip()]
    if not linhas:
        return ";"
    melhor, maior = ";", -1
    for candidato in SEPARADORES:
        contagens = [linha.count(candidato) for linha in linhas]
        constantes = [c for c in contagens if c > 0]
        if not constantes:
            continue
        if len(set(constantes)) == 1 and constantes[0] > maior:
            melhor, maior = candidato, constantes[0]
    return melhor


def ler_csv(caminho: Path | str, sep: str | None = None, encoding: str | None = None,
            colunas: list[str] | None = None):
    """Lê o CSV e devolve um DataFrame, detectando encoding e separador.

    `colunas` permite renomear por posição, para arquivos sem cabeçalho.
    """
    import pandas as pd

    caminho = Path(caminho)
    codificacao = encoding or detectar_encoding(caminho)
    texto = caminho.read_text(encoding=codificacao, errors="replace")
    separador = sep or detectar_separador(texto)
    dados = pd.read_csv(io.StringIO(texto), sep=separador, dtype=str,
                        keep_default_na=False, na_values=[""])
    dados.attrs["encoding"] = codificacao
    dados.attrs["separador"] = separador
    if colunas:
        if len(colunas) != len(dados.columns):
            raise ValueError("%s: esperava %d colunas, achou %d"
                             % (caminho.name, len(colunas), len(dados.columns)))
        dados.columns = colunas
    return dados


def ler_tabela(caminho: Path | str, sep: str = ";", encoding: str = "utf-8-sig", **kwargs):
    """Lê CSV ou XLSX **do próprio projeto** (convenção: ';' e utf-8-sig).

    Diferente de `ler_csv`, que é para arquivo de fora e detecta encoding e
    separador: aqui o formato é o que o projeto grava, e os tipos do pandas são
    preservados (sem `dtype=str`). XLSX vai pelo openpyxl.

    Era o `pd.read_csv(..., sep=';', encoding='utf-8-sig')` copiado em sete
    lugares do GSISTE, mais o despacho por extensão repetido em dois arquivos.
    """
    import pandas as pd

    caminho = Path(caminho)
    if caminho.suffix.lower() in {".xlsx", ".xls", ".xlsm"}:
        kwargs.setdefault("engine", "openpyxl")
        return pd.read_excel(caminho, **kwargs)
    return pd.read_csv(caminho, sep=sep, encoding=encoding, **kwargs)


def gravar_csv(caminho: Path | str, dados, sep: str = ";", encoding: str = "utf-8-sig",
               index: bool = False, **kwargs) -> Path:
    """Grava o DataFrame no formato do projeto: ';' e utf-8-sig, sem o índice.

    A convenção estava escrita 12 vezes no GSISTE, e uma delas sem o `sep` — que
    é exatamente o defeito que a centralização evita.
    """
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    dados.to_csv(destino, sep=sep, encoding=encoding, index=index, **kwargs)
    return destino


def gravar_xlsx(caminho: Path | str, dados, aba: str | None = None, index: bool = False,
                **kwargs) -> Path:
    """Grava o DataFrame em XLSX pelo openpyxl.

    `aba=None` mantém o nome padrão do pandas ("Sheet1"), como as chamadas que
    não informavam `sheet_name` faziam.
    """
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    kwargs.setdefault("engine", "openpyxl")
    if aba is not None:
        kwargs["sheet_name"] = aba
    dados.to_excel(destino, index=index, **kwargs)
    return destino


def inspecionar(caminho: Path | str, linhas: int = 3) -> dict:
    """Diagnóstico de um CSV: encoding, separador, colunas e amostra.

    Substitui os três scripts de diagnóstico (`diagnostico.py`,
    `diagnostico_completo.py`, `inspect_csv.py`) que existiam no GSISTE.
    """
    caminho = Path(caminho)
    codificacao = detectar_encoding(caminho)
    texto = caminho.read_text(encoding=codificacao, errors="replace")
    separador = detectar_separador(texto)
    leitor = csv.reader(io.StringIO(texto), delimiter=separador)
    cabecalho = next(leitor, [])
    amostra = []
    for i, linha in enumerate(leitor):
        if i >= linhas:
            break
        amostra.append(linha)
    return {"arquivo": caminho.name, "encoding": codificacao, "separador": separador,
            "colunas": cabecalho, "quantidade_colunas": len(cabecalho), "amostra": amostra}
