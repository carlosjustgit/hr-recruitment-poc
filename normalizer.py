"""
Módulo para normalização, deduplicação e etiquetagem de dados
"""
import re
from typing import List, Dict, Any, Set
from datetime import datetime

class DataNormalizer:
    """Classe para normalizar e processar dados de candidatos"""
    
    def __init__(self):
        # Skills comuns para etiquetagem
        self.common_skills = {
            'finanças': ['finanças', 'finance', 'financial', 'contabilidade', 'accounting'],
            'marketing': ['marketing', 'digital marketing', 'social media', 'branding'],
            'tecnologia': ['python', 'javascript', 'java', 'react', 'node.js', 'sql', 'data science'],
            'gestão': ['gestão', 'management', 'leadership', 'project management', 'agile'],
            'vendas': ['vendas', 'sales', 'business development', 'commercial'],
            'recursos humanos': ['rh', 'hr', 'recursos humanos', 'human resources', 'recrutamento'],
            'análise': ['análise', 'analysis', 'analytics', 'business intelligence', 'reporting'],
            'design': ['design', 'ui', 'ux', 'graphic design', 'web design'],
            'comunicação': ['comunicação', 'communication', 'public relations', 'content'],
            'logística': ['logística', 'logistics', 'supply chain', 'operations']
        }
    
    def clean(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Limpa dados básicos das linhas
        
        Args:
            rows: Lista de dicionários com dados brutos
            
        Returns:
            Lista de dicionários limpos
        """
        cleaned_rows = []
        
        for row in rows:
            cleaned_row = {}
            
            for key, value in row.items():
                if isinstance(value, str):
                    # Limpar espaços em branco
                    cleaned_value = value.strip()
                    
                    # Remover caracteres especiais excessivos
                    cleaned_value = re.sub(r'\s+', ' ', cleaned_value)
                    
                    # Capitalizar primeira letra de frases
                    cleaned_value = self._capitalize_sentences(cleaned_value)
                    
                    cleaned_row[key] = cleaned_value
                else:
                    cleaned_row[key] = value
            
            # Adicionar campos obrigatórios se não existirem
            if 'source' not in cleaned_row:
                cleaned_row['source'] = 'phantombuster'
            
            if 'ingested_at' not in cleaned_row:
                cleaned_row['ingested_at'] = datetime.now().isoformat()
            
            cleaned_rows.append(cleaned_row)
        
        return cleaned_rows
    
    def dedupe(self, rows: List[Dict[str, Any]], key: str = 'linkedin_url') -> List[Dict[str, Any]]:
        """
        Remove duplicados baseado numa chave
        
        Args:
            rows: Lista de dicionários
            key: Chave para identificar duplicados
            
        Returns:
            Lista sem duplicados
        """
        seen = set()
        unique_rows = []
        
        for row in rows:
            if key in row and row[key]:
                if row[key] not in seen:
                    seen.add(row[key])
                    unique_rows.append(row)
            else:
                # Manter linhas sem a chave (podem ser válidas)
                unique_rows.append(row)
        
        return unique_rows
    
    def tag_skills(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Etiqueta skills baseado no headline e educação
        
        Args:
            rows: Lista de dicionários com dados dos candidatos
            
        Returns:
            Lista com campo skills_tags adicionado
        """
        tagged_rows = []
        
        for row in rows:
            # Combinar texto para análise
            text_to_analyze = ""
            
            if 'headline' in row:
                text_to_analyze += f" {row['headline']}"
            
            if 'education' in row:
                text_to_analyze += f" {row['education']}"
            
            if 'current_company' in row:
                text_to_analyze += f" {row['current_company']}"
            
            # Converter para minúsculas para comparação
            text_lower = text_to_analyze.lower()
            
            # Encontrar skills
            found_skills = set()
            for skill_category, skill_keywords in self.common_skills.items():
                for keyword in skill_keywords:
                    if keyword.lower() in text_lower:
                        found_skills.add(skill_category)
                        break
            
            # Adicionar skills encontradas
            row['skills_tags'] = list(found_skills)
            tagged_rows.append(row)
        
        return tagged_rows
    
    def summarise(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Gera resumos curtos para cada candidato
        
        Args:
            rows: Lista de dicionários com dados dos candidatos
            
        Returns:
            Lista com campo summary adicionado
        """
        summarised_rows = []
        
        for row in rows:
            summary_parts = []
            
            # Nome
            if 'name' in row and row['name']:
                summary_parts.append(f"Nome: {row['name']}")
            
            # Headline
            if 'headline' in row and row['headline']:
                headline = row['headline'][:100]  # Limitar tamanho
                summary_parts.append(f"Perfil: {headline}")
            
            # Educação
            if 'education' in row and row['education']:
                education = row['education'][:80]  # Limitar tamanho
                summary_parts.append(f"Educação: {education}")
            
            # Empresa atual
            if 'current_company' in row and row['current_company']:
                company = row['current_company'][:60]  # Limitar tamanho
                summary_parts.append(f"Empresa: {company}")
            
            # Skills
            if 'skills_tags' in row and row['skills_tags']:
                skills_str = ", ".join(row['skills_tags'][:3])  # Máximo 3 skills
                summary_parts.append(f"Skills: {skills_str}")
            
            # Criar resumo
            summary = " | ".join(summary_parts)
            row['summary'] = summary
            summarised_rows.append(row)
        
        return summarised_rows
    
    def _capitalize_sentences(self, text: str) -> str:
        """Capitaliza primeira letra de cada frase"""
        sentences = re.split(r'([.!?]\s*)', text)
        capitalized = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                capitalized.append(sentence.capitalize())
            else:
                capitalized.append(sentence)
        
        return ''.join(capitalized)
    
    def normalize_all(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aplica todo o pipeline de normalização
        
        Args:
            rows: Lista de dicionários com dados brutos
            
        Returns:
            Lista completamente normalizada
        """
        # Pipeline de normalização
        cleaned = self.clean(rows)
        deduped = self.dedupe(cleaned)
        tagged = self.tag_skills(deduped)
        summarised = self.summarise(tagged)
        
        return summarised
