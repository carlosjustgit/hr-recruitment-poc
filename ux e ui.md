# ux e ui

— demo em streamlit

## princípios

- fricção mínima: um clique para actualizar dados, um para reindexar, um para pesquisar.
- clareza e honestidade: banner de poc e fonte dos dados sempre visíveis.
- rastreabilidade: cada resultado tem ligações à sheet e ao perfil.

## personas e tarefas

- recrutador: actualizar dados e fazer perguntas.
- responsável: verificar que há fontes, ver contagens e latências.
- operador da demo: mostrar remoção e auditoria.

## fluxo do utilizador

1. abre a app; lê o banner “prova de conceito”.
2. clica “actualizar dados”; vê estado do job e contagens.
3. clica “reindexar”.
4. coloca a pergunta; recebe lista de 3 a 5 candidatos com justificações e fontes.
5. se necessário, remove um registo e confirma que desaparece dos resultados.

## layout

barra lateral

- secção “dados”
    - botão “actualizar dados”
    - estado do job e progresso
    - contagens: linhas novas, removidas, totais
- secção “índice”
    - botão “reindexar”
    - top-k selector
- secção “métricas”
    - latência média, tamanho do índice
- secção “admin”
    - input `linkedin_url` para remover
    - botão “remover registo”
    - link para a worksheet “candidatos”

área principal

- cabeçalho com título e badge “poc”
- alerta de privacidade com resumo do propósito da demo
- campo de pergunta
- resultados em cartões:
    - nome e headline
    - porque foi seleccionado, com 1 a 2 frases
    - etiquetas de skills
    - links: “ver na sheet”, “ver no linkedin”
- rodapé com log resumido da sessão

## estados e erros

- estado “a actualizar” com spinner e timeout com opção de tentar de novo.
- erros de phantom com mensagem e sugestão de reduzir limite.
- erros de sheet com pedido para verificar permissões da service account.
- erro de índice esvaziado com chamada a “reindexar”.

## microcopy

- banner: “esta é uma prova de conceito para mostrar a experiência do utilizador. em produção, as fontes de dados serão oficiais e consentidas.”
- botão actualizar: “actualizar dados”
- métricas: “tempo de execução”, “linhas novas”, “duplicados removidos”
- ajuda na pergunta: “exemplos: quem tem mestrado em finanças, quem trabalhou com análise de risco”

## acessibilidade

- contraste suficiente, tamanhos de letra base 16 px
- botões com rótulos textuais, não apenas ícones
- foco visível ao navegar por teclado

## telemetria da demo

- `audit_log` na worksheet “auditoria” com acções: update, reindex, search, delete
- não registar texto integral das perguntas, apenas temas agregados para a sessão

## teste rápido de usabilidade

- cenário 1: actualizar dados, reindexar, pesquisar “mestrado em finanças”, verificar fontes
- cenário 2: remover registo e pesquisar de novo
- sucesso se cada cenário demorar menos de 2 minutos e sem mensagens de erro bloqueantes