# spec kit

— demo de agente de recrutamento com phantombuster, google sheets e streamlit

## sumário executivo

prova de conceito que demonstra a captura automática de perfis a partir de uma pesquisa no linkedin via phantombuster, escrita directa para uma google sheet, normalização e enriquecimento leve, indexação em memória e um agente de perguntas e respostas em streamlit. a demo não usa importações manuais; o botão “actualizar dados” lança o fluxo ponta a ponta.

> nota de conformidade: esta demo é uma prova de conceito. em produção, a origem de dados deverá ser alterada para fluxos oficiais e consentidos. a demo mostra o “como” técnico e a experiência de utilizador, não valida o modelo jurídico definitivo.
> 

## objectivo

permitir que um utilizador faça perguntas como “quem tem mestrado em finanças” ou “quem tem experiência em análise de risco” sobre um conjunto de candidatos provenientes de uma pesquisa dirigida e veja respostas justificadas com ligações para a sheet e para o perfil.

## âmbito

- integração automática com phantombuster por api para executar uma pesquisa pré-definida.
- escrita automática em google sheets através de integração do phantom ou apps script.
- limpeza, deduplicação e etiquetagem básica de skills.
- índice semântico em memória.
- ui mínima em streamlit com: actualizar dados, reindexar, pesquisar, ver fontes, remover registo.
- registo simples de auditoria da demo numa segunda sheet.

## fora do âmbito

- integrações com ats, rsc ou apis oficiais do linkedin.
- scoring avançado, faixas salariais, juntores de dados privados sensíveis.
- armazenamento persistente em base de dados dedicada.
- gestão de utilizadores e permissões complexas.

## suposições e riscos

- suposição: a conta phantom e a integração com google sheets estão activas e funcionais.
- suposição: a pesquisa usada não excede limites diários do linkedin nem do phantom.
- risco: alterações de detecção no linkedin podem interromper a recolha.
- mitigação: ter script de fallback para dados mock numa sheet separada, desactivado por defeito. o botão de fallback só aparece na versão interna de testes.

## histórias de utilizador

- como recrutador, quero carregar a lista de candidatos automaticamente para que não precise de processos manuais.
- como recrutador, quero pesquisar candidatos por educação, experiências e palavras-chave e ver justificativas com fontes.
- como responsável de projecto, quero ver um alerta claro de origem e limites da demo e poder remover um registo a pedido.

## requisitos funcionais

1. lançar phantom por api com query parametrizável, limite e aleatorização de delays.
2. gravar resultados em google sheets, worksheet “candidatos”.
3. limpar e deduplicar por `linkedin_url`.
4. gerar `summary` curto e `skills_tags` a partir de headline e educação.
5. criar índice em memória e responder a perguntas com top-k e excertos.
6. expor fontes por candidato, incluindo link para a linha da sheet e para o perfil.
7. botão “remover” que apaga a linha na sheet e reindexa.
8. registar acções num log simples na worksheet “auditoria”.

## requisitos não funcionais

- tempo de actualização até 90 segundos para 100 perfis.
- tempo de resposta do qa inferior a 2 segundos para top-k=5 após índice construido.
- chaves e segredos apenas em variáveis de ambiente.
- mensagens de erro claras e acções propostas.

## dados e esquema

worksheet “candidatos”

- `name`, `headline`, `location`, `current_company`, `education`, `linkedin_url` (único), `source`, `ingested_at`, `summary`, `skills_tags`
worksheet “auditoria”
- `timestamp`, `action`, `details`, `user`

## critérios de aceitação

- ao clicar “actualizar dados”, o phantom é lançado, a sheet é actualizada e a ui mostra contagens de linhas novas e removidas.
- pesquisa por “mestrado em finanças” devolve 3 a 5 candidatos com justificativas e fontes.
- o botão “remover” elimina da sheet e do índice no momento.
- banner de aviso de poc é visível e não desactivável.

## plano de sprint da demo

dia 1

- configurar segredos e integração phantom → sheet
- endpoint interno para lançar job e verificar estado
dia 2
- normalização, dedupe e etiquetagem
- índice em memória e função de pesquisa
dia 3
- ui streamlit com estados, fontes, remoção e auditoria
- testes, runbook e guião de apresentação

## guardrails

- não adicionar campos de email nem informação sensível.
- não usar importações manuais.
- não armazenar segredos em código ou na sheet.
- tornar o phantom substituível por outra fonte no mesmo contrato de dados.

## runbook da demo

1. verificar variáveis de ambiente e permissões da service account na sheet.
2. abrir streamlit, clicar “actualizar dados”, aguardar sucesso.
3. clicar “reindexar”.
4. testar duas perguntas modelo.
5. demonstrar “remover” num registo de teste.
6. fechar com o slide de “caminho para produção” com integrações oficiais.