"""Normalização de texto e números: o que mais se repetia entre os projetos.

- acentos e nomes, para chave de junção entre bases (GSISTE, ADAM)
- número de processo no formato SEI (ColetorSEI — estava duplicado, e as duas
  cópias não eram iguais: uma quebrava com célula vazia)
- valor monetário em formato brasileiro (ADAM e GSISTE tinham cada um o seu)
- data a partir do nome do arquivo (no ADAM a função existia, mas era `pass`:
  devolvia vazio e o app anunciava ao usuário que havia detectado a data)
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime

__all__ = ["sem_acentos", "chave_nome", "normalizar_numero_processo",
           "extrair_data_de_nome_de_arquivo", "para_numero", "nome_servidor",
           "nome_servidor_sem_pontuacao"]

# meses em português, para nomes de arquivo como "relatorio-jan-2026.pdf"
MESES = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
         "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}


def sem_acentos(texto) -> str:
    """Remove acentos preservando as letras (Á -> A, ç -> c)."""
    if texto is None:
        return ""
    decomposto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def chave_nome(nome) -> str:
    """Chave de junção entre bases: maiúsculas, sem acento, espaços colapsados."""
    limpo = sem_acentos(nome).upper()
    limpo = re.sub(r"[^A-Z0-9 ]+", " ", limpo)
    return re.sub(r"\s+", " ", limpo).strip()


def normalizar_numero_processo(valor) -> str:
    """Número de processo no formato SEI: XXXXX.XXXXXX/XXXX-XX.

    Aceita string, número ou vazio. Se não houver exatamente 17 dígitos,
    devolve o texto apenas aparado — nunca estoura.
    """
    if _vazio(valor):
        return ""
    texto = str(valor).strip()
    digitos = re.sub(r"\D", "", texto)
    if len(digitos) == 17:
        return "%s.%s/%s-%s" % (digitos[:5], digitos[5:11], digitos[11:15], digitos[15:])
    return texto


def extrair_data_de_nome_de_arquivo(nome_arquivo) -> date | None:
    """Procura uma data no nome do arquivo. Devolve `date` ou None.

    Reconhece: 2026-09-27, 27-09-2026, 27_09_2026, 27.09.2026, 20260927 e
    nomes com mês abreviado (relatorio-jan-2026, jan2026).
    """
    if not nome_arquivo:
        return None
    texto = sem_acentos(nome_arquivo).lower()

    for padrao, ordem in (
        (r"(?<!\d)(20\d{2})[-_.](\d{1,2})[-_.](\d{1,2})(?!\d)", "amd"),
        (r"(?<!\d)(\d{1,2})[-_.](\d{1,2})[-_.](20\d{2})(?!\d)", "dma"),
        (r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)", "amd"),
    ):
        achado = re.search(padrao, texto)
        if achado:
            try:
                if ordem == "amd":
                    return date(int(achado.group(1)), int(achado.group(2)), int(achado.group(3)))
                return date(int(achado.group(3)), int(achado.group(2)), int(achado.group(1)))
            except ValueError:
                continue

    achado = re.search(r"(?<![a-z])([a-z]{3})[-_. ]?(20\d{2})(?![a-z0-9])", texto)
    if achado and achado.group(1) in MESES:
        return date(int(achado.group(2)), MESES[achado.group(1)], 1)
    achado = re.search(r"(?<![a-z0-9])(20\d{2})[-_. ]?([a-z]{3})(?![a-z])", texto)
    if achado and achado.group(2) in MESES:
        return date(int(achado.group(1)), MESES[achado.group(2)], 1)

    achado = re.search(r"(?<![a-z])(janeiro|fevereiro|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)[-_. ]?(20\d{2})(?![0-9])", texto)
    if achado:
        numero = list(MESES.values())[list(["janeiro", "fevereiro", "marco", "abril", "maio", "junho",
                                            "julho", "agosto", "setembro", "outubro", "novembro",
                                            "dezembro"]).index(achado.group(1))]
        return date(int(achado.group(2)), numero, 1)
    return None


def nome_servidor(valor) -> str:
    """Nome de servidor como chave de junção entre bases: sem acento, maiúsculo.

    Era o `remover_acentos(texto) + .upper().strip()` copiado em dois arquivos do
    GSISTE (`juntar_bases2.py` e `processar_base.py`).
    """
    if _vazio_estrito(valor):
        return ""
    return sem_acentos(valor).upper().strip()


def nome_servidor_sem_pontuacao(valor) -> str:
    """Nome de servidor limpo para exibição/agrupamento: mantém acento, tira pontuação.

    Era o `limpar_nome()` do `gerar_base_servidores_unicos.py`: espaços colapsados,
    só letras/espaço/hífen/ponto, e maiúsculas no fim — mas **preservando** o
    acento, que é justamente o que diferencia esta versão da chave de junção.
    """
    if _vazio_estrito(valor):
        return ""
    texto = " ".join(str(valor).strip().split())
    texto = re.sub(r"[^a-zA-ZÀ-ÿ\s\-\.]", "", texto)
    return " ".join(texto.split()).upper()


def _vazio_estrito(valor) -> bool:
    """Vazio para `nome_servidor`: None e NaN contam; a string 'nan' NÃO.

    A diferença é de propósito: as chamadas do GSISTE fazem `.astype(str)` antes
    de padronizar, e lá o `pd.isna()` da cópia antiga recebia a **string** 'nan'
    (não um NaN), devolvendo 'nan' — trocar isso mudaria a base gerada.
    """
    if valor is None:
        return True
    if isinstance(valor, float) and valor != valor:      # NaN
        return True
    return False


def para_numero(valor, nulo=0.0) -> float:
    """Converte valor monetário em texto para float.

    Entende o formato brasileiro ("1.847,00") e o internacional ("1,847.00").
    Devolve `nulo` para vazio, traço, "N/A" e afins.
    """
    if _vazio(valor):
        return nulo
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = re.sub(r"[^\d,.\-]", "", str(valor)).strip()
    if not texto or texto in {"-", ".", ","}:
        return nulo
    ultima_virgula = texto.rfind(",")
    ultimo_ponto = texto.rfind(".")
    if ultima_virgula > ultimo_ponto:                 # 1.847,00
        texto = texto.replace(".", "").replace(",", ".")
    elif ultimo_ponto > ultima_virgula:               # 1,847.00
        texto = texto.replace(",", "")
    try:
        return float(texto)
    except ValueError:
        return nulo


def _vazio(valor) -> bool:
    if valor is None:
        return True
    if isinstance(valor, float) and valor != valor:    # NaN
        return True
    texto = str(valor).strip().lower()
    return texto in {"", "nan", "none", "null", "-", "n/a", "na", "nat"}
