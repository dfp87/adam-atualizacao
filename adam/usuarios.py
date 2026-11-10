"""Cadastro voluntário (opcional) para avisos de novas versões.

Preserva o formulário e a ordem das colunas da planilha. O que muda é a
autenticação: era o terceiro bloco copiado da mesma abertura de planilha, agora
vem do núcleo.
"""
from __future__ import annotations

from datetime import datetime

from nucleo import sheets

from .config import Config

COLUNAS = ("timestamp", "email", "nome", "cargo", "cidade", "estado", "area", "setor",
           "receber_novidades")


def montar_linha(dados: dict, momento: datetime | None = None) -> list:
    return [
        (momento or datetime.now()).isoformat(),
        dados.get("email", ""),
        dados.get("nome", ""),
        dados.get("cargo", ""),
        dados.get("cidade", ""),
        dados.get("estado", ""),
        dados.get("area", ""),
        dados.get("setor", ""),
        dados.get("receber_novidades", False),
    ]


def salvar_cadastro(dados: dict, cfg: Config | None = None, abrir_aba=None) -> bool:
    """Grava o cadastro. Devolve se deu certo, sem esconder o erro do chamador."""
    cfg = cfg or Config()
    try:
        if abrir_aba is not None:
            abrir_aba().append_row(montar_linha(dados))
        else:
            sheets.acrescentar(cfg.planilha_cadastro, montar_linha(dados))
        return True
    except Exception as erro:
        print("[cadastro] falha ao salvar: %s" % erro)
        return False


def formulario(abrir_aba=None, cfg: Config | None = None) -> None:
    """Formulário da página. Marca a sessão quando o envio dá certo."""
    import streamlit as st

    cfg = cfg or Config()
    if "formulario_enviado" not in st.session_state:
        st.session_state.formulario_enviado = False

    if st.session_state.formulario_enviado:
        st.success("👍 Você já enviou seus dados. Obrigado!")
        return

    with st.expander("📧 Receba novidades e atualizações do ADAM (opcional)"):
        st.markdown("Preencha os dados abaixo para receber informações sobre novas versões, "
                    "dicas e pesquisas.")
        with st.form("form_cadastro"):
            email = st.text_input("E-mail *", placeholder="seu@email.com")
            nome = st.text_input("Nome completo", placeholder="Ex: João da Silva")
            cargo = st.text_input("Cargo/Função", placeholder="Ex: Analista de Controle")
            cidade = st.text_input("Cidade", placeholder="Ex: Brasília")
            estado = st.text_input("Estado (UF)", placeholder="Ex: DF")
            area = st.text_input("Área de atuação", placeholder="Ex: Controle Externo")
            setor = st.text_input("Setor/Departamento", placeholder="Ex: Auditoria")
            receber = st.checkbox("Quero receber novidades por e-mail", value=True)
            enviado = st.form_submit_button("✉️ Enviar (não obrigatório)")

            if enviado:
                if not email:
                    st.warning("Por favor, informe seu e-mail para receber novidades "
                               "(ou deixe em branco se não quiser).")
                elif salvar_cadastro({"email": email, "nome": nome, "cargo": cargo,
                                      "cidade": cidade, "estado": estado, "area": area,
                                      "setor": setor, "receber_novidades": receber},
                                     cfg=cfg, abrir_aba=abrir_aba):
                    st.success("✅ Cadastro realizado! Agradecemos seu interesse.")
                    st.session_state.formulario_enviado = True
                    st.rerun()
                else:
                    st.error("Não foi possível salvar. Tente novamente mais tarde.")
