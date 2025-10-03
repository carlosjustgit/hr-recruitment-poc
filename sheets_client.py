"""
Cliente para integração com Google Sheets API
"""
import json
from typing import List, Dict, Any, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config

class GoogleSheetsClient:
    """Cliente para interagir com Google Sheets API"""
    
    def __init__(self):
        self.sheet_id = Config.GOOGLE_SHEETS_ID
        self.credentials_file = Config.GOOGLE_CREDENTIALS_FILE
        
        if not self.sheet_id or not self.credentials_file:
            raise ValueError("Google Sheets ID e credentials file são obrigatórios")
        
        self.service = self._build_service()
    
    def _build_service(self):
        """Constrói o serviço Google Sheets"""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            return build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            raise Exception(f"Erro ao construir serviço Google Sheets: {e}")
    
    def read_rows(self, worksheet_name: str, range_name: str = None) -> List[Dict[str, Any]]:
        """
        Lê linhas de uma worksheet
        
        Args:
            worksheet_name: Nome da worksheet
            range_name: Range específico (opcional)
            
        Returns:
            Lista de dicionários com os dados
        """
        try:
            if range_name:
                range_str = f"{worksheet_name}!{range_name}"
            else:
                range_str = f"{worksheet_name}!A:Z"
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_str
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return []
            
            # Primeira linha são os headers
            headers = values[0]
            rows = []
            
            for row in values[1:]:
                # Garantir que a linha tem o mesmo número de colunas que os headers
                while len(row) < len(headers):
                    row.append("")
                
                row_dict = dict(zip(headers, row))
                rows.append(row_dict)
            
            return rows
            
        except HttpError as e:
            raise Exception(f"Erro ao ler dados da worksheet {worksheet_name}: {e}")
    
    def write_rows(self, worksheet_name: str, data: List[Dict[str, Any]], 
                   range_name: str = None, clear_first: bool = False) -> bool:
        """
        Escreve dados numa worksheet
        
        Args:
            worksheet_name: Nome da worksheet
            data: Lista de dicionários com os dados
            range_name: Range específico (opcional)
            clear_first: Se deve limpar a worksheet primeiro
            
        Returns:
            True se sucesso
        """
        try:
            if not data:
                return True
            
            # Verificar se a worksheet existe, se não criar
            self._ensure_worksheet_exists(worksheet_name)
            
            # Preparar dados para escrita
            headers = list(data[0].keys())
            values = [headers]  # Primeira linha são os headers
            
            for row in data:
                values.append([str(row.get(header, "")) for header in headers])
            
            # Determinar range
            if range_name:
                range_str = f"{worksheet_name}!{range_name}"
            else:
                range_str = f"{worksheet_name}!A1"
            
            # Limpar worksheet se solicitado
            if clear_first:
                try:
                    self.service.spreadsheets().values().clear(
                        spreadsheetId=self.sheet_id,
                        range=range_str
                    ).execute()
                except HttpError:
                    # Se não conseguir limpar, continua sem limpar
                    pass
            
            # Escrever dados
            body = {'values': values}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=range_str,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            raise Exception(f"Erro ao escrever dados na worksheet {worksheet_name}: {e}")
    
    def _ensure_worksheet_exists(self, worksheet_name: str):
        """Garante que a worksheet existe, criando se necessário"""
        try:
            # Verificar se a worksheet existe
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            existing_sheets = [sheet.get('properties', {}).get('title') for sheet in spreadsheet.get('sheets', [])]
            
            if worksheet_name not in existing_sheets:
                # Criar nova worksheet
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body={
                        'requests': [{
                            'addSheet': {
                                'properties': {
                                    'title': worksheet_name
                                }
                            }
                        }]
                    }
                ).execute()
                
        except Exception as e:
            print(f"Aviso: Não foi possível verificar/criar worksheet {worksheet_name}: {e}")
    
    def append_rows(self, worksheet_name: str, data: List[Dict[str, Any]]) -> bool:
        """
        Adiciona dados ao final de uma worksheet
        
        Args:
            worksheet_name: Nome da worksheet
            data: Lista de dicionários com os dados
            
        Returns:
            True se sucesso
        """
        try:
            if not data:
                return True
            
            # Preparar dados
            headers = list(data[0].keys())
            values = []
            
            for row in data:
                values.append([str(row.get(header, "")) for header in headers])
            
            range_str = f"{worksheet_name}!A:Z"
            body = {'values': values}
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=range_str,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            raise Exception(f"Erro ao adicionar dados à worksheet {worksheet_name}: {e}")
    
    def delete_by_url(self, worksheet_name: str, linkedin_url: str) -> bool:
        """
        Remove uma linha baseada no LinkedIn URL
        
        Args:
            worksheet_name: Nome da worksheet
            linkedin_url: URL do LinkedIn a remover
            
        Returns:
            True se removido com sucesso
        """
        try:
            # Ler dados atuais
            rows = self.read_rows(worksheet_name)
            
            # Encontrar linha com o URL
            row_to_delete = None
            for i, row in enumerate(rows):
                if row.get('linkedin_url') == linkedin_url:
                    row_to_delete = i + 2  # +2 porque começamos em 1 e temos header
                    break
            
            if row_to_delete is None:
                return False
            
            # Remover linha
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id,
                body={
                    'requests': [{
                        'deleteDimension': {
                            'range': {
                                'sheetId': self._get_sheet_id(worksheet_name),
                                'dimension': 'ROWS',
                                'startIndex': row_to_delete - 1,
                                'endIndex': row_to_delete
                            }
                        }
                    }]
                }
            ).execute()
            
            return True
            
        except HttpError as e:
            raise Exception(f"Erro ao remover linha da worksheet {worksheet_name}: {e}")
    
    def _get_sheet_id(self, worksheet_name: str) -> int:
        """Obtém o ID interno da worksheet"""
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            for sheet in spreadsheet.get('sheets', []):
                if sheet.get('properties', {}).get('title') == worksheet_name:
                    return sheet.get('properties', {}).get('sheetId')
            
            raise Exception(f"Worksheet '{worksheet_name}' não encontrada")
            
        except HttpError as e:
            raise Exception(f"Erro ao obter ID da worksheet {worksheet_name}: {e}")
    
    def get_row_count(self, worksheet_name: str) -> int:
        """
        Obtém o número de linhas numa worksheet
        
        Args:
            worksheet_name: Nome da worksheet
            
        Returns:
            Número de linhas
        """
        try:
            range_str = f"{worksheet_name}!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_str
            ).execute()
            
            values = result.get('values', [])
            return len(values) - 1 if values else 0  # -1 para excluir header
            
        except HttpError as e:
            raise Exception(f"Erro ao contar linhas da worksheet {worksheet_name}: {e}")
