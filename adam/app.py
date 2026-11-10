"""A página do ADAM.

Aqui fica só a montagem da tela e a ordem dos passos. O cálculo está em `core`,
a planilha em `planilha`, o registro de uso em `telemetria`, os gráficos em
`painel` e os textos em `textos` — antes tudo isso estava neste arquivo, com
707 linhas.

O fluxo é o que já existia: consentimento → estatísticas → demonstração →
cadastro → upload → padronização → data e juros → termos → cálculo → relatórios.
"""
from __future__ import annotations

import io
import time
import uuid
import zipfile
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from nucleo import sheets
from nucleo.texto import extrair_data_de_nome_de_arquivo

from adam import core, painel, planilha, telemetria, textos, usuarios
from adam.config import Config

CFG = Config()
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# ==================== APOIO ====================
@st.cache_resource
def aba(nome: str):
    """Aba do Google Sheets, aberta uma vez por processo do servidor."""
    return sheets.aba(nome)


@st.cache_data(ttl=3600)
def tabela_de_uso() -> pd.DataFrame:
    return painel.preparar_tabela(aba(CFG.planilha_eventos).get_all_values())


def sessao() -> str:
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid.uuid4().hex
    return st.session_state.session_id


def registrar() -> telemetria.Telemetria:
    if "telemetria" not in st.session_state:
        st.session_state.telemetria = telemetria.Telemetria(
            abrir_aba=lambda: aba(CFG.planilha_eventos),
            sessao=sessao(), cfg=CFG,
            navegador=lambda: st.context.headers.get("User-Agent", "desconhecido"))
    return st.session_state.telemetria


def exigir_consentimento(tel: telemetria.Telemetria) -> None:
    if "consentimento_dado" not in st.session_state:
        st.session_state.consentimento_dado = False
        st.session_state.carregamento_registrado = False

    if st.session_state.consentimento_dado:
        if not st.session_state.carregamento_registrado:
            tel.registrar("carregamento_app", "Página principal carregada (sessão existente)")
            st.session_state.carregamento_registrado = True
        return

    st.warning("📜 **Aviso de Privacidade**")
    st.markdown(textos.AVISO_PRIVACIDADE)
    if st.checkbox("✅ Eu li e concordo com a Política de Privacidade."):
        st.session_state.consentimento_dado = True
        st.session_state.carregamento_registrado = True
        tel.registrar("carregamento_app", "Usuário registrou o seu consentimento e página "
                                          "principal do App foi carregada")
        st.rerun()

    st.info("Por favor, marque a caixa para concordar e prosseguir.")
    st.stop()


def barra_lateral() -> bool:
    """Instruções, termos e a foto do autor. Devolve se os termos foram aceitos."""
    with st.sidebar:
        if CFG.imagem_autor.exists():
            st.image(str(CFG.imagem_autor), width=150)
        st.caption("""
               **Powered by / Desenvolvido por:**         
               ***Douglas Ferreira Pinto***         
               *PhD Student in PPGGTD/UFT*         
               *Doutorando do PPGGTD/UFT*         
               *email: ferreira.douglas@mail.uft.edu.br*         
               """)
        st.caption("""
               **Profile links/Links de perfil:**
               *https://www.linkedin.com/in/douglas-ferreira-pinto/*
               *https://lattes.cnpq.br/0434254283119819*
               """)
        st.divider()
        st.header("Instruções:")
        st.markdown(textos.INSTRUCOES_PLANILHA)
        st.divider()
        with st.expander("📜 Termos e Condições de Uso"):
            st.markdown(textos.TERMOS)
        return st.checkbox("Li e concordo com os Termos e Condições de Uso do Aplicativo")


def bloco_demonstracao() -> None:
    with st.expander("**🎥🗃️🧏‍♂️ Demonstração do ADAM: Apresentação, Orientações e Considerações**"):
        st.markdown(textos.DEMONSTRACAO)
        # --- vídeo comentado até a versão 2.0 ---------------------------------------------
        # O link do YouTube sai do ar nesta versão e volta na 2.0 com o novo material.
        # st.markdown("*Obs.: O vídeo inicia automaticamente e com o volume zero (0).*")
        # st.video(textos.VIDEO_URL, start_time=0, autoplay=True, muted=True,
        #          end_time=30, loop=True, width=640)
        # ----------------------------------------------------------------------------------
        with st.expander("📥 *Planilhas de exemplo:*"):
            st.markdown(textos.PLANILHAS_EXEMPLO)
        with st.expander("**Sobre o ADAM: Contexto e apresentação**"):
            st.markdown(textos.SOBRE_ADAM)


def tempo_em_palavras(segundos: float) -> str:
    return ("%.2f s | %.2f min | %.2f h | %.2f dias"
            % (segundos, segundos / 60, segundos / 3600, segundos / 86400))


