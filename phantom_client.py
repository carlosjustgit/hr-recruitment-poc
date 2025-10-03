"""
Cliente para integração com PhantomBuster API
"""
import time
import requests
from typing import Dict, Any, Optional
from config import Config

class PhantomBusterClient:
    """Cliente para interagir com a API do PhantomBuster"""
    
    def __init__(self):
        self.api_key = Config.PHANTOMBUSTER_API_KEY
        self.agent_id = Config.PHANTOMBUSTER_AGENT_ID
        self.base_url = "https://api.phantombuster.com/api/v2"
        
        if not self.api_key or not self.agent_id:
            raise ValueError("PhantomBuster API key e Agent ID são obrigatórios")
    
    def launch_search(self, query: str, limit: int = 100) -> str:
        """
        Lança uma pesquisa no LinkedIn via PhantomBuster
        
        Args:
            query: Query de pesquisa para LinkedIn
            limit: Número máximo de perfis a recolher
            
        Returns:
            job_id: ID do job lançado
        """
        url = f"{self.base_url}/agents/launch"
        
        # Tentar diferentes formatos de payload baseado no tipo de agente
        payloads_to_try = [
            # Formato 1: LinkedIn Profile Scraper
            {
                "id": self.agent_id,
                "argument": {
                    "spreadsheetId": Config.GOOGLE_SHEETS_ID,
                    "numberOfProfiles": limit,
                    "searchQuery": query,
                    "sessionCookie": "",
                    "csvName": "linkedin_profiles"
                }
            },
            # Formato 2: LinkedIn Search Export
            {
                "id": self.agent_id,
                "argument": {
                    "spreadsheetId": Config.GOOGLE_SHEETS_ID,
                    "numberOfProfiles": limit,
                    "searchQuery": query,
                    "sessionCookie": ""
                }
            },
            # Formato 3: Mais simples
            {
                "id": self.agent_id,
                "argument": {
                    "numberOfProfiles": limit,
                    "searchQuery": query
                }
            }
        ]
        
        headers = {
            "X-Phantombuster-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        for i, payload in enumerate(payloads_to_try):
            try:
                print(f"Tentando formato {i+1}...")
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    container_id = data.get("containerId")
                    if container_id:
                        print(f"Sucesso com formato {i+1}")
                        return container_id
                
                print(f"Formato {i+1} falhou: {response.status_code}")
                if i < len(payloads_to_try) - 1:
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"Formato {i+1} erro: {e}")
                if i < len(payloads_to_try) - 1:
                    continue
        
        # Se todos falharam, tentar obter informações do agente
        try:
            agent_info = self.get_agent_info()
            print(f"Informações do agente: {agent_info}")
        except:
            pass
            
        raise Exception(f"Todos os formatos de payload falharam. Verifique o Agent ID: {self.agent_id}")
    
    def poll_status(self, job_id: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Faz poll do status de um job até completar ou timeout
        
        Args:
            job_id: ID do job a monitorizar
            timeout: Timeout em segundos
            
        Returns:
            Dict com status e dados do job
        """
        url = f"{self.base_url}/containers/fetch-output"
        
        headers = {
            "X-Phantombuster-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                params = {"id": job_id}
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") == "finished":
                    return {
                        "status": "succeeded",
                        "data": data.get("data", []),
                        "message": "Job concluído com sucesso"
                    }
                elif data.get("status") == "error":
                    return {
                        "status": "failed",
                        "error": data.get("error", "Erro desconhecido"),
                        "message": "Job falhou"
                    }
                elif data.get("status") in ["running", "queued"]:
                    time.sleep(10)  # Aguarda 10 segundos antes do próximo poll
                    continue
                else:
                    return {
                        "status": "unknown",
                        "message": f"Status desconhecido: {data.get('status')}"
                    }
                    
            except requests.exceptions.RequestException as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "message": "Erro ao fazer poll do job"
                }
        
        return {
            "status": "timeout",
            "message": f"Timeout após {timeout} segundos"
        }
    
    def get_job_info(self, job_id: str) -> Dict[str, Any]:
        """
        Obtém informações sobre um job específico
        
        Args:
            job_id: ID do job
            
        Returns:
            Dict com informações do job
        """
        url = f"{self.base_url}/containers/fetch"
        
        headers = {
            "X-Phantombuster-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            params = {"id": job_id}
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao obter informações do job: {e}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre o agente
        
        Returns:
            Dict com informações do agente
        """
        url = f"{self.base_url}/agents/fetch"
        
        headers = {
            "X-Phantombuster-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            params = {"id": self.agent_id}
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao obter informações do agente: {e}")
