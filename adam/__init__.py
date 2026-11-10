"""ADAM — atualização monetária e juros de débitos e créditos públicos.

O cálculo não é feito aqui: ele é terceirizado para a API pública de Cálculo de
Débito do TCU, que aplica os critérios legais vigentes. Este pacote prepara a
planilha, monta o payload, chama a API e formata os relatórios.

Módulos:
- `config`     — parâmetros (URL da API, prazos, pausas, planilhas)
- `planilha`   — leitura e padronização da planilha de entrada
- `core`       — cliente da API do TCU e montagem dos resultados e do log
- `telemetria` — registro anônimo de uso (Google Sheets)
- `usuarios`   — cadastro voluntário
- `painel`     — painel de estatísticas de uso
- `textos`     — os textos institucionais e os termos, fora do código da página
- `app`        — a página Streamlit
"""

__all__ = ["config", "core", "painel", "planilha", "telemetria", "textos", "usuarios"]
