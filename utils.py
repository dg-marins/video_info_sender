import json
import os
from datetime import datetime
import ffmpeg

class Utils:

    def __init__(self) -> None:
        pass

    def read_config_json_data(self):

        with open("config.json", 'r') as json_file:
            dados = json.load(json_file)

            return dados
        
    def get_video_duration(self, file_path):
        # Extrair a duração do vídeo em segundos
        try:
            file_path = os.path.abspath(file_path)

            probe = ffmpeg.probe(file_path)
            video_duration = float(probe['format']['duration'])  # Duração em segundos
        except ffmpeg.Error as e:
            print(f"Erro ao obter a duração do vídeo: {file_path}", e)
            video_duration = 0  # Define como 0 se houver erro
        except ffmpeg._run.Error as e:
            print(f"Arquivo Corrompido: {file_path}", e)
            video_duration = 0
        finally:
            return video_duration

    def get_empresa_id(self):
        return self.read_config_json_data().get("app").get("empresa_id")
    
    def get_server_id(self):
        return self.read_config_json_data().get("app").get("servidor_id")
    
    def get_list_of_all_videos_info(self, car_path):
        list_of_all_informations = []

        cameras = os.listdir(car_path)
        for camera in cameras:
            camera_dir = os.path.join(car_path, camera)
            if os.path.isdir(camera_dir):
                dates = os.listdir(camera_dir)
                for date in dates:
                    date_dir = os.path.join(camera_dir, date)
                    if os.path.isdir(date_dir):
                        files = os.listdir(date_dir)
                        for file in files:
                            file_path = os.path.join(date_dir, file)
                            file_name = os.path.basename(file_path)
                            channel = camera[-1]
                            video_date = datetime.strptime(file_name[:8], "%Y%m%d").strftime("%Y-%m-%d")
                            video_time = file_name[8:12]
                            video_time = f"{video_time[:2]}:{video_time[2:]}:00"
                            file_size_kb = os.path.getsize(file_path)/1024
                            video_duration = self.get_video_duration(file_path)

                            # Dados fictícios para o exemplo
                            data = {
                                "video_file": file_name,
                                "channel": int(channel),
                                "data_video": video_date,
                                "hora_video": video_time,
                                "tamanho": file_size_kb,
                                "duracao": str(int(video_duration)),
                                "path_arquivo": os.path.dirname(file_path)
                            }
                            
                            list_of_all_informations.append(data)
        
        return list_of_all_informations
    
    def get_formated_data_to_send(self, car_id, videos_data):

        formatter = {   
            "carro": car_id,
            "empresa": self.get_empresa_id(),
            "servidor": self.get_server_id(),
            "videos": videos_data
        }
        
        return formatter