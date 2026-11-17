"""Testes da impressão digital incremental usada para saber se um arquivo mudou.

Atenção ao contrato real: `impressao_incremental` é **SHA-1 truncado em 16 caracteres**, e em arquivos
maiores que 2 MB lê apenas o começo e o fim. Ele serve para decidir "preciso reprocessar este
arquivo?" — não para provar autoria ou integridade. A prova de execução usa SHA-256 sobre a
string canônica do atestado (ADR002), que é outro mecanismo.

Rodar: python3 -m unittest discover -s tests -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo import incremental  # noqa: E402


class TestHashParcial(unittest.TestCase):
    def _arquivo(self, pasta, conteudo, nome="amostra.csv"):
        arquivo = Path(pasta) / nome
        arquivo.write_text(conteudo, encoding="utf-8")
        return arquivo

    def test_deterministico(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = self._arquivo(pasta, "id;valor\n1;10\n")
            self.assertEqual(
                incremental.impressao_incremental(arquivo),
                incremental.impressao_incremental(arquivo),
            )

    def test_formato_16_hex(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = self._arquivo(pasta, "id;valor\n1;10\n")
            resumo = incremental.impressao_incremental(arquivo)
            self.assertEqual(len(resumo), 16)
            int(resumo, 16)  # levanta se não for hexadecimal

    def test_conteudo_diferente_muda_o_hash(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = self._arquivo(pasta, "id;valor\n1;10\n", "a.csv")
            b = self._arquivo(pasta, "id;valor\n1;11\n", "b.csv")
            self.assertNotEqual(
                incremental.impressao_incremental(a),
                incremental.impressao_incremental(b),
            )

    def test_mesmo_conteudo_nomes_diferentes_mesmo_hash(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = self._arquivo(pasta, "id;valor\n1;10\n", "a.csv")
            b = self._arquivo(pasta, "id;valor\n1;10\n", "b.csv")
            self.assertEqual(
                incremental.impressao_incremental(a),
                incremental.impressao_incremental(b),
            )

    def test_arquivo_grande_le_apenas_comeco_e_fim(self):
        """Limite conhecido e documentado: diferença no meio de um arquivo grande não é detectada.

        Não é defeito — é o desenho de um índice incremental. Este teste existe para que ninguém
        use `impressao_incremental` como prova de integridade por engano.
        """
        with tempfile.TemporaryDirectory() as pasta:
            cabeca = "x" * (64 * 1024)
            cauda = "z" * (64 * 1024)
            meio_a = "A" * (3 * 1024 * 1024)
            meio_b = "B" * (3 * 1024 * 1024)
            a = self._arquivo(pasta, cabeca + meio_a + cauda, "a.txt")
            b = self._arquivo(pasta, cabeca + meio_b + cauda, "b.txt")
            self.assertEqual(
                incremental.impressao_incremental(a),
                incremental.impressao_incremental(b),
            )


if __name__ == "__main__":
    unittest.main()