def calcular(df_processado: pd.DataFrame, data_atualizacao: date, aplica_juros: bool,
             tel: telemetria.Telemetria) -> None:
    data_str = data_atualizacao.strftime("%d/%m/%Y")
    tel.registrar("aceite_termos", "Usuário aceitou os Termos e Condições de Uso: True")
    tel.registrar("configuracao_atualizacao_data",
                  "Data de atualização selecionada: %s" % data_str)
    tel.registrar("configuracao_atualizacao_juros", "Aplicar juros: %s" % aplica_juros)
    tel.registrar("processamento_iniciado", "Início do processamento dos cálculos de "
                                            "atualização monetária e juros")

    barra = st.progress(0, text="Iniciando...")
    linha_status = st.empty()
    inicio = time.time()

    def progresso(atual: int, total: int) -> None:
        percentual = int(atual / total * 100) if total else 100
        decorrido = time.time() - inicio
        ritmo = atual / decorrido if decorrido > 0 else 0
        restante = (total - atual) / ritmo if ritmo > 0 else 0
        barra.progress(percentual, text="Processando: %d%%" % percentual)
        linha_status.text("%d/%d | %.2f ind/s | ETA: %.1fs" % (atual, total, ritmo, restante))

    try:
        with st.spinner("Enviando requisições para o Sistema de Débitos Web do TCU..."):
            st.markdown("""ℹ️ Atenção: Se o processamento parecer lento, o motivo pode ser devido à quantidade de indivíduos e/ou à velocidade resposta da API do TCU por payload (carga de conjunto de dados).<br>
                            Recomendamos aguardar até que a barra de progresso atinja 100% e o status indique conclusão, mesmo que o percentual pareça travado por um tempo.""",
                        unsafe_allow_html=True)
            df_resultado, df_log = core.calcular_por_devedor(
                df_processado, data_atualizacao=data_str, aplica_juros=aplica_juros,
                progress_callback=progresso, cfg=CFG)

        decorrido = time.time() - inicio
        barra.progress(100, text="Concluído!")
        linha_status.text("Processamento concluído! ✅")

        # Antes estes números estavam trocados: a "taxa de parcelas" contava
        # indivíduos e a linha seguinte invertia a razão
        individuos, lancamentos = len(df_resultado), len(df_log)
        st.text("Indivíduos processados: %d" % individuos)
        st.text("Lançamentos processados: %d" % lancamentos)
        if decorrido > 0:
            st.text("Ritmo: %.2f indivíduos/s | %.2f lançamentos/s | %.4f s por indivíduo"
                    % (individuos / decorrido, lancamentos / decorrido, decorrido / max(individuos, 1)))
        st.text("Tempo total: %s" % tempo_em_palavras(decorrido))

        tel.registrar("processamento_concluido_tempo",
                      "Tempo total: %.2f segundos." % decorrido)
        tel.registrar("processamento_concluido_qtde_individuos",
                      "Indivíduos processados: %d." % individuos)
        tel.registrar("processamento_concluido_taxa_parcelas",
                      "Taxa média de processamento de lançamentos por segundo: %.2f."
                      % (lancamentos / decorrido if decorrido > 0 else 0))

        st.session_state.df_resultado = df_resultado
        st.session_state.df_log = df_log
        st.session_state.calculo_realizado = True
        st.session_state.start_time = time.time()
        tel.registrar("processamento_concluido", "Fim do processamento dos cálculos de "
                                                 "atualização monetária e juros")

    except Exception as erro:
        st.error("Erro durante o processamento: %s" % erro)
        st.exception(erro)


def bloco_resultados(tel: telemetria.Telemetria) -> None:
    df_resultado = st.session_state.df_resultado
    df_log = st.session_state.df_log
    decorrido = time.time() - st.session_state.start_time

    st.success("Cálculo finalizado com sucesso!")
    st.text("Tempo total: %.2fs" % decorrido)
    st.text("Indivíduos: %d" % len(df_resultado))

    st.subheader("📊 Resultado por Indivíduo")
    st.dataframe(df_resultado)
    st.subheader("📋 Log detalhado")
    st.dataframe(df_log.head(20))

    marca = datetime.now(ZoneInfo(CFG.fuso)).strftime("%d-%m-%Y_%Hh%Mm%Ss")
    nome_resultado, nome_log, nome_zip = ("Resultado_%s.xlsx" % marca,
                                          "Log_%s.xlsx" % marca,
                                          "Relatorios_%s.zip" % marca)

    def excel_bytes(tabela: pd.DataFrame) -> bytes:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as escritor:
            tabela.to_excel(escritor, index=False)
        return buffer.getvalue()

    def zip_bytes() -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as arquivo:
            arquivo.writestr(nome_resultado, excel_bytes(df_resultado))
            arquivo.writestr(nome_log, excel_bytes(df_log))
        return buffer.getvalue()

    opcoes = {
        "ZIP (resultado + log)": ("zip", zip_bytes, nome_zip, "application/zip"),
        "Resultado Excel": ("resultado", lambda: excel_bytes(df_resultado), nome_resultado, MIME_XLSX),
        "Log Excel": ("log", lambda: excel_bytes(df_log), nome_log, MIME_XLSX),
    }

    st.subheader("📋 Download dos Relatórios")
    st.info(textos.DICA_DOWNLOAD)
    escolhido = st.selectbox("**Escolha o tipo de relatório**:", list(opcoes))

    if st.button("📌 Preparar download", key="preparar_download"):
        tipo, gerar, nome, mime = opcoes[escolhido]
        st.session_state.download_ready = {"data": gerar(), "file_name": nome,
                                           "mime": mime, "label": escolhido}
        if tel.registrar_agora("download_preparacao", "%s_selecionado" % tipo):
            pass

    if st.session_state.get("download_ready"):
        pronto = st.session_state.download_ready
        st.success("Pronto para baixar: %s" % pronto["label"])
        if st.download_button(label="⬇️ Baixar %s" % pronto["label"], data=pronto["data"],
                              file_name=pronto["file_name"], mime=pronto["mime"],
                              key="download_final"):
            tel.registrar_agora("download_concluido", "%s_baixado" % pronto["label"])
            del st.session_state.download_ready
            st.balloons()

    st.markdown(textos.AGRADECIMENTO, unsafe_allow_html=True)


