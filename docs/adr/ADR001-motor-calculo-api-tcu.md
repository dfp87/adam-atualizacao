# ADR001 — O cálculo não é reimplementado: o motor é a API pública do TCU

## Data

> 17/11/2026

## Status

> Aceito

## Contexto

O ADAM atualiza monetariamente débitos e créditos públicos. A tentação natural, num artefato de
cálculo, é implementar a fórmula: juros, Selic, atualização, data de corte, compensações. Foi o que a
versão anterior fazia — e é o que qualquer planilha de trabalho faz. O problema não é o esforço: é que
duas implementações da mesma regra divergem, e a divergência aparece justamente no caso que ninguém
testou.

A Receita Federal, ao publicar a Calculadora de Tributos em 2026, tomou a decisão oposta para o seu
domínio: as fórmulas ficam em banco e o código executa expressões (ADR001 da própria RFB). Qualquer que
seja a estratégia, a pergunta de projeto é sempre a mesma: **onde mora a regra, e quem responde por ela**.

## Decisão

O ADAM **não calcula**. Ele monta o pedido, envia à **API pública de Cálculo de Débito do TCU**, um
pedido por devedor, valida os quatro saldos retornados, e entrega dois relatórios: o resultado
consolidado e o log detalhado de cada lançamento.

A regra de cálculo permanece onde é oficialmente mantida. O ADAM é o artefato que faz a ponte entre a
planilha do servidor e o motor oficial — com validação de entrada, conferência de saldos e registro do
que foi feito.

## Consequências

- **A favor:** não há segunda implementação da regra para divergir; a atualização da regra pelo TCU
  chega ao resultado sem alteração de código; o artefato pode ser auditado contra o motor oficial, não
  contra a minha interpretação dele.
- **Contra:** o ADAM depende de disponibilidade da API. Sem rede, não calcula — e isso é limitação
  declarada, não defeito oculto.
- **Contra:** a conferência passa a ser de *saldos*, não de fórmula: o artefato valida o que recebeu,
  não recria o cálculo para comparar.
- **Consequência de projeto:** como o cálculo não está aqui, a contribuição do artefato é a *cadeia de
  evidência* — entrada validada, parâmetros visíveis, resultado conferível e prova por execução (ADR002).
