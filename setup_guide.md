# Guia de Configuração - Demo Agente de Recrutamento

## 🚀 Configuração Rápida

### 1. Variáveis de Ambiente

Crie um ficheiro `.env` na raiz do projeto com:

```bash
# PhantomBuster API
PHANTOMBUSTER_API_KEY=sua_api_key_aqui
PHANTOMBUSTER_AGENT_ID=seu_agent_id_aqui

# Google Sheets API
GOOGLE_SHEETS_ID=id_da_sua_google_sheet
GOOGLE_CREDENTIALS_FILE=caminho/para/service-account-key.json

# OpenAI API
OPENAI_API_KEY=sua_openai_api_key_aqui

# Configurações opcionais
MAX_CANDIDATES=100
TOP_K_RESULTS=5
EMBEDDING_MODEL=text-embedding-ada-002
```

### 2. Google Sheets Setup

1. **Criar Google Sheet:**
   - Vá para [Google Sheets](https://sheets.google.com)
   - Crie uma nova sheet
   - Copie o ID da URL (ex: `1ABC123...`)

2. **Configurar Service Account:**
   - Vá para [Google Cloud Console](https://console.cloud.google.com)
   - Crie um novo projeto ou selecione existente
   - Ative a Google Sheets API
   - Crie uma Service Account
   - Descarregue o ficheiro JSON de credenciais
   - Partilhe a Google Sheet com o email da Service Account

3. **Estrutura das Worksheets:**
   
   **Worksheet "candidatos" (criar automaticamente):**
   ```
   name | headline | location | current_company | education | linkedin_url | source | ingested_at | summary | skills_tags
   ```
   
   **Worksheet "auditoria" (criar automaticamente):**
   ```
   timestamp | action | details | user
   ```

### 3. PhantomBuster Setup

1. **Criar conta:**
   - Vá para [PhantomBuster](https://phantombuster.com)
   - Crie uma conta gratuita

2. **Configurar agente:**
   - Escolha "LinkedIn Profile Scraper" ou "LinkedIn Search Export"
   - Configure com a sua Google Sheet
   - Obtenha o Agent ID

3. **Obter API Key:**
   - Vá para Settings > API
   - Copie a sua API Key

### 4. OpenAI Setup

1. **Criar conta:**
   - Vá para [OpenAI](https://openai.com)
   - Crie uma conta

2. **Configurar billing:**
   - Adicione método de pagamento
   - Crie uma API Key

## 🧪 Teste Rápido

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Executar aplicação:**
   ```bash
   streamlit run app.py
   ```

3. **Testar fluxo:**
   - Clique "Actualizar Dados"
   - Aguarde conclusão
   - Clique "Reindexar"
   - Digite uma pergunta
   - Veja resultados

## 🔧 Troubleshooting

### Erro: "Configurações em falta"
- Verifique se todas as variáveis de ambiente estão definidas
- Confirme que o ficheiro `.env` está na raiz do projeto

### Erro: "Google Sheets API"
- Verifique se a Service Account tem permissões
- Confirme que a Google Sheet está partilhada
- Verifique se o ficheiro de credenciais existe

### Erro: "PhantomBuster API"
- Confirme que a API Key está correcta
- Verifique se o Agent ID existe
- Confirme que o agente está configurado

### Erro: "OpenAI API"
- Verifique se a API Key está correcta
- Confirme que tem billing activo
- Verifique os limites de uso

## 📊 Dados de Teste

Se não tiver dados reais, pode usar dados de teste:

1. **Criar dados mock na Google Sheet:**
   ```csv
   name,headline,location,current_company,education,linkedin_url,source,ingested_at,summary,skills_tags
   João Silva,Analista Financeiro,Lisboa,Banco XYZ,Mestrado em Finanças,https://linkedin.com/in/joao-silva,test,2024-01-01,João Silva | Analista Financeiro | Mestrado em Finanças | Banco XYZ | Skills: finanças,finanças
   Maria Santos,Marketing Manager,Porto,Startup ABC,Licenciatura em Marketing,https://linkedin.com/in/maria-santos,test,2024-01-01,Maria Santos | Marketing Manager | Licenciatura em Marketing | Startup ABC | Skills: marketing,marketing
   ```

2. **Testar pesquisa:**
   - "Quem tem mestrado em finanças?"
   - "Quem trabalha em marketing?"

## 🎯 Próximos Passos

1. **Configurar todas as APIs**
2. **Testar com dados reais**
3. **Personalizar queries de pesquisa**
4. **Ajustar configurações de IA**
5. **Implementar melhorias**

## 📞 Suporte

Para problemas técnicos:
1. Verificar logs de auditoria na Google Sheet
2. Confirmar configurações de API
3. Testar com dados mock primeiro
4. Consultar documentação das APIs
