"""Testes das normalizações puras — o que erra em silêncio numa planilha.

Rodar: python3 -m unittest discover -s tests -v
"""
import sys
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo import texto  # noqa: E402


class TestSemAcentos(unittest.TestCase):
    def test_remove_acentos_e_cedilha(self):
        self.assertEqual(texto.sem_acentos("João Gonçalves Ação"), "Joao Goncalves Acao")

    def test_mantem_texto_sem_acento(self):
        self.assertEqual(texto.sem_acentos("MARIA SILVA"), "MARIA SILVA")


class TestChaveNome(unittest.TestCase):
    def test_maiuscula_sem_espaco_duplicado(self):
        self.assertEqual(texto.chave_nome("  João   da Silva "), "JOAO DA SILVA")

    def test_idempotente(self):
        uma = texto.chave_nome("José  Antônio")
        self.assertEqual(uma, texto.chave_nome(uma))


class TestNumeroProcesso(unittest.TestCase):
    def test_preserva_formato_sei(self):
        self.assertEqual(
            texto.normalizar_numero_processo("12345.678901/2026-11"),
            "12345.678901/2026-11",
        )

    def test_vazio_devolve_vazio(self):
        self.assertEqual(texto.normalizar_numero_processo(""), "")


class TestDataNoNomeDoArquivo(unittest.TestCase):
    def test_iso(self):
        self.assertEqual(
            texto.extrair_data_de_nome_de_arquivo("relatorio_2024-03-15.xlsx"),
            date(2024, 3, 15),
        )

    def test_brasileiro(self):
        self.assertEqual(
            texto.extrair_data_de_nome_de_arquivo("extrato 15-03-2024.csv"),
            date(2024, 3, 15),
        )

    def test_arquivo_sem_data(self):
        self.assertIsNone(texto.extrair_data_de_nome_de_arquivo("planilha_final.csv"))


class TestParaNumero(unittest.TestCase):
    def test_formato_brasileiro(self):
        self.assertEqual(texto.para_numero("1.234,56"), 1234.56)

    def test_formato_com_ponto_decimal(self):
        self.assertEqual(texto.para_numero("1234.56"), 1234.56)

    def test_vazio_devolve_zero(self):
        self.assertEqual(texto.para_numero(""), 0.0)

    def test_none_devolve_zero(self):
        self.assertEqual(texto.para_numero(None), 0.0)


if __name__ == "__main__":
    unittest.main()
