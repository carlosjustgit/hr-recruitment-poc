# fluxo de dados

1. utilizador clica “actualizar dados”.
2. streamlit chama endpoint phantom, guarda `job_id`, faz poll até `succeeded`.
3. resultados aparecem na worksheet “candidatos”.
4. streamlit lê a sheet, normaliza e deduplica por `linkedin_url`.
5. embeddings gerados e índice criado em memória.
6. perguntas do utilizador são convertidas em query semântica e top-k é calculado.
7. resposta inclui candidatos, razões e ligações para a sheet e para o perfil.
8. acções de remoção escrevem na sheet e reconstroem o índice.

## desenho dos módulos

- `phantom_client.py`
    - `launch_search(query, limit) -> job_id`
    - `poll_status(job_id) -> status`
- `sheets_client.py`
    - `read_rows(range) -> list[dict]`
    - `write_rows(range, rows)`
    - `delete_by_url(url) -> bool`
- `normalizer.py`
    - `clean(rows) -> rows`
    - `dedupe(rows, key='linkedin_url') -> rows`
    - `tag_skills(rows) -> rows`
    - `summarise(rows) -> rows`
- `indexer.py`
    - `build(rows) -> index`
    - `search(index, query, k=5) -> hits`
- `qa.py`
    - `compose_answer(hits, question) -> str, justifications, sources`
- `audit.py`
    - `log(action, details) -> None`

## segurança

- todas as chaves em variáveis de ambiente.
- service account do google com acesso apenas à sheet alvo.
- sem escrita de dados sensíveis além do necessário para a demo.
- logs na worksheet “auditoria” sem dados pessoais.

## implantação

- local do apresentador em windows ou mac, com python 3.10+.
- instalar dependências:
    - `pip install streamlit google-api-python-client google-auth openai faiss-cpu`
- executar com `streamlit run app.py`.
- alternativa: replit ou codespaces para partilha rápida.

## observabilidade

- métricas na barra lateral: tempo de execução do phantom, linhas novas, duplicados removidos, tamanho do índice, latência média de resposta.
- erros apresentados com mensagens accionáveis e botão “ver log”.

## caminho para produção

- substituir phantom por exportações oficiais do recruiter ou por integração aprovada.
- mover dados para uma base relacional e índice vectorial gerido.
- adicionar sso, perfis e auditoria completa.
- documentação de privacidade e contratos de dados.