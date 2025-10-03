import streamlit as st
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Demo Agente de Recrutamento",
    page_icon="🎯",
    layout="wide"
)

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

# Sidebar
with st.sidebar:
    st.header("📊 Controlo de Dados")
    
    st.subheader("🔄 Dados")
    if st.button("🔄 Actualizar Dados", type="primary"):
        st.success("✅ Dados actualizados! (Demo)")
    
    st.subheader("🔍 Índice")
    if st.button("🔍 Reindexar"):
        st.success("✅ Índice construído! (Demo)")
    
    st.subheader("📈 Métricas")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Candidatos", len(demo_candidates))
    with col2:
        st.metric("Índice", "✅")

# Área principal
st.header("🔍 Pesquisa de Candidatos")

# Campo de pergunta
question = st.text_input(
    "Faça a sua pergunta:",
    placeholder="Ex: Quien tiene magíster en finanzas? Quien tiene experiencia en minería?",
    help="Exemplos: quien tiene magíster en finanzas, quien trabajó en marketing digital"
)

# Sugestões de pesquisa
if not question:
    st.info("💡 Sugestões de pesquisa:")
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
    with st.spinner("🔍 A pesquisar..."):
        # Simular pesquisa
        hits = demo_candidates[:3]  # Top 3 resultados
        answer = f"Encontrei {len(hits)} candidatos relevantes para a sua pesquisa '{question}'. Estes são os perfis mais adequados baseados nas suas competências e experiência."
        
        st.subheader("📋 Resposta")
        st.write(answer)
        
        st.subheader("👥 Candidatos Encontrados")
        
        for i, candidate in enumerate(hits):
            with st.expander(f"👤 {candidate['name']} (Score: {candidate['similarity_score']:.3f})"):
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Perfil:** {candidate['headline']}")
                    st.write(f"**Educação:** {candidate['education']}")
                    st.write(f"**Empresa:** {candidate['current_company']}")
                    st.write(f"**Localização:** {candidate['location']}")
                    
                    skills_str = ", ".join(candidate['skills_tags'])
                    st.write(f"**Skills:** {skills_str}")
                
                with col2:
                    st.write(f"**Relevância:** Alta relevância | Skills relevantes | Educação relevante")
                    
                    # Links
                    st.markdown(f"[🔗 LinkedIn]({candidate['linkedin_url']})")
                    st.markdown("[📊 Ver na Sheet](https://docs.google.com/spreadsheets/d/12Wp7WSecBTDn1bwb-phv5QN6JEC8vpztgs_tK5_fMdQ)")

# Rodapé
st.markdown("---")
st.subheader("📝 Log da Sessão")
st.write(f"**{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}** - Demo iniciada com dados chilenos")
