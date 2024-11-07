import requests
import os
from datetime import datetime
import ffmpeg

class VideoInfoSender:
    def __init__(self, api_url, api_token=None):
        self.api_url = api_url
        self.api_token = api_token

    def get_video_info(self, file_path):
        """Extrai as informações do vídeo a partir do arquivo."""
        # Exemplo de extração de dados a partir do nome do arquivo e metadados
        file_name = os.path.basename(file_path)
        file_size_kb = os.path.getsize(file_path)/1024
        video_date = datetime.strptime(file_name[:8], "%Y%m%d").strftime("%Y-%m-%d")
        video_time = file_name[8:12]
        video_time = f"{video_time[:2]}:{video_time[2:]}:00"
        
        # Extrair a duração do vídeo em segundos
        try:
            probe = ffmpeg.probe(file_path)
            video_duration = float(probe['format']['duration'])  # Duração em segundos
        except ffmpeg.Error as e:
            print("Erro ao obter a duração do vídeo:", e)
            video_duration = 0  # Define como 0 se houver erro

        # Dados fictícios para o exemplo
        data = {
            "video_file": file_name,
            "channel": 1,
            "carro": 1,
            "empresa": 1,
            "data_video": video_date,
            "hora_video": video_time,
            "servidor": 1,
            "tamanho": file_size_kb,
            "duracao": str(int(video_duration)),
            "path_arquivo": os.path.dirname(file_path)
        }
        return data

    def send_video_info(self, video_info):
        """Envia as informações do vídeo para a API."""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        try:
            response = requests.post(self.api_url, json=video_info, headers=headers)
            response.raise_for_status()
            print("Informações enviadas com sucesso:", response.json())
        except requests.exceptions.RequestException as e:
            print("Erro ao enviar dados para a API:", e)