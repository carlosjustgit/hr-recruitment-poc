"""
Script para testar PhantomBuster API
"""
import os
from phantom_client import PhantomBusterClient
from config import Config

def test_phantom():
    """Testa a conexão com PhantomBuster"""
    
    print("Testando PhantomBuster API...")
    print(f"API Key: {Config.PHANTOMBUSTER_API_KEY[:10]}...")
    print(f"Agent ID: {Config.PHANTOMBUSTER_AGENT_ID}")
    
    try:
        # Inicializar cliente
        client = PhantomBusterClient()
        
        # Testar informações do agente
        print("\nObtendo informações do agente...")
        agent_info = client.get_agent_info()
        print(f"Agente encontrado: {agent_info.get('name', 'N/A')}")
        print(f"Tipo: {agent_info.get('type', 'N/A')}")
        print(f"Status: {agent_info.get('status', 'N/A')}")
        
        # Testar lançamento de job
        print("\nTestando lançamento de job...")
        job_id = client.launch_search(
            query="Chile AND finanzas",
            limit=5
        )
        
        print(f"Job lançado com sucesso! ID: {job_id}")
        
        # Testar status do job
        print("\nVerificando status do job...")
        status = client.poll_status(job_id, timeout=30)
        print(f"Status: {status}")
        
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    test_phantom()
