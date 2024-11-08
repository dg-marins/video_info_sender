import requests
from utils import Utils

class SectransAPI:
    def __init__(self, api_url, api_token=None):
        self.api_url = api_url
        self.api_token = api_token

    def get_cars_by_company_id(self, company_id):
        endpoint = f"/api/list_cars/{company_id}"

        headers = {
            "Content-Type": "application/json"
        }
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        try:
            response = requests.get(self.api_url+endpoint)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print("Erro ao pegar carros na API:", e)
            return None

    def send_videos_info(self, data_to_send):
        """Envia as informações do vídeo para a API."""
        
        endpoint = "/api/videos/register/"
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        try:
            response = requests.post(self.api_url+endpoint, json=data_to_send, headers=headers)
            response.raise_for_status()
            print("Informações enviadas com sucesso:", response.json())
        except requests.exceptions.RequestException as e:
            print("Erro ao enviar dados para a API:", e)