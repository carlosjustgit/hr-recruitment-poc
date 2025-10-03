"""
Demo Agente de Recrutamento - Aplicação Principal Streamlit
"""
import streamlit as st
import time
from typing import Dict, Any, List
import traceback

# Importar módulos
from config import Config
from phantom_client import PhantomBusterClient
from sheets_client import GoogleSheetsClient
from normalizer import DataNormalizer
from indexer import SemanticIndexer
from qa import QASystem
from audit import AuditLogger

# Configuração da página
st.set_page_config(
    page_title="Demo Agente de Recrutamento",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar componentes
@st.cache_resource
def init_components():
    """Inicializa componentes da aplicação"""
    try:
        # Inicializar apenas componentes que funcionam sem APIs externas
        normalizer = DataNormalizer()
        qa_system = QASystem()
        
        # Tentar inicializar outros componentes, mas não falhar se não funcionarem
        phantom_client = None
        sheets_client = None
        indexer = None
        audit_logger = None
        
        try:
            phantom_client = PhantomBusterClient()
        except Exception:
            st.warning("⚠️ PhantomBuster não configurado - modo demo")
        
        try:
            sheets_client = GoogleSheetsClient()
        except Exception:
            st.warning("⚠️ Google Sheets não configurado - modo demo")
        
        try:
            indexer = SemanticIndexer()
        except Exception:
            st.warning("⚠️ Indexador semântico não disponível - modo demo")
        
        try:
            audit_logger = AuditLogger()
        except Exception:
            st.warning("⚠️ Sistema de auditoria não disponível - modo demo")
        
        return {
            'phantom': phantom_client,
            'sheets': sheets_client,
            'normalizer': normalizer,
            'indexer': indexer,
            'qa': qa_system,
            'audit': audit_logger
        }
    except Exception as e:
        st.error(f"Erro ao inicializar componentes: {e}")
        return None

def main():
    """Função principal da aplicação"""
    
    # Banner POC
    st.markdown("""
    <div style="background-color: #ff6b6b; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
        <h3>⚠️ PROVA DE CONCEITO</h3>
        <p>Esta é uma demo para mostrar a experiência do utilizador. Em produção, as fontes de dados serão oficiais e consentidas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Título principal
    st.title("🎯 Demo Agente de Recrutamento")
    st.markdown("Pesquise candidatos usando linguagem natural")
    
    # Inicializar componentes
    components = init_components()
    if not components:
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Controlo de Dados")
        
        # Secção de dados
        st.subheader("🔄 Dados")
        
        if st.button("🔄 Actualizar Dados", type="primary"):
            update_data(components)
        
        # Estado do job
        if 'job_status' in st.session_state:
            display_job_status()
        
        # Secção de índice
        st.subheader("🔍 Índice")
        
        if st.button("🔍 Reindexar"):
            reindex_data(components)
        
        # Top-K selector
        top_k = st.slider("Número de resultados", 1, 10, 5)
        st.session_state['top_k'] = top_k
        
        # Secção de métricas
        st.subheader("📈 Métricas")
        display_metrics(components)
        
        # Secção admin
        st.subheader("⚙️ Admin")
        
        # Remover candidato
        linkedin_url_to_remove = st.text_input("LinkedIn URL para remover:")
        if st.button("🗑️ Remover Candidato") and linkedin_url_to_remove:
            remove_candidate(components, linkedin_url_to_remove)
        
        # Link para sheet
        if st.button("📊 Ver Google Sheet"):
            st.markdown(f"[Abrir Google Sheet](https://docs.google.com/spreadsheets/d/{Config.GOOGLE_SHEETS_ID})")
    
    # Área principal
    st.header("🔍 Pesquisa de Candidatos")
    
    # Campo de pergunta
    question = st.text_input(
        "Faça a sua pergunta:",
        placeholder="Ex: Quem tem mestrado em finanças? Quem tem experiência em análise de risco?",
        help="Exemplos: quem tem mestrado em finanças, quem trabalhou com análise de risco"
    )
    
    # Sugestões de pesquisa
    if not question:
        st.info("💡 Sugestões de pesquisa:")
        if components['qa']:
            suggestions = components['qa'].generate_search_suggestions()
        else:
            suggestions = [
                "Quien tiene magíster en finanzas?",
                "Quien tiene experiencia en análisis de riesgo?",
                "Quien trabajó en marketing digital?",
                "Quien tiene skills en Python y data science?",
                "Quien tiene experiencia en minería?",
                "Quien trabajó en startups chilenas?"
            ]
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions[:6]):
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggestion_{i}"):
                    st.session_state['question'] = suggestion
                    st.rerun()
    
    # Botão de pesquisa
    if st.button("🔍 Pesquisar", disabled=not question):
        search_candidates(components, question)
    
    # Resultados
    if 'search_results' in st.session_state:
        display_results(components)
    
    # Rodapé com log da sessão
    display_session_log(components)

def update_data(components: Dict[str, Any]):
    """Actualiza dados via PhantomBuster"""
    try:
        with st.spinner("🔄 A actualizar dados..."):
            # Lançar job PhantomBuster para Chile
            job_id = components['phantom'].launch_search(
                query="Chile AND (finanzas OR finance OR contabilidad OR ingeniero OR marketing OR ventas)",
                limit=Config.MAX_CANDIDATES
            )
            
            st.session_state['job_id'] = job_id
            st.session_state['job_status'] = 'running'
            
            # Fazer poll do status
            status_result = components['phantom'].poll_status(job_id, timeout=300)
            
            if status_result['status'] == 'succeeded':
                st.success("✅ Dados actualizados com sucesso!")
                
                # Ler dados da sheet
                candidates = components['sheets'].read_rows(Config.CANDIDATES_WORKSHEET)
                
                # Normalizar dados
                normalized_candidates = components['normalizer'].normalize_all(candidates)
                
                # Escrever dados normalizados de volta
                components['sheets'].write_rows(
                    Config.CANDIDATES_WORKSHEET, 
                    normalized_candidates, 
                    clear_first=True
                )
                
                # Registo de auditoria
                if components['audit']:
                    components['audit'].log_data_update(
                        new_rows=len(normalized_candidates),
                        removed_rows=0,
                        total_rows=len(normalized_candidates)
                    )
                
                st.session_state['job_status'] = 'completed'
                st.rerun()
                
            else:
                st.error(f"❌ Erro ao actualizar dados: {status_result.get('message', 'Erro desconhecido')}")
                if components['audit']:
                    components['audit'].log_error(
                        'data_update_failed',
                        status_result.get('message', 'Erro desconhecido'),
                        'phantom_job'
                    )
                st.session_state['job_status'] = 'failed'
                
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        if components['audit']:
            components['audit'].log_error('data_update_exception', str(e), 'update_data')
        traceback.print_exc()

def display_job_status():
    """Mostra estado do job"""
    status = st.session_state.get('job_status', 'idle')
    
    if status == 'running':
        st.info("🔄 Job em execução...")
    elif status == 'completed':
        st.success("✅ Job concluído")
    elif status == 'failed':
        st.error("❌ Job falhou")

def reindex_data(components: Dict[str, Any]):
    """Reindexa dados"""
    try:
        with st.spinner("🔍 A reindexar dados..."):
            # Ler dados da sheet
            candidates = components['sheets'].read_rows(Config.CANDIDATES_WORKSHEET)
            
            if not candidates:
                st.warning("⚠️ Nenhum candidato encontrado. Actualize os dados primeiro.")
                return
            
            # Construir índice
            success = components['indexer'].build(candidates)
            
            if success:
                st.success(f"✅ Índice construído com {len(candidates)} candidatos")
                
                # Registo de auditoria
                if components['audit']:
                    components['audit'].log_reindex(len(candidates))
                
                st.session_state['index_built'] = True
            else:
                st.error("❌ Erro ao construir índice")
                
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        if components['audit']:
            components['audit'].log_error('reindex_exception', str(e), 'reindex_data')

def display_metrics(components: Dict[str, Any]):
    """Mostra métricas na sidebar"""
    try:
        # Estatísticas do índice
        index_stats = components['indexer'].get_index_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Candidatos", index_stats.get('total_candidates', 0))
        with col2:
            st.metric("Índice", "✅" if index_stats.get('index_built') else "❌")
        
        # Estatísticas de auditoria
        audit_stats = {}
        if components['audit']:
            try:
                audit_stats = components['audit'].get_action_stats()
            except:
                pass
        
        if audit_stats:
            st.write("**Actividade recente:**")
            for action, count in list(audit_stats.items())[:3]:
                st.write(f"- {action}: {count}")
                
    except Exception as e:
        st.write("Métricas não disponíveis")

def search_candidates(components: Dict[str, Any], question: str):
    """Pesquisa candidatos"""
    try:
        with st.spinner("🔍 A pesquisar..."):
            # Se não há indexer disponível, usar dados de demo
            if not components['indexer']:
                # Dados de demonstração para Chile
                demo_candidates = [
                    {
                        'name': 'Carlos Mendoza',
                        'headline': 'Analista Financiero Senior',
                        'location': 'Santiago, Chile',
                        'current_company': 'Banco Santander Chile',
                        'education': 'Magíster en Finanzas - Universidad de Chile',
                        'linkedin_url': 'https://linkedin.com/in/carlos-mendoza',
                        'skills_tags': ['finanzas', 'análise'],
                        'similarity_score': 0.95,
                        'rank': 1
                    },
                    {
                        'name': 'María González',
                        'headline': 'Marketing Manager Digital',
                        'location': 'Valparaíso, Chile',
                        'current_company': 'StartupTech Chile',
                        'education': 'Ingeniería Comercial - PUCV',
                        'linkedin_url': 'https://linkedin.com/in/maria-gonzalez',
                        'skills_tags': ['marketing', 'digital'],
                        'similarity_score': 0.87,
                        'rank': 2
                    },
                    {
                        'name': 'Diego Ramírez',
                        'headline': 'Data Scientist',
                        'location': 'Concepción, Chile',
                        'current_company': 'TechCorp Chile',
                        'education': 'Ingeniería Informática - Universidad de Concepción',
                        'linkedin_url': 'https://linkedin.com/in/diego-ramirez',
                        'skills_tags': ['tecnologia', 'análise'],
                        'similarity_score': 0.82,
                        'rank': 3
                    },
                    {
                        'name': 'Ana Herrera',
                        'headline': 'Contadora Senior',
                        'location': 'Santiago, Chile',
                        'current_company': 'EY Chile',
                        'education': 'Contador Auditor - Universidad de Chile',
                        'linkedin_url': 'https://linkedin.com/in/ana-herrera',
                        'skills_tags': ['contabilidad', 'auditoria'],
                        'similarity_score': 0.78,
                        'rank': 4
                    },
                    {
                        'name': 'Roberto Silva',
                        'headline': 'Ingeniero de Ventas',
                        'location': 'Antofagasta, Chile',
                        'current_company': 'Minera Escondida',
                        'education': 'Ingeniería Industrial - Universidad Católica del Norte',
                        'linkedin_url': 'https://linkedin.com/in/roberto-silva',
                        'skills_tags': ['ventas', 'minería'],
                        'similarity_score': 0.75,
                        'rank': 5
                    }
                ]
                
                hits = demo_candidates
                answer = f"Encontrei {len(hits)} candidatos relevantes para a sua pesquisa '{question}'. Estes são os perfis mais adequados baseados nas suas competências e experiência."
                justifications = [
                    "Alta relevância | Skills relevantes: finanças, análise | Educação relevante",
                    "Relevância moderada | Skills relevantes: marketing, digital | Educação relevante", 
                    "Relevância moderada | Skills relevantes: tecnologia, análise | Educação relevante"
                ]
                sources = hits
                
            else:
                # Usar indexer real se disponível
                if not st.session_state.get('index_built', False):
                    st.warning("⚠️ Índice não construído. Clique em 'Reindexar' primeiro.")
                    return
                
                hits = components['indexer'].search(question, k=st.session_state.get('top_k', 5))
                
                if not hits:
                    st.info("ℹ️ Nenhum candidato encontrado para esta pesquisa.")
                    return
                
                # Compor resposta
                answer, justifications, sources = components['qa'].compose_answer(hits, question)
            
            # Guardar resultados
            st.session_state['search_results'] = {
                'question': question,
                'answer': answer,
                'hits': hits,
                'justifications': justifications,
                'sources': sources
            }
            
            # Registo de auditoria (se disponível)
            if components['audit']:
                try:
                    if components['qa']:
                        intent_analysis = components['qa'].analyze_query_intent(question)
                        components['audit'].log_search(
                            question, 
                            len(hits), 
                            intent_analysis['intent_type']
                        )
                except:
                    pass
            
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Erro na pesquisa: {e}")
        if components['audit']:
            try:
                components['audit'].log_error('search_exception', str(e), 'search_candidates')
            except:
                pass

def display_results(components: Dict[str, Any]):
    """Mostra resultados da pesquisa"""
    results = st.session_state['search_results']
    
    st.subheader("📋 Resposta")
    st.write(results['answer'])
    
    st.subheader("👥 Candidatos Encontrados")
    
    hits = results['hits']
    justifications = results['justifications']
    
    for i, (candidate, justification) in enumerate(zip(hits, justifications)):
        with st.expander(f"👤 {candidate.get('name', 'N/A')} (Score: {candidate.get('similarity_score', 0):.3f})"):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Perfil:** {candidate.get('headline', 'N/A')}")
                st.write(f"**Educação:** {candidate.get('education', 'N/A')}")
                st.write(f"**Empresa:** {candidate.get('current_company', 'N/A')}")
                st.write(f"**Localização:** {candidate.get('location', 'N/A')}")
                
                if candidate.get('skills_tags'):
                    skills_str = ", ".join(candidate['skills_tags'])
                    st.write(f"**Skills:** {skills_str}")
            
            with col2:
                st.write(f"**Relevância:** {justification}")
                
                # Links
                if candidate.get('linkedin_url'):
                    st.markdown(f"[🔗 LinkedIn]({candidate['linkedin_url']})")
                
                st.markdown(f"[📊 Ver na Sheet](https://docs.google.com/spreadsheets/d/{Config.GOOGLE_SHEETS_ID})")

def remove_candidate(components: Dict[str, Any], linkedin_url: str):
    """Remove candidato"""
    try:
        with st.spinner("🗑️ A remover candidato..."):
            # Remover da sheet
            success = components['sheets'].delete_by_url(Config.CANDIDATES_WORKSHEET, linkedin_url)
            
            if success:
                # Remover do índice
                components['indexer'].remove_candidate(linkedin_url)
                
                st.success("✅ Candidato removido com sucesso")
                
                # Registo de auditoria
                if components['audit']:
                    components['audit'].log_delete(linkedin_url)
                
                st.rerun()
            else:
                st.error("❌ Candidato não encontrado")
                
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        if components['audit']:
            components['audit'].log_error('delete_exception', str(e), 'remove_candidate')

def display_session_log(components: Dict[str, Any]):
    """Mostra log da sessão"""
    st.markdown("---")
    st.subheader("📝 Log da Sessão")
    
    try:
        recent_actions = []
        if components['audit']:
            recent_actions = components['audit'].get_recent_actions(5)
        
        if recent_actions:
            for action in recent_actions:
                timestamp = action.get('timestamp', 'N/A')
                action_type = action.get('action', 'N/A')
                details = action.get('details', 'N/A')
                
                st.write(f"**{timestamp}** - {action_type}: {details}")
        else:
            st.write("Nenhuma ação registada nesta sessão.")
            
    except Exception as e:
        st.write("Log não disponível")

if __name__ == "__main__":
    # Verificar configurações
    if not Config.validate():
        st.error("""
        ❌ Configurações em falta!
        
        Por favor, configure as seguintes variáveis de ambiente:
        - PHANTOMBUSTER_API_KEY
        - PHANTOMBUSTER_AGENT_ID  
        - GOOGLE_SHEETS_ID
        - GOOGLE_CREDENTIALS_FILE
        - OPENAI_API_KEY
        """)
        st.stop()
    
    main()
