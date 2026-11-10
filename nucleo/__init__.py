"""Núcleo comum dos projetos — o que era copiado de um projeto para o outro.

Cada módulo existe porque o mesmo código (ou quase) aparecia em mais de um
projeto, e cada correção precisava ser feita em todos:

- `log`         — configuração de log (estava em 3 projetos, sem idempotência)
- `texto`       — normalização de nome, número de processo e data (duplicada)
- `excel`       — escrita de planilha com ajuste de coluna (18 cópias em 1 projeto)
- `tabelas`     — leitura de CSV tolerante a encoding e separador (2 projetos)
- `incremental` — controle do que já foi processado por hash (2 projetos)
- `sheets`      — acesso a Google Sheets a partir de credencial fora do código
- `config`      — parâmetros por linha de comando e ambiente (4 projetos)

Regra de convivência: o núcleo não depende de nenhum projeto. Os projetos
dependem dele.
"""

__all__ = ["config", "excel", "incremental", "log", "sheets", "tabelas", "texto"]
