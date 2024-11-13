import json
import logging
from datetime import datetime
import ffmpeg
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    
    def process_video_info(self, file_path, camera_dir, date_dir):
        try:
            # Extrair informações do nome do arquivo
            file_name = file_path.name
            channel = int(camera_dir.name[-1])  # Converte 'cameraX' para int X
            video_date = datetime.strptime(file_name[:8], "%Y%m%d").strftime("%Y-%m-%d")
            video_time = f"{file_name[8:10]}:{file_name[10:12]}:00"
            
            # Dados adicionais
            file_size_kb = file_path.stat().st_size / 1024
            video_duration = self.get_video_duration(str(file_path))

            # Montar o dicionário com as informações
            data = {
                "video_file": file_name,
                "channel": channel,
                "data_video": video_date,
                "hora_video": video_time,
                "tamanho": file_size_kb,
                "duracao": str(int(video_duration)),
                "path_arquivo": str(file_path.parent)
            }
            
            return data

        except Exception as e:
            print(f"Erro ao processar o arquivo {file_path}: {e}")
            return None

    def get_list_of_all_videos_info(self, car_path):
        list_of_all_informations = []
        
        try:
            car_path = Path(car_path)
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                
                # Percorrer os diretórios e adicionar as tarefas ao executor
                for camera_dir in car_path.iterdir():
                    if camera_dir.is_dir():
                        for date_dir in camera_dir.iterdir():
                            if date_dir.is_dir():
                                for file_path in date_dir.iterdir():
                                    if file_path.is_file():
                                        futures.append(
                                            executor.submit(self.process_video_info, file_path, camera_dir, date_dir)
                                        )
                
                # Aguardar as tarefas terminarem e coletar os resultados
                for future in as_completed(futures):
                    result = future.result()
                    if result is not None:
                        list_of_all_informations.append(result)

        except Exception as e:
            print(f"Erro ao acessar o diretório {car_path}: {e}")

        finally:
            return list_of_all_informations

    def get_formated_data_to_send(self, car_id: str, empresa_id: int, servidor_id: int, videos_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formata os dados para envio à API.

        Args:
            car_id (str): ID do carro.
            videos_info (List[Dict[str, Any]]): Informações dos vídeos.

        Returns:
            Dict[str, Any]: Dados formatados para envio.
        """
        return {
            "carro": car_id,
            "empresa": empresa_id,
            "servidor": servidor_id,
            "videos": videos_info
        }