"""
Configurações da Demo Agente de Recrutamento
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis do ficheiro .env
load_dotenv()

class Config:
    """Configurações da aplicação"""
    
    # PhantomBuster (com fallback para nomes antigos)
    PHANTOMBUSTER_API_KEY: Optional[str] = os.getenv("PHANTOMBUSTER_API_KEY") or os.getenv("PHANTOM_API_KEY")
    PHANTOMBUSTER_AGENT_ID: Optional[str] = os.getenv("PHANTOMBUSTER_AGENT_ID") or os.getenv("PHANTOM_AGENT_ID")
    
    # Google Sheets (com fallback para nomes antigos)
    GOOGLE_SHEETS_ID: Optional[str] = os.getenv("GOOGLE_SHEETS_ID") or os.getenv("GOOGLE_SHEET_ID")
    GOOGLE_CREDENTIALS_FILE: Optional[str] = os.getenv("GOOGLE_CREDENTIALS_FILE") or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_B64")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Configurações da aplicação
    MAX_CANDIDATES: int = int(os.getenv("MAX_CANDIDATES", "100"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # Sheets worksheets
    CANDIDATES_WORKSHEET = "candidatos"
    AUDIT_WORKSHEET = "auditoria"
    
    @classmethod
    def validate(cls) -> bool:
        """Valida se todas as configurações necessárias estão presentes"""
        # Para demo, só precisamos da OpenAI API Key
        required_vars = [
            cls.OPENAI_API_KEY
        ]
        return all(var is not None for var in required_vars)
