# ADR002 — A prova é da execução, não do código: atestado verificável por hash

## Data

> 17/11/2026

## Status

> Aceito

## Contexto

Publicar o código-fonte é uma forma de transparência — a que a Receita Federal adotou em 2026 ao abrir
a Calculadora de Tributos sob licença MIT, com os hashes das versões iniciais registrados em portaria.
Ela responde à pergunta "como a regra é aplicada?".

Mas há uma segunda pergunta, que o código aberto não responde: **"este resultado específico saiu deste
sistema, com esta entrada, nesta data?"** Num cálculo que gera crédito e débito contra terceiros, é
essa a pergunta que o jurisdicionado, o controle interno e o tribunal fazem.

Log de execução não resolve: log é texto que o próprio sistema escreve, sem âncora externa, e pode ser
editado ou reescrito sem deixar rastro. Arquivo em pasta compartilhada também não: não há como provar
que o arquivo conferido é o que gerou o número.

## Decisão

Cada cálculo emite um **atestado** contendo um resumo SHA-256 de uma string canônica com:

- identificação do artefato e do token da execução
- pessoa e e-mail do operador
- instante da execução (**UTC**, imutável)
- arquivo de entrada e hashes das planilhas processadas
- número de devedores e de linhas
- total apurado, com duas casas decimais
- a **chave do acórdão** de origem (v2) — o vínculo entre o cálculo e o processo que o motivou

O atestado é verificável em rota pública (`/verificar/<hash>`): qualquer pessoa recalcula o resumo a
partir dos dados declarados e confere se o resultado corresponde. O hash guarda UTC; a tela exibe em
horário de Brasília — a prova é imutável, a leitura é local.

O módulo que implementa essa lógica é `app/atestado.py` do projeto canônico (Atende Contábil), com
testes próprios; esta cópia pública documenta o desenho e demonstra o cálculo.

## Consequências

- **A favor:** a prova não depende de confiar no operador nem no servidor — depende de recálculo. E,
  ao incluir a chave do acórdão, o selo passa a provar *origem*, não apenas resultado.
- **A favor:** o atestado não carrega dado pessoal além do necessário; o que circula é o hash.
- **Contra:** o atestado prova que *este* resultado saiu deste sistema; não prova que o cálculo está
  certo. Correção é outro eixo — medido por acurácia contra o sistema oficial (ver o artigo do ADAM).
- **Consequência de projeto:** quem muda a string canônica muda todos os hashes. A string é, por isso,
  versionada — e a versão entra no próprio material do hash.
