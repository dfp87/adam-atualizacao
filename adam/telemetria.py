"""Registro anônimo de uso.

O que muda em relação ao `app.py` anterior:

1. **A falha deixa de ser silenciosa.** A função de geolocalização devolvia dois
   valores quando não conseguia localizar o IP e nove quando conseguia; o
   chamador sempre esperava nove, então estourava e o `except` engolia tudo —
   exatamente os eventos com geolocalização se perdiam sem aviso
2. **Duas consultas por evento viram uma por sessão.** Cada evento consultava
   `api.ipify.org` e `ip-api.com`; o IP não muda dentro da sessão, então o
   resultado é reaproveitado
3. **Um só construtor de linha**, usado pelo registro assíncrono e pelo
   síncrono — antes eram dois blocos de 30 linhas idênticas
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime

import requests

from .config import Config

CABECALHO_EVENTOS = ("timestamp", "evento", "detalhe", "sessao", "continente", "pais",
                     "codigo_pais", "regiao", "nome_regiao", "cidade", "bairro",
                     "latitude", "longitude", "navegador")


@dataclass
class Geolocalizacao:
    """Resultado da localização por IP. Sempre completo — vazio quando não deu."""
    continente: str = ""
    pais: str = ""
    codigo_pais: str = ""
    regiao: str = ""
    nome_regiao: str = ""
    cidade: str = ""
    bairro: str = ""
    latitude: object = ""
    longitude: object = ""

    def como_linha(self) -> list:
        # bairro vazio cai para a cidade, como no comportamento original
        return [self.continente or "", self.pais or "", self.codigo_pais or "",
                self.regiao or "", self.nome_regiao or "", self.cidade or "",
                self.bairro or self.cidade or "", self.latitude or "",
                self.longitude or ""]


def ip_publico(timeout: int = 5) -> str | None:
    try:
        return requests.get("https://api.ipify.org", timeout=timeout).text
    except Exception:
        return None


def geolocalizacao(ip: str | None, timeout: int = 5) -> Geolocalizacao:
    """Localiza o IP. Devolve sempre o mesmo tipo, com ou sem sucesso."""
    if not ip:
        return Geolocalizacao()
    try:
        url = ("http://ip-api.com/json/%s?fields=status,continent,country,countryCode,"
               "region,regionName,city,district,lat,lon" % ip)
        dados = requests.get(url, timeout=timeout).json()
        if dados.get("status") != "success":
            return Geolocalizacao()
        return Geolocalizacao(
            continente=dados.get("continent"), pais=dados.get("country"),
            codigo_pais=dados.get("countryCode"), regiao=dados.get("region"),
            nome_regiao=dados.get("regionName"), cidade=dados.get("city"),
            bairro=dados.get("district"), latitude=dados.get("lat"),
            longitude=dados.get("lon"),
        )
    except Exception:
        return Geolocalizacao()


def montar_linha(evento: str, detalhe: str, sessao: str, geo: Geolocalizacao,
                 navegador: str, momento: datetime | None = None) -> list:
    """Linha da planilha de eventos, na ordem que já estava em uso."""
    quando = (momento or datetime.now()).isoformat()
    return [quando, evento, detalhe, sessao] + geo.como_linha() + [(navegador or "desconhecido")[:100]]


class Telemetria:
    """Grava eventos na planilha de uso.

    `abrir_aba` é uma função que devolve a aba (permite cache do Streamlit).
    `navegador` é uma função que devolve o User-Agent do visitante.
    """

    def __init__(self, abrir_aba, sessao: str, cfg: Config | None = None, navegador=None):
        self.cfg = cfg or Config()
        self.abrir_aba = abrir_aba
        self.sessao = sessao
        self.navegador = navegador or (lambda: "desconhecido")
        self._geo: Geolocalizacao | None = None

    def localizacao(self) -> Geolocalizacao:
        """Consultada uma vez por sessão e reaproveitada."""
        if self._geo is None:
            self._geo = geolocalizacao(ip_publico())
        return self._geo

    def linha(self, evento: str, detalhe: str = "") -> list:
        return montar_linha(evento, detalhe, self.sessao, self.localizacao(), self.navegador())

    def registrar(self, evento: str, detalhe: str = "") -> None:
        """Registro assíncrono, para não atrasar a página."""
        def _gravar():
            try:
                self.abrir_aba().append_row(self.linha(evento, detalhe))
            except Exception as erro:
                # Antes era um print; agora o erro fica visível no log da aplicação
                print("[telemetria] falha ao registrar %s: %s" % (evento, erro))
        threading.Thread(target=_gravar, daemon=True).start()

    def registrar_agora(self, evento: str, detalhe: str = "") -> bool:
        """Registro síncrono, para eventos críticos (downloads). Devolve se deu certo."""
        try:
            self.abrir_aba().append_row(self.linha(evento, detalhe))
            return True
        except Exception as erro:
            print("[telemetria] falha ao registrar %s: %s" % (evento, erro))
            return False
