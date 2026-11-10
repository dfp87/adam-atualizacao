"""Cliente da API de Cálculo de Débito do TCU e montagem dos relatórios.

Preserva o contrato que o app já usava:

- uma requisição por `id` (devedor), com os lançamentos ordenados por data
- corpo: `{dataAtualizacao: 'dd/mm/aaaa', aplicaJuros: bool, parcelasDebito:
  [{dataFato, indicativoDebitoCredito, valorOriginal}]}`
- resposta validada nos quatro saldos obrigatórios
- pausa entre requisições conforme o tamanho do grupo (0,2 / 0,4 / 0,6 s)
- devedor com erro entra no resultado com `status` = "ERRO: ...", sem derrubar
  os demais

O que muda: repetição automática em falha transitória de rede, resposta 429 ou
5xx (antes, um tropeço momentâneo marcava o devedor como erro definitivo) e a
data circula como data, não como texto.
"""
from __future__ import annotations

import time
from datetime import datetime

import pandas as pd
import requests

from .config import Config

CAMPOS_OBRIGATORIOS = ("saldoDebito", "saldoVariacaoSelic", "saldoJuros", "saldoTotal")
CABECALHOS = {"Content-Type": "application/json", "Accept": "application/json"}
STATUS_TRANSITORIOS = {429, 500, 502, 503, 504}


def montar_parcelas(grupo: pd.DataFrame) -> list[dict]:
    """Parcelas do payload, ordenadas por data e arredondadas a 2 casas."""
    ordenado = grupo.sort_values("dataFato")
    return [
        {
            "dataFato": pd.to_datetime(linha["dataFato"]).strftime("%d/%m/%Y"),
            "indicativoDebitoCredito": linha["indicativoDebitoCredito"],
            "valorOriginal": float(round(linha["valorOriginal"], 2)),
        }
        for _, linha in ordenado.iterrows()
    ]


def montar_payload(data_atualizacao: str, aplica_juros: bool, parcelas: list[dict]) -> dict:
    return {"dataAtualizacao": data_atualizacao, "aplicaJuros": bool(aplica_juros),
            "parcelasDebito": parcelas}


def enviar(payload: dict, cfg: Config, pausa: float = 0.0, sessao=None) -> dict:
    """Envia o payload e devolve a resposta validada.

    Repete a chamada em falha transitória. Erro definitivo vira exceção com o
    texto da resposta, como antes.
    """
    pedir = (sessao or requests).post
    ultimo_erro = None

    for tentativa in range(1, max(1, cfg.tentativas) + 1):
        try:
            resposta = pedir(cfg.api_url, json=payload, headers=CABECALHOS,
                             timeout=(cfg.timeout_conexao, cfg.timeout_leitura))
            if resposta.status_code in STATUS_TRANSITORIOS:
                raise requests.HTTPError("HTTP %s" % resposta.status_code)
            if resposta.status_code != 200:
                raise Exception(resposta.text)
            dados = resposta.json()
            for campo in CAMPOS_OBRIGATORIOS:
                if campo not in dados:
                    raise Exception("Campo ausente no retorno: %s" % campo)
            time.sleep(pausa)
            return dados
        except Exception as erro:
            ultimo_erro = erro
            transitorio = isinstance(erro, (requests.ConnectionError, requests.Timeout,
                                            requests.HTTPError))
            if not transitorio or tentativa == max(1, cfg.tentativas):
                raise
            time.sleep(cfg.espera_retry * tentativa)

    raise ultimo_erro if ultimo_erro else RuntimeError("falha desconhecida")


def log_lancamentos(id_devedor: str, grupo: pd.DataFrame, payload: dict,
                    resposta: dict) -> list[dict]:
    """Uma linha de log por lançamento enviado — formato preservado do app."""
    momento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registros = []
    for _, linha in grupo.sort_values("dataFato").iterrows():
        registros.append({
            "id": id_devedor,
            "dataFato": linha["dataFato"],
            "indicativoDebitoCredito": linha["indicativoDebitoCredito"],
            "valorOriginal_Decimal": str(linha["valorOriginal"]),
            "valorOriginal_Enviado_API": float(linha["valorOriginal"]),
            "payload_dataAtualizacao": payload["dataAtualizacao"],
            "aplicaJuros": payload["aplicaJuros"],
            "saldoDebito_API": resposta.get("saldoDebito"),
            "saldoVariacaoSelic_API": resposta.get("saldoVariacaoSelic"),
            "saldoJuros_API": resposta.get("saldoJuros"),
            "saldoTotal_API": resposta.get("saldoTotal"),
            "timestampProcessamento": momento,
        })
    return registros


def calcular_por_devedor(df_lancamentos: pd.DataFrame, data_atualizacao: str,
                         aplica_juros: bool = True, progress_callback=None,
                         cfg: Config | None = None, sessao=None):
    """Processa os lançamentos por devedor e devolve (resultado, log)."""
    cfg = cfg or Config()
    dados = df_lancamentos.copy()
    dados["id"] = dados["id"].astype(str).str.strip()
    grupos = list(dados.groupby("id", dropna=False))
    total = len(grupos)

    resultados, logs = [], []
    for indice, (id_devedor, grupo) in enumerate(grupos):
        try:
            parcelas = montar_parcelas(grupo)
            payload = montar_payload(data_atualizacao, aplica_juros, parcelas)
            resposta = enviar(payload, cfg, pausa=cfg.pausa_para(len(grupo)), sessao=sessao)

            resultados.append({
                "id": str(id_devedor),
                "dataAtualizacao": resposta["data"],
                "saldoDebito": resposta["saldoDebito"],
                "saldoVariacaoSelic": resposta["saldoVariacaoSelic"],
                "saldoJuros": resposta["saldoJuros"],
                "saldoTotal": resposta["saldoTotal"],
                "status": "Ok",
            })
            logs.extend(log_lancamentos(str(id_devedor), grupo, payload, resposta))

        except Exception as erro:
            resultados.append({
                "id": str(id_devedor),
                "dataAtualizacao": data_atualizacao,
                "saldoTotal": None,
                "status": "ERRO: %s" % erro,
            })

        if progress_callback:
            progress_callback(indice + 1, total)

    df_resultado = pd.DataFrame(resultados)
    df_log = pd.DataFrame(logs)
    if not df_resultado.empty:
        df_resultado["id"] = df_resultado["id"].astype("string")
    if not df_log.empty:
        df_log["id"] = df_log["id"].astype("string")
    return df_resultado, df_log
