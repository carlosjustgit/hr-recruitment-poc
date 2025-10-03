"""
Módulo para sistema de perguntas e respostas
"""
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from config import Config

class QASystem:
    """Sistema de perguntas e respostas para candidatos"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def compose_answer(self, hits: List[Dict[str, Any]], question: str) -> Tuple[str, List[str], List[Dict[str, Any]]]:
        """
        Compõe resposta baseada nos hits da pesquisa
        
        Args:
            hits: Lista de candidatos encontrados
            question: Pergunta original
            
        Returns:
            Tuple com (resposta_texto, justificativas, fontes)
        """
        try:
            if not hits:
                return "Não foram encontrados candidatos que correspondam à sua pesquisa.", [], []
            
            # Preparar contexto dos candidatos
            candidates_context = self._prepare_candidates_context(hits)
            
            # Gerar resposta usando OpenAI
            prompt = self._create_prompt(question, candidates_context)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "És um assistente de recrutamento especializado em analisar perfis de candidatos. Responde de forma clara e profissional."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            answer_text = response.choices[0].message.content
            
            # Extrair justificativas
            justifications = self._extract_justifications(hits)
            
            # Preparar fontes
            sources = self._prepare_sources(hits)
            
            return answer_text, justifications, sources
            
        except Exception as e:
            raise Exception(f"Erro ao compor resposta: {e}")
    
    def _prepare_candidates_context(self, hits: List[Dict[str, Any]]) -> str:
        """Prepara contexto dos candidatos para o prompt"""
        context_parts = []
        
        for i, candidate in enumerate(hits[:5], 1):  # Máximo 5 candidatos
            context_part = f"Candidato {i}:\n"
            context_part += f"- Nome: {candidate.get('name', 'N/A')}\n"
            context_part += f"- Perfil: {candidate.get('headline', 'N/A')}\n"
            context_part += f"- Educação: {candidate.get('education', 'N/A')}\n"
            context_part += f"- Empresa atual: {candidate.get('current_company', 'N/A')}\n"
            context_part += f"- Skills: {', '.join(candidate.get('skills_tags', []))}\n"
            context_part += f"- Score de relevância: {candidate.get('similarity_score', 0):.3f}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, candidates_context: str) -> str:
        """Cria prompt para o OpenAI"""
        return f"""
Com base nos seguintes candidatos encontrados, responde à pergunta do recrutador de forma clara e útil.

Pergunta: {question}

Candidatos encontrados:
{candidates_context}

Por favor:
1. Responde diretamente à pergunta
2. Menciona os candidatos mais relevantes (máximo 3-4)
3. Explica brevemente por que cada candidato é relevante
4. Mantém a resposta concisa mas informativa

Resposta:
"""
    
    def _extract_justifications(self, hits: List[Dict[str, Any]]) -> List[str]:
        """Extrai justificativas para cada candidato"""
        justifications = []
        
        for candidate in hits[:3]:  # Máximo 3 justificativas
            justification_parts = []
            
            # Justificação baseada no score
            score = candidate.get('similarity_score', 0)
            if score > 0.8:
                justification_parts.append("Alta relevância")
            elif score > 0.6:
                justification_parts.append("Relevância moderada")
            else:
                justification_parts.append("Relevância baixa")
            
            # Justificação baseada em skills
            skills = candidate.get('skills_tags', [])
            if skills:
                justification_parts.append(f"Skills relevantes: {', '.join(skills[:2])}")
            
            # Justificação baseada na educação
            education = candidate.get('education', '')
            if education and len(education) > 10:
                justification_parts.append("Educação relevante")
            
            justification = " | ".join(justification_parts)
            justifications.append(justification)
        
        return justifications
    
    def _prepare_sources(self, hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepara fontes com links para sheet e LinkedIn"""
        sources = []
        
        for candidate in hits:
            source = {
                'name': candidate.get('name', 'N/A'),
                'linkedin_url': candidate.get('linkedin_url', ''),
                'sheet_row': candidate.get('rank', 0),
                'similarity_score': candidate.get('similarity_score', 0)
            }
            sources.append(source)
        
        return sources
    
    def generate_search_suggestions(self) -> List[str]:
        """Gera sugestões de pesquisa para o utilizador"""
        return [
            "Quem tem mestrado em finanças?",
            "Quem tem experiência em análise de risco?",
            "Quem trabalhou em marketing digital?",
            "Quem tem skills em Python e data science?",
            "Quem tem experiência em gestão de equipas?",
            "Quem trabalhou em startups?",
            "Quem tem formação em engenharia?",
            "Quem tem experiência internacional?"
        ]
    
    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analisa a intenção da query
        
        Args:
            query: Query do utilizador
            
        Returns:
            Dict com análise da intenção
        """
        query_lower = query.lower()
        
        # Detectar tipo de pesquisa
        if any(word in query_lower for word in ['mestrado', 'licenciatura', 'doutoramento', 'formação', 'educação']):
            intent_type = 'education'
        elif any(word in query_lower for word in ['experiência', 'trabalhou', 'trabalha', 'empresa']):
            intent_type = 'experience'
        elif any(word in query_lower for word in ['skills', 'conhecimento', 'tecnologia', 'ferramenta']):
            intent_type = 'skills'
        elif any(word in query_lower for word in ['localização', 'cidade', 'país', 'região']):
            intent_type = 'location'
        else:
            intent_type = 'general'
        
        return {
            'intent_type': intent_type,
            'query_length': len(query),
            'has_question_mark': '?' in query,
            'keywords': [word for word in query.split() if len(word) > 3]
        }
