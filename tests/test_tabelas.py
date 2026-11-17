"""Testes de detecção e leitura de tabela.

Os testes que dependem de `pandas` são pulados quando a biblioteca não está no interpretador —
assim a suíte roda em qualquer máquina, sem instalar nada.

Rodar: python3 -m unittest discover -s tests -v
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo import tabelas  # noqa: E402

TEM_PANDAS = importlib.util.find_spec("pandas") is not None


class TestDeteccao(unittest.TestCase):
    def test_separador_ponto_e_virgula(self):
        self.assertEqual(tabelas.detectar_separador("a;b;c\n1;2;3"), ";")

    def test_separador_virgula(self):
        self.assertEqual(tabelas.detectar_separador("a,b\n1,2"), ",")

    def test_encoding_de_arquivo_utf8(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "amostra.csv"
            arquivo.write_text("nome;valor\nJoão;1\n", encoding="utf-8")
            codificacao = tabelas.detectar_encoding(arquivo)
            self.assertIn(codificacao, tabelas.ENCODINGS)


@unittest.skipUnless(TEM_PANDAS, "pandas não está neste interpretador")
class TestLeituraComPandas(unittest.TestCase):
    def test_le_csv_detecta_separador_e_encoding(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "dados.csv"
            arquivo.write_text("id;valor\n1;10,50\n", encoding="utf-8-sig")
            dados = tabelas.ler_csv(arquivo)
            self.assertEqual(list(dados.columns), ["id", "valor"])
            self.assertEqual(len(dados), 1)

    def test_renomeia_colunas_por_posicao(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "sem_cabecalho.csv"
            arquivo.write_text("1;10,50\n", encoding="utf-8-sig")
            dados = tabelas.ler_csv(arquivo, colunas=["id", "valor"])
            self.assertEqual(list(dados.columns), ["id", "valor"])


if __name__ == "__main__":
    unittest.main()
