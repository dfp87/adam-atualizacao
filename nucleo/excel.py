"""Escrita de planilhas: um lugar só para gravar abas e ajustar colunas.

Motivo de existir: o bloco de ajuste de largura de coluna estava repetido 18
vezes em um único projeto (4 arquivos), e a rotina de acrescentar aba, em três
scripts que escreviam no mesmo arquivo sem combinar entre si.
"""
from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter


def ajustar_colunas(aba, limite: int = 50) -> None:
    """Largura de cada coluna pelo maior conteúdo, com teto."""
    for coluna in aba.columns:
        maior = 0
        for celula in coluna:
            if celula.value is not None:
                maior = max(maior, len(str(celula.value)))
        if coluna and coluna[0].column:
            aba.column_dimensions[get_column_letter(coluna[0].column)].width = min(maior + 2, limite)


def _linhas(dados) -> list[list]:
    """Aceita DataFrame do pandas, lista de listas ou lista de dicionários."""
    if hasattr(dados, "columns") and hasattr(dados, "itertuples"):        # DataFrame
        return [list(dados.columns)] + [list(linha) for linha in dados.itertuples(index=False, name=None)]
    if dados and isinstance(dados[0], dict):
        cabecalho = list(dados[0])
        return [cabecalho] + [[registro.get(c) for c in cabecalho] for registro in dados]
    return list(dados)


def gravar_abas(caminho: Path | str, abas: dict, ajustar: bool = True) -> Path:
    """Cria o arquivo do zero com as abas informadas: {nome_da_aba: dados}."""
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    livro = Workbook()
    livro.remove(livro.active)
    for nome, dados in abas.items():
        aba = livro.create_sheet(title=str(nome)[:31])
        for linha in _linhas(dados):
            aba.append(linha)
        if ajustar:
            ajustar_colunas(aba)
    livro.save(destino)
    return destino


def abas(caminho: Path | str) -> list[str]:
    livro = load_workbook(caminho, read_only=True)
    try:
        return list(livro.sheetnames)
    finally:
        livro.close()


def ler_abas(caminho: Path | str) -> dict:
    """Lê todas as abas de volta como listas de linhas — espelho de `gravar_abas`."""
    livro = load_workbook(caminho, read_only=True, data_only=True)
    try:
        return {nome: [list(linha) for linha in livro[nome].iter_rows(values_only=True)]
                for nome in livro.sheetnames}
    finally:
        livro.close()


def adicionar_aba(caminho: Path | str, nome: str, dados, substituir: bool = True,
                  ajustar: bool = True) -> Path:
    """Acrescenta (ou substitui) uma aba, preservando as demais do arquivo."""
    return atualizar_abas(caminho, {nome: dados}, substituir=substituir, ajustar=ajustar)


def atualizar_abas(caminho: Path | str, novas: dict, substituir: bool = True,
                   ajustar: bool = True) -> Path:
    """Grava várias abas em **uma** passada, preservando as demais do arquivo.

    `adicionar_aba` chamada em laço abre e salva o arquivo inteiro a cada aba: num
    livro de 12 MB com cinco abas, são cinco leituras e cinco gravações — minutos
    de espera por nada. Aqui o livro é lido uma vez e salvo uma vez.

    A ordem das abas que já existiam é preservada (a aba trocada fica no lugar
    dela); abas novas entram no fim, como fazia o `create_sheet`.
    """
    destino = Path(caminho)
    conteudo: dict = {}
    if destino.exists():
        livro = load_workbook(destino)
        try:
            for nome in livro.sheetnames:
                if nome in novas:
                    if not substituir:
                        raise ValueError("A aba %r já existe em %s" % (nome, destino))
                    conteudo[nome] = novas[nome]        # substitui no mesmo lugar
                else:
                    conteudo[nome] = [list(linha)
                                      for linha in livro[nome].iter_rows(values_only=True)]
        finally:
            livro.close()

    for nome, dados in novas.items():                   # abas novas entram no fim
        conteudo.setdefault(nome, dados)
    return gravar_abas(destino, conteudo, ajustar=ajustar)
