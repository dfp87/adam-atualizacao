# ADAM — Assistente de Atualização Monetária

Aplicação Streamlit que calcula atualização monetária e juros de débitos e créditos públicos usando a
**API pública de Cálculo de Débito do TCU** como motor. O cálculo não é reimplementado aqui: o ADAM monta
o pedido, chama a API por devedor, valida os quatro saldos e entrega dois relatórios — resultado
consolidado e log detalhado de cada lançamento.

## Como usar

1. Leia e aceite o Aviso de Privacidade.
2. Envie uma planilha `.xlsx` com três colunas: `id`, `dataFato` (dd/mm/aaaa) e `Valor do Registro`
   (negativo = débito, positivo = crédito).
3. Confira a prévia, escolha a data de atualização e se aplica juros.
4. Marque a leitura dos Termos e clique em **Calcular valores atualizados**.
5. Baixe o resultado e o log.

## Estrutura

```
streamlit_app.py     ponto de entrada do Streamlit Cloud (ajusta o caminho e chama adam/app.py)
adam/                a aplicação: página, cliente da API, planilha, telemetria, cadastro, textos
nucleo/              núcleo comum (planilhas Google e conversão de texto), vendorizado para o deploy
assets/eu.jpg        foto do autor na barra lateral
requirements.txt     dependências
```

## Rodar localmente

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy

Streamlit Community Cloud, a partir deste repositório:
- **Main file path:** `streamlit_app.py`
- **Branch:** `main`

### O que está fora desta versão

- **Vídeo de demonstração** — o link do YouTube saiu do ar e volta na 2.0 (código comentado em
  `adam/app.py` e `adam/textos.py`).
- **Estatísticas de uso** — o painel depende de credencial de Google Sheets e volta na 2.0 (bloco
  comentado em `adam/app.py`).

## Onde este projeto vive

O **projeto canônico** do ADAM é o módulo dentro do **Atende Contábil**
(`app/adam.py`, em `atende.dfpcentral.com.br`). Este repositório é a **cópia de publicação** que roda no
Streamlit Community Cloud: mesma regra de cálculo, mesma API do TCU, com as duas seções desligadas nesta
versão (vídeo e painel de estatísticas).

Mudança de regra ou de cálculo entra primeiro no Atende e é replicada aqui — não o contrário.

## Créditos

Fonte: Webservice de Dados Abertos do TCU · Licença Open Database License (ODbL).
