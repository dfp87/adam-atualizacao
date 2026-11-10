"""Painel de estatísticas de uso do ADAM.

Lê a mesma planilha de eventos que a telemetria grava e desenha os gráficos.

O que muda em relação ao `stats_usage.py` anterior:

1. **O cartão de downloads passa a contar downloads.** Ele procurava o evento
   `download`, que o app nunca registra — os eventos reais são
   `download_preparacao` e `download_concluido`. O número era sempre zero
2. **Sem gráfico repetido.** "Acessos por dia" (área) e "Evolução diária"
   (linha) eram o mesmo dado desenhado duas vezes
3. **Sem código morto:** saíram a matriz de calor que era montada e nunca usada
   (`heat_data`), os `import` de `Counter`, `numpy`, `os` e `datetime`, e a
   abertura da planilha passou a ser feita uma vez (era em três arquivos)
4. **Menos gráficos, mais leitura:** o mapa de países e a rosca de continentes
   viraram uma linha de texto quando há mais de um país — o público é brasileiro
   e o mapa por estado já responde a pergunta
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .config import Config

ORDEM_DIAS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DIAS_EM_PORTUGUES = dict(zip(ORDEM_DIAS, ["Segunda", "Terça", "Quarta", "Quinta",
                                          "Sexta", "Sábado", "Domingo"]))

# Nomes amigáveis para os eventos que o app realmente registra
ROTULOS = {
    "carregamento_app": "🔹 Carregamento do app",
    "upload_arquivo": "📂 Upload de arquivo",
    "aceite_termos": "📜 Aceite dos termos",
    "configuracao_atualizacao_data": "📅 Data de atualização",
    "configuracao_atualizacao_juros": "💸 Opção de juros",
    "processamento_iniciado": "🚀 Processamento iniciado",
    "processamento_concluido": "✅ Processamento concluído",
    "processamento_concluido_tempo": "⏱️ Tempo registrado",
    "processamento_concluido_qtde_individuos": "👥 Indivíduos registrados",
    "processamento_concluido_taxa_parcelas": "📦 Taxa registrada",
    "download_preparacao": "📋 Preparação de download",
    "download_concluido": "📥 Download concluído",
}

COLUNAS = ("timestamp", "evento", "detalhe", "sessao", "continente", "pais",
           "codigo_pais", "regiao", "nome_regiao", "cidade", "bairro",
           "latitude", "longitude", "navegador")

# A planilha real tem 15 colunas. Os nomes do cabeçalho não são os usados aqui
# (`action`, `fase`, `session`, `lat`, `long`...), então a leitura é feita por
# POSIÇÃO — como o código anterior fazia — e não por nome. Ler por nome, como a
# primeira versão desta revisão, devolvia uma tabela vazia.
COLUNAS_PLANILHA = 15


def preparar_tabela(registros: list[list]) -> pd.DataFrame:
    """Converte as linhas da planilha em tabela tratada."""
    if not registros or len(registros) <= 1:
        return pd.DataFrame(columns=COLUNAS)

    corpo = []
    for linha in registros[1:]:
        if isinstance(linha, (list, tuple)) and any(str(c).strip() for c in linha):
            corpo.append(list(linha)[:len(COLUNAS)] + [""] * max(0, len(COLUNAS) - len(linha)))

    if not corpo:
        return pd.DataFrame(columns=COLUNAS)

    tabela = pd.DataFrame(corpo, columns=list(COLUNAS))

    tabela["timestamp"] = pd.to_datetime(tabela["timestamp"], errors="coerce")
    tabela = tabela.dropna(subset=["timestamp"]).copy()
    tabela["data"] = tabela["timestamp"].dt.date
    tabela["hora"] = tabela["timestamp"].dt.hour
    tabela["dia_semana"] = tabela["timestamp"].dt.day_name()
    tabela["latitude"] = pd.to_numeric(tabela["latitude"], errors="coerce")
    tabela["longitude"] = pd.to_numeric(tabela["longitude"], errors="coerce")
    return tabela.sort_values("timestamp").reset_index(drop=True)


def indicadores(tabela: pd.DataFrame) -> dict:
    conta = lambda evento: int((tabela["evento"] == evento).sum())
    return {
        "eventos": len(tabela),
        "sessoes": int(tabela["sessao"].nunique()),
        "acessos": conta("carregamento_app"),
        "processamentos": conta("processamento_concluido"),
        "downloads": conta("download_concluido"),
    }


def desenhar(tabela: pd.DataFrame, cfg: Config | None = None) -> None:
    """Desenha o painel. Importa o Streamlit aqui dentro para o módulo poder
    ser testado sem interface."""
    import streamlit as st

    cfg = cfg or Config()
    numeros = indicadores(tabela)

    colunas = st.columns(5)
    for coluna, (rotulo, valor) in zip(colunas, [
        ("📌 Total de eventos", numeros["eventos"]),
        ("🧭 Sessões distintas", numeros["sessoes"]),
        ("👥 Acessos ao app", numeros["acessos"]),
        ("⚙️ Processamentos concluídos", numeros["processamentos"]),
        ("📥 Downloads concluídos", numeros["downloads"]),
    ]):
        coluna.metric(rotulo, valor)

    por_dia = tabela.groupby("data").size().reset_index(name="acessos")
    if not por_dia.empty:
        figura = px.area(por_dia, x="data", y="acessos", title="📅 Acessos por dia",
                         labels={"data": "Data", "acessos": "Eventos"},
                         template="plotly_white", color_discrete_sequence=["#2c3e50"])
        figura.update_traces(fill="tozeroy", line_color="#3498db")
        figura.update_layout(hovermode="x unified", height=400,
                             plot_bgcolor="rgba(0,0,0,0)", title_font_size=18)
        st.plotly_chart(figura, use_container_width=True)

    por_tipo = tabela["evento"].value_counts().reset_index()
    por_tipo.columns = ["evento", "quantidade"]
    por_tipo["rotulo"] = por_tipo["evento"].map(lambda e: ROTULOS.get(e, e))
    figura = px.bar(por_tipo.sort_values("quantidade"), y="rotulo", x="quantidade",
                    orientation="h", title="📊 Distribuição de eventos",
                    labels={"quantidade": "Quantidade", "rotulo": "Tipo de evento"},
                    template="plotly_white", color="quantidade",
                    color_continuous_scale="Blues", text="quantidade")
    figura.update_traces(textposition="outside", cliponaxis=False)
    figura.update_layout(height=400, showlegend=False)
    st.plotly_chart(figura, use_container_width=True)

    por_hora = tabela.groupby("hora").size().reset_index(name="acessos")
    por_dia_semana = (tabela.groupby("dia_semana").size().reset_index(name="acessos"))
    if not por_hora.empty and not por_dia_semana.empty:
        figura = go.Figure()
        figura.add_trace(go.Scatter(x=por_hora["hora"], y=por_hora["acessos"],
                                    mode="lines+markers", fill="tozeroy", name="Hora",
                                    line=dict(color="#e67e22", width=3)))
        figura.add_trace(go.Bar(x=[DIAS_EM_PORTUGUES.get(d, d) for d in por_dia_semana["dia_semana"]],
                                y=por_dia_semana["acessos"], name="Dia da semana",
                                marker_color="#2ecc71", text=por_dia_semana["acessos"],
                                textposition="outside", xaxis="x2"))
        figura.update_layout(
            title="⏱️ Padrão de acessos (hora do dia e dia da semana)", height=500,
            showlegend=False,
            grid=dict(rows=2, columns=1, pattern="independent"),
            xaxis=dict(title="Hora", domain=[0, 1]),
            xaxis2=dict(title="Dia da semana", anchor="y2"),
            yaxis=dict(title="Eventos"),
            yaxis2=dict(domain=[0, 0.45]),
        )
        st.plotly_chart(figura, use_container_width=True)

    cidades = tabela["cidade"].replace("", pd.NA).dropna().value_counts().head(10).reset_index()
    if not cidades.empty:
        cidades.columns = ["cidade", "acessos"]
        figura = px.bar(cidades, x="acessos", y="cidade", orientation="h",
                        title="🌍 Top 10 cidades de origem",
                        labels={"acessos": "Eventos", "cidade": "Cidade"},
                        template="plotly_white", color="acessos",
                        color_continuous_scale="Tealgrn", text="acessos")
        figura.update_traces(textposition="outside", cliponaxis=False)
        figura.update_layout(height=450)
        st.plotly_chart(figura, use_container_width=True)

    _mapa(tabela, cfg)

    paises = tabela["pais"].replace("", pd.NA).dropna().value_counts()
    if len(paises) > 1:
        st.caption("Acessos por país: " + " · ".join("%s (%d)" % (p, n) for p, n in paises.items()))


def _mapa(tabela: pd.DataFrame, cfg: Config) -> None:
    """Mapa por estado, com as cidades em pontos."""
    import streamlit as st

    estados = tabela["regiao"].replace("", pd.NA).dropna().str.upper().str.strip()
    pontos = tabela.dropna(subset=["latitude", "longitude"])
    if estados.empty or pontos.empty:
        st.info("Dados insuficientes para exibir o mapa geográfico.")
        return

    try:
        import requests
        geo = requests.get(cfg.geo_geo_json, timeout=20).json()
    except Exception as erro:
        st.warning("Não foi possível carregar o mapa: %s" % erro)
        return

    por_estado = estados.value_counts().reset_index()
    por_estado.columns = ["regiao", "eventos"]

    figura = go.Figure()
    figura.add_trace(go.Choropleth(
        geojson=geo, locations=por_estado["regiao"], z=por_estado["eventos"],
        featureidkey="properties.sigla", colorscale="Blues", colorbar_title="Eventos",
        marker_line_color="white", marker_line_width=0.5, name="Estados"))
    figura.add_trace(go.Scattergeo(
        lon=pontos["longitude"], lat=pontos["latitude"],
        text=pontos["cidade"], mode="markers",
        marker=dict(size=8, color="red", opacity=0.7, line=dict(width=0.5, color="white")),
        name="Localidades"))
    figura.update_layout(title="🗺️ Mapa: acessos por estado e localidade", height=600,
                         geo=dict(scope="south america", fitbounds="locations",
                                  visible=False, projection_type="mercator"),
                         margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(figura, use_container_width=True)


def mostrar_painel(tabela: pd.DataFrame, cfg: Config | None = None) -> None:
    """Ponto de entrada do painel na página."""
    if tabela.empty:
        import streamlit as st
        st.info("📭 Ainda não há dados de uso para exibir. Após algumas execuções do app, "
                "as estatísticas aparecerão aqui.")
        return
    desenhar(tabela, cfg)
