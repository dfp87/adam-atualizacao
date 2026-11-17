# ADR003 — Núcleo separado da interface: a regra testável não mora no Streamlit

## Data

> 17/11/2026

## Status

> Aceito

## Contexto

O ADAM nasceu dentro de um `app.py` de Streamlit — como quase todo artefato de servidor que começa como
prova de conceito. Nessa forma, a normalização de texto, a leitura de planilha e a regra de negócio
ficam no mesmo arquivo em que se desenha o botão. Três consequências ruins aparecem depois:

1. **teste exige interface** — para conferir `para_numero("1.234,56")`, seria preciso subir o app;
2. **troca de interface obriga a mexer no cálculo** — e é aí que se introduz erro sem perceber;
3. **reuso vira cópia** — a mesma normalização apareceu no GSISTE e no ColetorSEI, com duas versões
   diferentes, e uma delas quebrava com célula vazia.

## Decisão

Separar em duas camadas, com dependência numa direção só:

- **`nucleo/`** — funções puras de texto, número, data, tabela e impressão digital. Só biblioteca
  padrão no caminho crítico (o que exige `pandas` está isolado em leitura/gravação de tabela), sem
  Streamlit, sem sessão, sem estado global.
- **`adam/` + `streamlit_app.py`** — a interface: formulário, prévia, escolha de data, botões, download.

A interface pode mudar de tecnologia sem tocar no núcleo. O núcleo pode ser chamado por script, por
teste ou por outro app.

## Consequências

- **A favor:** os testes rodam sem interface (`python3 -m unittest discover tests`), em segundos, e
  cobrem exatamente o que erra em silêncio — acento, separador, formato de número, data no nome do
  arquivo, determinismo do hash.
- **A favor:** o mesmo núcleo serve ao ADAM no Streamlit e ao ADAM embutido no Atende Contábil, o que
  evita a divergência entre duas cópias do mesmo cálculo.
- **Contra:** mais arquivos e um `sys.path` a resolver; em troca, o custo de testar cai a quase zero.
- **Limite declarado:** o núcleo é puro, mas não é completo — a chamada à API do TCU e a emissão do
  atestado vivem fora dele, porque dependem de rede e de banco.
