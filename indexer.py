"""
Módulo para indexação semântica e pesquisa
"""
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from config import Config

class SemanticIndexer:
    """Classe para indexação semântica e pesquisa de candidatos"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.embedding_model = Config.EMBEDDING_MODEL
        self.index = None
        self.candidates_data = []
        self.dimension = 1536  # Dimensão dos embeddings do OpenAI ada-002
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Obtém embedding de um texto usando OpenAI
        
        Args:
            text: Texto para embedar
            
        Returns:
            Lista com embedding
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Erro ao obter embedding: {e}")
    
    def _prepare_text_for_embedding(self, candidate: Dict[str, Any]) -> str:
        """
        Prepara texto do candidato para embedding
        
        Args:
            candidate: Dados do candidato
            
        Returns:
            Texto combinado para embedding
        """
        text_parts = []
        
        # Nome
        if candidate.get('name'):
            text_parts.append(f"Nome: {candidate['name']}")
        
        # Headline
        if candidate.get('headline'):
            text_parts.append(f"Perfil: {candidate['headline']}")
        
        # Educação
        if candidate.get('education'):
            text_parts.append(f"Educação: {candidate['education']}")
        
        # Empresa atual
        if candidate.get('current_company'):
            text_parts.append(f"Empresa atual: {candidate['current_company']}")
        
        # Localização
        if candidate.get('location'):
            text_parts.append(f"Localização: {candidate['location']}")
        
        # Skills
        if candidate.get('skills_tags'):
            skills_str = ", ".join(candidate['skills_tags'])
            text_parts.append(f"Skills: {skills_str}")
        
        # Summary
        if candidate.get('summary'):
            text_parts.append(f"Resumo: {candidate['summary']}")
        
        return " | ".join(text_parts)
    
    def build(self, candidates: List[Dict[str, Any]]) -> bool:
        """
        Constrói índice semântico a partir dos candidatos
        
        Args:
            candidates: Lista de candidatos para indexar
            
        Returns:
            True se sucesso
        """
        try:
            if not candidates:
                self.index = None
                self.candidates_data = []
                return True
            
            # Preparar textos
            texts = []
            for candidate in candidates:
                text = self._prepare_text_for_embedding(candidate)
                texts.append(text)
            
            # Obter embeddings
            embeddings = []
            for i, text in enumerate(texts):
                embedding = self._get_embedding(text)
                embeddings.append(embedding)
            
            # Converter para numpy array
            embeddings_array = np.array(embeddings).astype('float32')
            
            # Criar índice FAISS
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (cosine similarity)
            
            # Normalizar embeddings para cosine similarity
            faiss.normalize_L2(embeddings_array)
            
            # Adicionar ao índice
            self.index.add(embeddings_array)
            
            # Guardar dados dos candidatos
            self.candidates_data = candidates.copy()
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao construir índice: {e}")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Pesquisa candidatos usando query semântica
        
        Args:
            query: Query de pesquisa
            k: Número de resultados a retornar
            
        Returns:
            Lista de candidatos com scores
        """
        try:
            if self.index is None or len(self.candidates_data) == 0:
                return []
            
            # Obter embedding da query
            query_embedding = self._get_embedding(query)
            query_array = np.array([query_embedding]).astype('float32')
            
            # Normalizar para cosine similarity
            faiss.normalize_L2(query_array)
            
            # Pesquisar
            scores, indices = self.index.search(query_array, min(k, len(self.candidates_data)))
            
            # Preparar resultados
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.candidates_data):
                    candidate = self.candidates_data[idx].copy()
                    candidate['similarity_score'] = float(score)
                    candidate['rank'] = i + 1
                    results.append(candidate)
            
            return results
            
        except Exception as e:
            raise Exception(f"Erro na pesquisa: {e}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do índice
        
        Returns:
            Dict com estatísticas
        """
        if self.index is None:
            return {
                'total_candidates': 0,
                'index_built': False,
                'dimension': self.dimension
            }
        
        return {
            'total_candidates': len(self.candidates_data),
            'index_built': True,
            'dimension': self.dimension,
            'index_type': 'FAISS IndexFlatIP'
        }
    
    def clear(self):
        """Limpa o índice"""
        self.index = None
        self.candidates_data = []
    
    def remove_candidate(self, linkedin_url: str) -> bool:
        """
        Remove candidato do índice
        
        Args:
            linkedin_url: URL do LinkedIn do candidato a remover
            
        Returns:
            True se removido
        """
        try:
            # Encontrar candidato
            candidate_to_remove = None
            for i, candidate in enumerate(self.candidates_data):
                if candidate.get('linkedin_url') == linkedin_url:
                    candidate_to_remove = i
                    break
            
            if candidate_to_remove is None:
                return False
            
            # Remover da lista
            self.candidates_data.pop(candidate_to_remove)
            
            # Reconstruir índice se necessário
            if len(self.candidates_data) > 0:
                return self.build(self.candidates_data)
            else:
                self.clear()
                return True
                
        except Exception as e:
            raise Exception(f"Erro ao remover candidato: {e}")
