"""
Teste rápido do PhantomBuster
"""
from phantom_client import PhantomBusterClient

def quick_test():
    try:
        client = PhantomBusterClient()
        
        print("Lançando job...")
        job_id = client.launch_search("Chile AND finanzas", 5)
        print(f"SUCESSO! Job ID: {job_id}")
        
        return True
    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    quick_test()
