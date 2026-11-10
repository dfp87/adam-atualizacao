"""Textos institucionais do ADAM, fora do código da página.

Motivo de existir: eram 200 linhas de markdown no meio do `app.py`, misturadas
com a lógica. Aqui ficam separados — e é aqui que se corrige uma frase sem
risco de mexer no fluxo.

⚠️ PENDÊNCIA: o aviso de privacidade aponta para `[Política de Privacidade](LINK_AQUI)`
em produção desde o início. Enquanto não houver uma página publicada, o link
não leva a lugar nenhum — decidir entre publicar um texto próprio ou retirar a
promessa de link.
"""

AVISO_PRIVACIDADE = """
Este aplicativo coleta **dados de navegação e utilização** 
para fins de análise de uso e a melhoria do serviço.

Os dados coletados são tratados de forma anônima e agregada,
sem nenhuma identificação pessoal e/ou sem qualquer informação 
que possa levar à identificação do(a) usuário(a).

Tais parâmetros incluem:                    
            1️⃣. Data e hora de acesso.                    
            2️⃣. Tipo de evento (ex: carregamento, download etc).                     
            3️⃣. Detalhes do evento.                     
            4️⃣. Geolocalização por: Continente, País, Estado, Cidade e Bairro (esse último se disponível).                     
            5️⃣. Tipo do navegador para fins de análise sobre compatibilidade.                     

Ao clicar em "Eu li e concordo com a Política de Privacidade", 
você estará declarando que concorda com nossa **[Política de Privacidade](LINK_AQUI)**.
"""

DEMONSTRACAO = """
A seguir, apresentamos uma demonstração do ADAM em funcionamento, utilizando uma planilha de exemplo com dados fictícios. 
O vídeo mostra o processo completo, desde o upload da planilha, passando pelo pré-processamento dos dados, 
a configuração da data de atualização e aplicação de juros, até a geração dos relatórios de resultado e log detalhado.

Esta demonstração tem como objetivo ilustrar a facilidade de uso do ADAM e a eficiência na realização dos cálculos de atualização monetária e juros, 
utilizando os parâmetros oficiais do Tribunal de Contas da União (TCU).
"""

# --- Link do vídeo: fora do ar até a versão 2.0 -----------------------------------------
# A demonstração em vídeo volta na 2.0 com o novo material; até lá o bloco de demonstração
# mostra apenas o texto e as planilhas de exemplo.
# VIDEO_URL = "https://www.youtube.com/watch?v=IVugCjwIqKw&list=RDIVugCjwIqKw&start_radio=1"
# -----------------------------------------------------------------------------------------

PLANILHAS_EXEMPLO = """
Caso não tenha uma planilha pronta, use nosso modelo:

[🔗 Baixar planilha de exemplo (XLSX)](https://docs.google.com/spreadsheets/d/19PaFbsBPhQkHkR1SqOBcEuSHdPfEHjpB_RCtt-a7nfM/edit?usp=sharing)
ou
[🔗 Baixar planilha de exemplo - origem TG (XLSX)](https://docs.google.com/spreadsheets/d/1DO0Wc4o8YW0Mum-M8AbFKHeJKUpf-G-4A-DdQSqzuh0/edit?usp=sharing)

*Ambas as planilhas contêm dados fictícios para teste.*
"""

