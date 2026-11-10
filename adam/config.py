"""Parâmetros do ADAM, num lugar só.

Antes: URL da API, prazos, pausas, nomes das planilhas e o caminho da foto
estavam espalhados em `core.py`, `app.py`, `users.py` e `stats_usage.py`.
Agora vêm daqui e podem ser trocados por variável de ambiente ou linha de
comando, sem editar código.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

API_PADRAO = "https://divida.apps.tcu.gov.br/api/publico/calculadora/calcular-saldos-debito"

# Faixas de pausa entre requisições, por quantidade de parcelas do devedor.
# Valores idênticos aos que o app já usava — a API do TCU é pública e não deve
# ser sobrecarregada.
FAIXAS_PAUSA = ((20, 0.2), (100, 0.4))

RAIZ = Path(__file__).resolve().parent.parent


@dataclass
class Config:
    api_url: str = field(default_factory=lambda: os.environ.get("ADAM_API_URL", API_PADRAO))
    timeout_conexao: int = 10
    timeout_leitura: int = 60
    tentativas: int = 3           # em erro de rede, 429 ou 5xx
    espera_retry: float = 2.0     # dobra a cada tentativa
    planilha_eventos: str = "log_usage_app_ADAM"
    planilha_cadastro: str = "cadastro_usuarios_ADAM"
    fuso: str = "America/Sao_Paulo"
    imagem_autor: Path = RAIZ / "assets" / "eu.jpg"
    geo_geo_json: str = ("https://raw.githubusercontent.com/codeforamerica/"
                         "click_that_hood/master/public/data/brazil-states.geojson")

    def pausa_para(self, quantidade_parcelas: int) -> float:
        """Pausa entre requisições, conforme o tamanho do grupo."""
        for limite, pausa in FAIXAS_PAUSA:
            if quantidade_parcelas <= limite:
                return pausa
        return 0.6