def bloco_entrada() -> pd.DataFrame | None:
    """Upload, prévia e padronização. Devolve a tabela pronta ou nada."""
    enviado = st.file_uploader("📂 Carregar arquivo Excel (.xlsx)", type=["xlsx"])
    if enviado is None:
        if "upload_registrado" in st.session_state:
            del st.session_state.upload_registrado
        st.info("Aguardando o upload de um arquivo Excel...")
        return None

    tel = registrar()
    if "upload_registrado" not in st.session_state:
        tel.registrar("upload_arquivo", "arquivo carregado")
        st.session_state.upload_registrado = True

    try:
        bruto = planilha.ler_excel(enviado)
    except Exception as erro:
        st.error("Erro ao ler o arquivo: %s" % erro)
        st.stop()

    st.success("Arquivo carregado com sucesso!")
    st.subheader("Prévia dos dados originais")
    st.dataframe(bruto.head(10))

    data_no_nome = extrair_data_de_nome_de_arquivo(enviado.name)
    if data_no_nome:
        st.info("Data detectada no nome do arquivo: %s" % data_no_nome.strftime("%d/%m/%Y"))

    try:
        with st.spinner("Processando a base de dados..."):
            processado = planilha.preprocessar(bruto)
    except Exception as erro:
        st.error("Erro no pré-processamento: %s" % erro)
        st.stop()

    st.success("Pré-processamento concluído!")
    st.subheader("Dados após padronização")
    st.dataframe(processado.head(10))
    return processado


# ==================== PÁGINA ====================
st.set_page_config(page_title="ADAM  - Atualização de Valores", layout="wide")
st.title("💰📈 ADAM - Assistente De Atualização Monetária")

telemetria_da_pagina = registrar()
exigir_consentimento(telemetria_da_pagina)

# --- Estatísticas de uso: comentadas até a versão 2.0 --------------------------------
# Motivo: o painel depende de credencial de Google Sheets (gspread) que não existe no
# ambiente de deploy. Volta na 2.0 com a credencial própria e a planilha do painel.
#
# with st.expander("📊 **Estatísticas de uso do ADAM**"):
#     st.markdown("Dados coletados anonimamente para melhoria do serviço.")
#     try:
#         with st.spinner("🔄 Carregando estatísticas de uso..."):
#             painel.mostrar_painel(tabela_de_uso(), CFG)
#     except Exception as erro:
#         st.info("Não foi possível carregar as estatísticas agora: %s" % erro)
# -------------------------------------------------------------------------------------

bloco_demonstracao()

with st.expander("📧✅ ***Cadastro voluntário **(Opcional)** para o recebimento de "
                 "atualizações e novidades desse e de outros artefatos***:"):
    usuarios.formulario(abrir_aba=lambda: aba(CFG.planilha_cadastro), cfg=CFG)

st.markdown("---")
st.markdown("Envie uma planilha com os valores de débitos e de créditos e obtenha os "
            "valores atualizados monetariamente e com juros.")

aceite_termos = barra_lateral()
df_processado = bloco_entrada()

if df_processado is not None:
    st.subheader("📅 Data de referência para atualização")
    data_atualizacao = st.date_input("Data da atualização monetária e juros",
                                     value=date.today(), format="DD/MM/YYYY")
    aplica_juros = st.checkbox("Aplicar juros", value=True)

    if not aceite_termos:
        st.warning("⚠️ **Para habilitar o processamento dos cálculos é necessário fazer a "
                   "leitura dos Termos e Condições de Uso.**\n\nVerifique a barra de navegação "
                   "lateral e, após a leitura, marque a caixa de **leitura e concordância** "
                   "para iniciar os cálculos de atualização dos valores.")
    elif st.button("🚀 Calcular valores atualizados", type="primary", key="btn_calcular"):
        calcular(df_processado, data_atualizacao, aplica_juros, telemetria_da_pagina)

    if st.session_state.get("calculo_realizado"):
        bloco_resultados(telemetria_da_pagina)

st.markdown("---")
st.markdown(textos.CREDITOS, unsafe_allow_html=True)
st.markdown("---")