SOBRE_ADAM = """
O ADAM é uma ferramenta web gratuita que automatiza o cálculo da atualização 
monetária e dos juros de débitos e créditos públicos, utilizando os mesmos 
parâmetros e a mesma base de dados oficiais do Tribunal de Contas da União (TCU). 

Desenvolvido como parte de uma pesquisa de Doutorado no âmbito do Programa de 
Pós‑Graduação em Governança e Transformação Digital (PPGGTD/UFT), o aplicativo 
elimina erros manuais de cálculos, reduz drasticamente o tempo de processamento e 
garante total rastreabilidade por meio de logs detalhados.

______________________________

**Como funciona:**
Você envia uma planilha Excel (modelo disponível) com os lançamentos por id 
(identificador, data do fato, valor positivo para débito ou negativo para crédito). 

O ADAM pré‑processa os dados, consulta em tempo real a API de cálculos do TCU 
(que aplica os critérios legais vigentes) e gera dois relatórios**¹**:

1️⃣. Resultado consolidado por id (valores corrigidos, juros, total)

2️⃣. Log detalhado de cada lançamento (payload, resposta da API, timestamps)

*Obs**¹**.: Ao final do processamento existe a possibilidade de realizar o download de ambos os relatórios zipados.*

______________________________

**Diferenciais validados por pesquisa científica com o artigo submetido, aceito, apresentado e publicado nos Anais no Encontro de Administração da Tecnologia da Informação (EnATI) de 2026.**

**O *EnATI* é um evento divisional promovido pela Associação Nacional de Pós-Graduação e Pesquisa em Administração (ANPAD).**
Trata-se de um dos eventos científicos mais importantes e renomados nas áreas de Administração, Contabilidade e Gestão no Brasil.

Durante o desenvolvimento deste Produto Técnico-Tecnológico (PTT), foram verificados os parâmetros de:

Acurácia, Eficiência e Avaliação de Usabilidade (esse último por meio do *System Usability Scale*).            

Onde:            

🎯Acurácia = Obteve 100% em comparação com os resultados testados diretamente no sistema oficial do TCU.

⏳Eficiência**²** = Redução de 99,5% no tempo de cálculo (de 247 segundos para 1,24 segundos)

*Obs**²**.: Foram realizados testes estatísticos: Teste t, Teste W (Wilcoxon) e Teste de Cohen'd.*
Todos os resultados foram estatisticamente significativos (p < 0.0001) nas comparações de tempo gastos para realização dos cálculos e, o Teste de Cohen's d apresentou valores acima de 1,18 que se traduziu na eliminação do Erro Tipo II em 100%, ou seja, o risco de ter falhado em um testes estatísticos sobre as diferenças de tempo entre as metodologias de cálculos que foram comparadas foi 0,00%.

🖥️ Usabilidade = Excelente (94,5 pontos no SUS antes do desenvolvimento dessa interface).

______________________________

**Destaques:**

1️⃣. Automatização total dos cálculos de atualização monetária e juros, eliminando erros manuais.

2️⃣. Processamento em lote por id, com consultas em tempo real à API do TCU, garantindo precisão e conformidade com os parâmetros oficiais.

3️⃣. Geração de relatórios detalhados, incluindo um log completo de cada lançamento, payload enviado e resposta da API, com timestamps para rastreabilidade total.

______________________________

**Finalidades:**

1️⃣. Facilitar a vida de servidores públicos, gestores, pesquisadores e cidadãos que precisam realizar cálculos de atualização monetária e juros com base nos parâmetros oficiais do TCU.

As unidades podem utilizar o ADAM, para:
            
    1️⃣. 1️⃣. Para atualização de débitos e créditos em processos administrativos (internos ou externos);
    1️⃣. 2️⃣. Para auditorias e fiscalização de contas públicas, garantindo a precisão dos cálculos e a conformidade com os parâmetros oficiais do TCU;
    1️⃣. 3️⃣. Para pesquisas acadêmicas e entre outros.

Obs.: O ADAM é uma ferramenta de uso geral, ou seja, pode ser utilizado para qualquer tipo de débito 
ou crédito público, desde que os dados estejam organizados no formato esperado (id, data do fato e valor do registro).
O aplicativo não é específico para um tipo de débito ou crédito, mas sim uma solução genérica para cálculos de atualização monetária e juros com base nos parâmetros oficiais do TCU.

    Tribunais Eleitorais, Ministérios Públicos, Tribunais de Contas Estaduais, Prefeituras, 
    Governos Estaduais, Universidades Públicas, Institutos Federais, entre outros órgãos 
    públicos e pesquisadores acadêmicos podem se beneficiar do ADAM para realizar cálculos 
    de atualização monetária e juros de forma rápida, precisa e confiável.
            
2️⃣. Contribuir para a transparência e eficiência na gestão pública, ao fornecer uma ferramenta acessível e confiável para cálculos complexos.
            
3️⃣. Servir como base para futuras pesquisas acadêmicas e desenvolvimento de soluções tecnológicas na área de gestão pública e finanças públicas.

______________________________

**Créditos e licenças:**

Os índices de correção e juros são fornecidos pelo Webservice de Dados Abertos do Tribunal 
de Contas da União (TCU), em referência a API de Cálculo de Débito.

Os dados são licenciados sob ODbL e os créditos sobre a API devem ser atribuídos ao TCU.

Os créditos sobre este aplicativo (código e estrutura) devem ser atribuídos ao desenvolvedor.

O código fonte do ADAM é de uso pessoal e acadêmico, não é comercial – consulte os Termos e Condições de Uso na barra lateral.
"""

