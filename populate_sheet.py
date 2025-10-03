"""
Script para popular a Google Sheet com dados de exemplo do Chile
"""
import os
from sheets_client import GoogleSheetsClient
from config import Config

def populate_sheet():
    """Popula a Google Sheet com dados de exemplo"""
    
    # Dados de exemplo para Chile
    sample_data = [
        {
            'name': 'Carlos Mendoza',
            'headline': 'Analista Financiero Senior',
            'location': 'Santiago, Chile',
            'current_company': 'Banco Santander Chile',
            'education': 'Magíster en Finanzas - Universidad de Chile',
            'linkedin_url': 'https://linkedin.com/in/carlos-mendoza',
            'source': 'demo',
            'ingested_at': '2024-10-03T10:00:00',
            'summary': 'Carlos Mendoza | Analista Financiero Senior | Magíster en Finanzas - Universidad de Chile | Banco Santander Chile | Skills: finanzas, análisis',
            'skills_tags': 'finanzas, análisis'
        },
        {
            'name': 'María González',
            'headline': 'Marketing Manager Digital',
            'location': 'Valparaíso, Chile',
            'current_company': 'StartupTech Chile',
            'education': 'Ingeniería Comercial - PUCV',
            'linkedin_url': 'https://linkedin.com/in/maria-gonzalez',
            'source': 'demo',
            'ingested_at': '2024-10-03T10:00:00',
            'summary': 'María González | Marketing Manager Digital | Ingeniería Comercial - PUCV | StartupTech Chile | Skills: marketing, digital',
            'skills_tags': 'marketing, digital'
        },
        {
            'name': 'Diego Ramírez',
            'headline': 'Data Scientist',
            'location': 'Concepción, Chile',
            'current_company': 'TechCorp Chile',
            'education': 'Ingeniería Informática - Universidad de Concepción',
            'linkedin_url': 'https://linkedin.com/in/diego-ramirez',
            'source': 'demo',
            'ingested_at': '2024-10-03T10:00:00',
            'summary': 'Diego Ramírez | Data Scientist | Ingeniería Informática - Universidad de Concepción | TechCorp Chile | Skills: tecnología, análisis',
            'skills_tags': 'tecnología, análisis'
        },
        {
            'name': 'Ana Herrera',
            'headline': 'Contadora Senior',
            'location': 'Santiago, Chile',
            'current_company': 'EY Chile',
            'education': 'Contador Auditor - Universidad de Chile',
            'linkedin_url': 'https://linkedin.com/in/ana-herrera',
            'source': 'demo',
            'ingested_at': '2024-10-03T10:00:00',
            'summary': 'Ana Herrera | Contadora Senior | Contador Auditor - Universidad de Chile | EY Chile | Skills: contabilidad, auditoría',
            'skills_tags': 'contabilidad, auditoría'
        },
        {
            'name': 'Roberto Silva',
            'headline': 'Ingeniero de Ventas',
            'location': 'Antofagasta, Chile',
            'current_company': 'Minera Escondida',
            'education': 'Ingeniería Industrial - Universidad Católica del Norte',
            'linkedin_url': 'https://linkedin.com/in/roberto-silva',
            'source': 'demo',
            'ingested_at': '2024-10-03T10:00:00',
            'summary': 'Roberto Silva | Ingeniero de Ventas | Ingeniería Industrial - Universidad Católica del Norte | Minera Escondida | Skills: ventas, minería',
            'skills_tags': 'ventas, minería'
        }
    ]
    
    try:
        # Inicializar cliente
        sheets_client = GoogleSheetsClient()
        
        # Escrever dados na sheet
        success = sheets_client.write_rows(
            Config.CANDIDATES_WORKSHEET,
            sample_data,
            clear_first=True
        )
        
        if success:
            print("SUCESSO: Dados de exemplo adicionados a Google Sheet!")
            print(f"DADOS: {len(sample_data)} candidatos chilenos adicionados")
        else:
            print("ERRO: Falha ao adicionar dados a Google Sheet")
            
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    populate_sheet()
