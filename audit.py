"""
Módulo para sistema de auditoria
"""
from datetime import datetime
from typing import Dict, Any, List
from sheets_client import GoogleSheetsClient
from config import Config

class AuditLogger:
    """Sistema de auditoria para registar ações"""
    
    def __init__(self):
        self.sheets_client = GoogleSheetsClient()
        self.audit_worksheet = Config.AUDIT_WORKSHEET
    
    def log(self, action: str, details: Dict[str, Any], user: str = "system") -> bool:
        """
        Regista uma ação na worksheet de auditoria
        
        Args:
            action: Tipo de ação (update, reindex, search, delete, etc.)
            details: Detalhes da ação
            user: Utilizador que executou a ação
            
        Returns:
            True se sucesso
        """
        try:
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'details': self._format_details(details),
                'user': user
            }
            
            # Adicionar à worksheet de auditoria
            return self.sheets_client.append_rows(self.audit_worksheet, [audit_entry])
            
        except Exception as e:
            # Se falhar, pelo menos imprimir para debug
            print(f"Erro ao registar auditoria: {e}")
            return False
    
    def _format_details(self, details: Dict[str, Any]) -> str:
        """
        Formata detalhes para string
        
        Args:
            details: Dicionário com detalhes
            
        Returns:
            String formatada
        """
        if not details:
            return "Sem detalhes"
        
        formatted_parts = []
        for key, value in details.items():
            if isinstance(value, (list, dict)):
                formatted_parts.append(f"{key}: {str(value)[:100]}")  # Limitar tamanho
            else:
                formatted_parts.append(f"{key}: {str(value)}")
        
        return " | ".join(formatted_parts)
    
    def log_data_update(self, new_rows: int, removed_rows: int, total_rows: int) -> bool:
        """
        Regista atualização de dados
        
        Args:
            new_rows: Número de linhas novas
            removed_rows: Número de linhas removidas
            total_rows: Total de linhas após atualização
            
        Returns:
            True se sucesso
        """
        details = {
            'new_rows': new_rows,
            'removed_rows': removed_rows,
            'total_rows': total_rows,
            'operation': 'data_update'
        }
        
        return self.log('update', details)
    
    def log_reindex(self, candidates_count: int, index_type: str = "semantic") -> bool:
        """
        Regista reindexação
        
        Args:
            candidates_count: Número de candidatos indexados
            index_type: Tipo de índice
            
        Returns:
            True se sucesso
        """
        details = {
            'candidates_count': candidates_count,
            'index_type': index_type,
            'operation': 'reindex'
        }
        
        return self.log('reindex', details)
    
    def log_search(self, query: str, results_count: int, intent_type: str = "general") -> bool:
        """
        Regista pesquisa
        
        Args:
            query: Query de pesquisa
            results_count: Número de resultados
            intent_type: Tipo de intenção da pesquisa
            
        Returns:
            True se sucesso
        """
        # Não registar query completa por privacidade
        query_summary = query[:50] + "..." if len(query) > 50 else query
        
        details = {
            'query_length': len(query),
            'query_summary': query_summary,
            'results_count': results_count,
            'intent_type': intent_type,
            'operation': 'search'
        }
        
        return self.log('search', details)
    
    def log_delete(self, linkedin_url: str, candidate_name: str = None) -> bool:
        """
        Regista remoção de candidato
        
        Args:
            linkedin_url: URL do LinkedIn removido
            candidate_name: Nome do candidato (opcional)
            
        Returns:
            True se sucesso
        """
        details = {
            'linkedin_url': linkedin_url,
            'candidate_name': candidate_name or 'N/A',
            'operation': 'delete'
        }
        
        return self.log('delete', details)
    
    def log_error(self, error_type: str, error_message: str, context: str = None) -> bool:
        """
        Regista erro
        
        Args:
            error_type: Tipo de erro
            error_message: Mensagem de erro
            context: Contexto adicional
            
        Returns:
            True se sucesso
        """
        details = {
            'error_type': error_type,
            'error_message': error_message[:200],  # Limitar tamanho
            'context': context or 'N/A',
            'operation': 'error'
        }
        
        return self.log('error', details)
    
    def get_recent_actions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém ações recentes da auditoria
        
        Args:
            limit: Número máximo de ações a retornar
            
        Returns:
            Lista de ações recentes
        """
        try:
            # Ler últimas linhas da worksheet de auditoria
            rows = self.sheets_client.read_rows(self.audit_worksheet)
            
            # Ordenar por timestamp (mais recente primeiro)
            sorted_rows = sorted(rows, key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return sorted_rows[:limit]
            
        except Exception as e:
            print(f"Erro ao obter ações recentes: {e}")
            return []
    
    def get_action_stats(self) -> Dict[str, int]:
        """
        Obtém estatísticas de ações
        
        Returns:
            Dict com contadores de ações
        """
        try:
            rows = self.sheets_client.read_rows(self.audit_worksheet)
            
            stats = {}
            for row in rows:
                action = row.get('action', 'unknown')
                stats[action] = stats.get(action, 0) + 1
            
            return stats
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
