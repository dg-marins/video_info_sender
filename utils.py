import json
import logging
from datetime import datetime
import ffmpeg
from pathlib import Path
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)

class VideoDurationError(Exception):
    """Exceção personalizada para erros ao obter a duração do vídeo."""
    pass

class Utils:
    def __init__(self, config_path: str = "config.json") -> None:
        self.config_path = Path(config_path)
        self.cache_duration = {}

    def read_config_json_data(self) -> Dict[str, Any]:
        """Lê os dados do arquivo de configuração JSON.

        Returns:
            Dict[str, Any]: Dados da configuração.
        """
        with self.config_path.open('r') as json_file:
            data = json.load(json_file)
            return data
        
    def get_video_duration(self, file_path: str) -> float:
        """Extrai a duração do vídeo em segundos.

        Args:
            file_path (str): Caminho para o arquivo de vídeo.

        Returns:
            float: Duração do vídeo em segundos.

        Raises:
            VideoDurationError: Se houver um erro ao obter a duração.
        """
        if file_path in self.cache_duration:
            return self.cache_duration[file_path]

        try:
            file_path = Path(file_path).resolve()
            probe = ffmpeg.probe(str(file_path))
            video_duration = float(probe['format']['duration'])  # Duração em segundos
            self.cache_duration[file_path] = video_duration
        except ffmpeg.Error as e:
            logging.error(f"Erro ao obter a duração do vídeo: {file_path}", exc_info=e)
            raise VideoDurationError(f"Erro ao obter a duração do vídeo: {file_path}") from e
        except ffmpeg._run.Error as e:
            logging.error(f"Arquivo Corrompido: {file_path}", exc_info=e)
            raise VideoDurationError(f"Arquivo Corrompido: {file_path}") from e
        return video_duration

    def get_company_id(self) -> str:
        """Retorna o ID da empresa do arquivo de configuração.

        Returns:
            str: ID da empresa.
        """
        return self.read_config_json_data().get("app").get("empresa_id")
    
    def get_server_id(self) -> str:
        """Retorna o ID do servidor do arquivo de configuração.

        Returns:
            str: ID do servidor.
        """
        return self.read_config_json_data().get("app").get("servidor_id")
    
    def get_list_of_all_videos_info(self, car_path: str) -> List[Dict[str, Any]]:
        """Coleta informações de todos os vídeos em um diretório específico.

        Args:
            car_path (str): Caminho para o diretório do carro.

        Returns:
            List[Dict[str, Any]]: Lista de dicionários contendo informações dos vídeos.
        """
        car_path = Path(car_path)
        videos_info = []
        
        for video_file in car_path.glob("*.mp4"):  # Supondo que os vídeos sejam .mp4
            duration = self.get_video_duration(video_file)
            videos_info.append({
                "name": video_file.name,
                "duration": duration,
                "path": str(video_file)
            })
        
        return videos_info

    def get_formated_data_to_send(self, car_id: str, videos_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formata os dados para envio à API.

        Args:
            car_id (str): ID do carro.
            videos_info (List[Dict[str, Any]]): Informações dos vídeos.

        Returns:
            Dict[str, Any]: Dados formatados para envio.
        """
        return {
            "car_id": car_id,
            "videos": videos_info
        }