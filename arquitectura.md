# arquitectura

da demo — phantombuster, google sheets e streamlit

## visão geral

a arquitectura minimiza dependências: o phantombuster recolhe e escreve para a google sheet; a aplicação streamlit lê, normaliza, indexa em memória e responde a perguntas. tudo sem supabase e sem passos manuais.

## componentes

- phantombuster api: executa pesquisa linkedin predefinida e exporta para google sheets.
- google sheets api: fonte de verdade; worksheets “candidatos” e “auditoria”.
- streamlit app:
    - módulo de orquestração: lança phantom, faz poll de estado, regista auditoria.
    - módulo de dados: leitura, limpeza, dedupe, etiquetagem.
    - módulo de vectorização: embeddings e índice em memória.
    - módulo de qa: pesquisa, composição de resposta e apresentação de fontes.
- fornecedores de ia:
    - embeddings e geração de texto via openai ou equivalente configurável.

## diagrama ascii