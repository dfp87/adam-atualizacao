"""Ponto de entrada do ADAM no Streamlit Community Cloud.

O Streamlit Cloud executa **um arquivo** (`Main file path`) e não permite escolher a pasta de trabalho.
Este arquivo só ajusta o caminho de importação — para `adam` e `nucleo` serem encontrados — e entrega a
execução ao `adam/app.py`, que é a página de verdade. Assim a estrutura do projeto continua a mesma:
nada foi movido nem duplicado para o deploy.

Por que não apontar direto para `adam/app.py` no painel: ali dentro há `from adam import ...`, e o
intérprete não acharia o pacote, porque a raiz do repositório não estaria no `sys.path`.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

runpy.run_path(str(RAIZ / "adam" / "app.py"), run_name="__main__")
