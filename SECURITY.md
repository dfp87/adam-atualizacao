# Segurança do deploy — auditoria de 10/11/2026

Objetivo: publicar o ADAM no Streamlit Community Cloud **sem expor credencial, chave ou dado sensível**.

## Resultado da varredura

| Verificação | Resultado |
|---|---|
| Arquivo de credencial no pacote (`.streamlit/secrets.toml`, `.env`, `*.json` de service account, `*.pem`, `*.key`) | **nenhum** |
| Chave, token ou senha literal no código | **nenhum** |
| Credencial do Google | lida por `st.secrets["gcp_service_account"]`, `GOOGLE_SERVICE_ACCOUNT` (JSON) ou `GOOGLE_APPLICATION_CREDENTIALS` (caminho) — **nunca** embutida |
| Dependência que exigiria segredo para importar | nenhuma: `gspread` é importado dentro da função |
| Planilhas, CSVs, logs e ZIPs | fora do pacote e no `.gitignore` |

Como funciona a leitura da credencial (`nucleo/sheets.py`): o cliente Google é criado **na hora do uso**,
a partir de `st.secrets`, variável de ambiente ou caminho de arquivo. Sem credencial, `CredencialAusente`
é levantado e o chamador trata — telemetria e cadastro falham em silêncio, a página continua funcionando.

## Dados pessoais que aparecem no app (por decisão do autor)

- Nome e titulação na barra lateral
- E-mail institucional `ferreira.douglas@mail.uft.edu.br`
- Links de LinkedIn e Lattes
- Foto `assets/eu.jpg`

São identidade profissional pública, não dado de terceiro. **Nenhum** dado de usuário do app é gravado
sem credencial configurada.

## Telemetria e cadastro voluntário

- Só gravam em Google Sheets **quando existe credencial** (v2.0).
- Sem credencial — como nesta publicação — não gravam nada; o app não quebra.
- O Aviso de Privacidade consultado no primeiro acesso descreve a coleta da v2.0. Ao ligar a credencial,
  o texto já está correto; enquanto não houver credencial, não há coleta efetiva.

## Recomendações para o deploy

1. **Credencial do Google (v2.0) só nos Secrets do Streamlit Cloud** (App settings → Secrets), nunca no
   repositório. O arquivo `.streamlit/secrets.toml` está no `.gitignore`.
2. **Visibilidade do repositório**: público é o caminho mais simples para o Community Cloud; privado
   exige autorizar o acesso do Streamlit ao repositório. Em nenhum dos dois casos há segredo no código.
3. **Tokens do GitHub**: a conta `dfp87` tem escopo `repo`. Conceder apenas o repositório do ADAM ao
   Streamlit, não a organização inteira.
4. **LGPD**: ao ativar telemetria/geolocalização por IP (v2.0), registrar base legal e finalidade; hoje
   não há coleta.
