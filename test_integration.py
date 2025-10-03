"""
Teste de integração para Demo Agente de Recrutamento
"""
import os
import sys
from datetime import datetime

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("Testando imports...")
    
    try:
        from config import Config
        print("OK - Config importado com sucesso")
        
        from phantom_client import PhantomBusterClient
        print("OK - PhantomBusterClient importado com sucesso")
        
        from sheets_client import GoogleSheetsClient
        print("OK - GoogleSheetsClient importado com sucesso")
        
        from normalizer import DataNormalizer
        print("OK - DataNormalizer importado com sucesso")
        
        from indexer import SemanticIndexer
        print("OK - SemanticIndexer importado com sucesso")
        
        from qa import QASystem
        print("OK - QASystem importado com sucesso")
        
        from audit import AuditLogger
        print("OK - AuditLogger importado com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"ERRO de import: {e}")
        return False

def test_config():
    """Testa configurações"""
    print("\nTestando configuracoes...")
    
    try:
        from config import Config
        
        # Verificar se as variáveis estão definidas
        required_vars = [
            'PHANTOMBUSTER_API_KEY',
            'PHANTOMBUSTER_AGENT_ID', 
            'GOOGLE_SHEETS_ID',
            'GOOGLE_CREDENTIALS_FILE',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(Config, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"ATENCAO: Variaveis em falta: {', '.join(missing_vars)}")
            print("Configure as variaveis de ambiente antes de executar")
            return False
        else:
            print("OK - Todas as configuracoes estao presentes")
            return True
            
    except Exception as e:
        print(f"ERRO na configuracao: {e}")
        return False

def test_normalizer():
    """Testa o normalizador com dados mock"""
    print("\nTestando normalizador...")
    
    try:
        from normalizer import DataNormalizer
        
        # Dados mock
        mock_data = [
            {
                'name': 'Joao Silva',
                'headline': 'Analista Financeiro',
                'location': 'Lisboa',
                'current_company': 'Banco XYZ',
                'education': 'Mestrado em Financas',
                'linkedin_url': 'https://linkedin.com/in/joao-silva',
                'source': 'test'
            },
            {
                'name': 'Maria Santos',
                'headline': 'Marketing Manager',
                'location': 'Porto',
                'current_company': 'Startup ABC',
                'education': 'Licenciatura em Marketing',
                'linkedin_url': 'https://linkedin.com/in/maria-santos',
                'source': 'test'
            }
        ]
        
        normalizer = DataNormalizer()
        normalized = normalizer.normalize_all(mock_data)
        
        print(f"OK - Normalizados {len(normalized)} candidatos")
        
        # Verificar campos adicionados
        for candidate in normalized:
            assert 'summary' in candidate, "Campo 'summary' em falta"
            assert 'skills_tags' in candidate, "Campo 'skills_tags' em falta"
            assert 'ingested_at' in candidate, "Campo 'ingested_at' em falta"
        
        print("OK - Todos os campos obrigatorios foram adicionados")
        return True
        
    except Exception as e:
        print(f"ERRO no normalizador: {e}")
        return False

def test_qa_system():
    """Testa o sistema de QA"""
    print("\nTestando sistema de QA...")
    
    try:
        from qa import QASystem
        
        qa = QASystem()
        
        # Testar análise de intenção
        intent = qa.analyze_query_intent("Quem tem mestrado em financas?")
        print(f"OK - Analise de intencao: {intent['intent_type']}")
        
        # Testar sugestões
        suggestions = qa.generate_search_suggestions()
        print(f"OK - Geradas {len(suggestions)} sugestoes de pesquisa")
        
        return True
        
    except Exception as e:
        print(f"ERRO no sistema de QA: {e}")
        return False

def test_dependencies():
    """Testa se todas as dependências estão instaladas"""
    print("\nTestando dependencias...")
    
    required_packages = [
        'streamlit',
        'google-api-python-client',
        'google-auth',
        'openai',
        'faiss-cpu',
        'numpy',
        'pandas',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"OK - {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"ERRO - {package}")
    
    if missing_packages:
        print(f"\nATENCAO: Pacotes em falta: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False
    else:
        print("OK - Todas as dependencias estao instaladas")
        return True

def main():
    """Executa todos os testes"""
    print("Iniciando testes de integracao...")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_imports,
        test_config,
        test_normalizer,
        test_qa_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"ERRO inesperado em {test.__name__}: {e}")
    
    print("\n" + "=" * 50)
    print(f"Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("SUCESSO! Todos os testes passaram! A aplicacao esta pronta.")
        print("\nPara executar:")
        print("   streamlit run app.py")
    else:
        print("ATENCAO: Alguns testes falharam. Verifique as configuracoes.")
        print("\nConsulte o setup_guide.md para ajuda na configuracao")

if __name__ == "__main__":
    main()
