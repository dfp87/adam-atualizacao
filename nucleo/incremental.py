"""Controle incremental: o que já foi processado e o que mudou.

Motivo de existir: o GSISTE tinha um controle por hash dos arquivos de entrada
e o LeitorPDF, outro por lista de nomes. Aqui fica um só, com a mesma ideia:
registrar uma linha por item, com impressão digital suficiente para saber se o
arquivo mudou, sem reler o conteúdo inteiro de arquivos grandes.

A impressão digital é caminho + tamanho + data de modificação; para arquivos
pequenos, também o hash do conteúdo. Acima de `limite_hash`, o hash é parcial
(começo e fim do arquivo) — o suficiente para detectar troca de conteúdo sem
pagar o custo de ler 500 MB.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

BLOCO = 64 * 1024


def hash_parcial(caminho: Path, limite: int = 2 * 1024 * 1024) -> str:
    """Hash do arquivo: inteiro se for pequeno, do começo e do fim se for grande."""
    tamanho = os.path.getsize(caminho)
    digestor = hashlib.sha1()
    with open(caminho, "rb") as f:
        if tamanho <= limite:
            digestor.update(f.read())
        else:
            digestor.update(f.read(BLOCO))
            f.seek(max(0, tamanho - BLOCO))
            digestor.update(f.read(BLOCO))
            digestor.update(str(tamanho).encode())
    return digestor.hexdigest()[:16]


@dataclass
class Registro:
    rel: str
    tamanho: int = 0
    mtime: int = 0
    hash: str = ""
    erro: str | None = None
    extras: dict = field(default_factory=dict)

    def como_dicionario(self) -> dict:
        dados = {"rel": self.rel, "tamanho": self.tamanho, "mtime": self.mtime,
                 "hash": self.hash, "erro": self.erro}
        dados.update(self.extras)
        return dados


class Indice:
    """Índice em JSONL: uma linha por item, gravada por acréscimo."""

    def __init__(self, caminho: Path | str):
        self.caminho = Path(caminho)

    def carregar(self) -> dict[str, dict]:
        registros: dict[str, dict] = {}
        if not self.caminho.exists():
            return registros
        with open(self.caminho, encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                try:
                    dados = json.loads(linha)
                except json.JSONDecodeError:
                    continue
                if isinstance(dados, dict) and dados.get("rel"):
                    registros[dados["rel"]] = dados
        return registros

    def registrar(self, registro: Registro | dict) -> None:
        dados = registro.como_dicionario() if isinstance(registro, Registro) else registro
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(self.caminho, "a", encoding="utf-8") as f:
            f.write(json.dumps(dados, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())


def impressao(caminho: Path, com_hash: bool = True) -> tuple[int, int, str]:
    info = caminho.stat()
    return info.st_size, int(info.st_mtime), (hash_parcial(caminho) if com_hash else "")


def precisa_processar(caminho: Path, raiz: Path, registros: dict[str, dict],
                      reprocessar: bool = False, com_hash: bool = True) -> bool:
    """Refaz o item se for novo, se mudou de tamanho/data/hash ou se falhou antes."""
    if reprocessar:
        return True
    rel = str(Path(caminho).relative_to(raiz))
    registro = registros.get(rel)
    if registro is None or registro.get("erro"):
        return True
    try:
        tamanho, mtime, digesto = impressao(Path(caminho), com_hash)
    except OSError:
        return True
    if registro.get("tamanho") != tamanho or registro.get("mtime") != mtime:
        return True
    if com_hash and registro.get("hash") and registro["hash"] != digesto:
        return True
    return False