INSTRUCOES_PLANILHA = """
**Formato esperado da planilha (Excel):**

- Coluna `id` (identificador do indivíduo, aceita: idDevedor', 'idIndividuo', 'idTCE', 'idGenerico' ou'id')
- Coluna `dataFato` (data do débito, formato dd/mm/aaaa)
- Coluna `Valor do Registro` (valor numérico, podendo ser positivo ou negativo - negativo é valor devido 'débito' e positivo é valor pago ou descontado 'crédito')
                            Aceita como rótulo: 'Valor do Registro', 'valorOriginal', 'Valor', 'valor' ou 'VALOR'.

**Exemplo:**

| id        | dataFato   | Valor do Registro |
|-----------|------------|-------------------|
| 123       | 15/03/2023 | 1000,50           |
| 123       | 20/05/2023 | -200,00           |
"""

TERMOS = """
### Termos de Uso do Aplicativo

**1. Aceitação**  
Ao utilizar este aplicativo, você concorda com estes Termos de Uso e com a Política de Privacidade.

**2. Finalidade**  
O aplicativo foi desenvolvido para fins educacionais e de pesquisa, realizando cálculos de atualização monetária e juros com base em dados fornecidos pelo Webservice do Tribunal de Contas da União (TCU).

**3. Direitos de Propriedade Intelectual**  
- O código-fonte, layout e elementos gráficos pertencem ao desenvolvedor (Lei 9.610/98).  
- Os dados obtidos via API são do Tribunal de Contas da União (TCU) e regidos pela licença ODbL.

**4. Uso permitido e proibido**  
- ✅ Permitido uso pessoal, acadêmico e não comercial.  
- ❌ Proibido uso comercial sem autorização expressa do TCU e do desenvolvedor.  
- ❌ Proibido inserir conteúdos maliciosos ou sobrecarregar a infraestrutura.

**5. Responsabilidade**  
O aplicativo é fornecido "no estado em que se encontra".
O desenvolvedor não se responsabiliza por danos decorrentes do uso das informações geradas.

**6. Modificações**  
Estes Termos podem ser alterados a qualquer momento; o uso continuado implica aceitação da nova versão.

**7. Legislação**  
Regido pela legislação brasileira (Código Civil, e LGPD).

**8. Contato**  
Para dúvidas: [ferreira.douglas@mail.uft.edu.br](mailto:ferreira.douglas@mail.uft.edu.br)

---

### Condições de Uso do Aplicativo

Os dados obtidos via Webservice do TCU estão sujeitos às seguintes condições:

1. **Proibição de uso comercial** – Vedada a utilização para fins comerciais, salvo autorização expressa do TCU.
2. **Obrigação de atribuição** – Toda republicação deve citar **fonte (TCU)**, **título** e **autor (Tribunal de Contas da União)**.
3. **Isenção de responsabilidade do TCU** – O TCU não se responsabiliza por danos decorrentes do uso dos dados.
4. **Isenção de responsabilidade do desenvolvedor** – O desenvolvedor não se responsabiliza por danos decorrentes do uso dos dados.
5. **Licença aberta** – Dados sob **Open Database License (ODbL)**.

Para mais detalhes: [Termos de Uso do Portal TCU](https://portaldatransparencia.gov.br/termos-de-uso)
"""

DICA_DOWNLOAD = """
**Dica**:

Use a caixa de seleção para obter as versões dos arquivos:                   
            - ZIP (resultado + log)                   
            - Resultado do cálculo (Excel)                   
            - Log detalhado (Excel)

Se preferir, pode baixar os arquivos individualmente também.                   

Após selecionar o tipo de relatório e clicar em "Preparar download", 
o botão de download final será habilitado para que você possa baixar 
o arquivo gerado.
"""

AGRADECIMENTO = """ℹ️ **O processamento da atualização monetária e juros acabou**.<br>
               🤝 **Obrigado pela preferência!**"""

CREDITOS = """
**Créditos:**  
*Fonte: Webservice de Dados Abertos do Tribunal de Contas União (TCU) - [https://sites.tcu.gov.br/dados-abertos/webservices-tcu/](https://sites.tcu.gov.br/dados-abertos/webservices-tcu/)*  
*Título: Cálculo de débito via Application Programming Interface (API) do Webservices do TCU*  
*Autor da API utilizada como motor dos cálculos deste App: Tribunal de Contas da União (TCU)*  
*Licença: Open Database License (ODbL) – [https://opendatacommons.org/licenses/odbl/](https://opendatacommons.org/licenses/odbl/)*  
*Termos de uso originais: [https://portaldatransparencia.gov.br/termos-de-uso](https://portaldatransparencia.gov.br/termos-de-uso)*
"""
