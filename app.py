from video_sender import VideoInfoSender
from utils import Utils
import os



if __name__ == '__main__':

    util = Utils()
    
    config_file = util.readJsonFile("config.json")
    api_config = config_file.get("api")
    host = api_config.get("api_host")
    port = api_config.get("api_port")
    url =  api_config.get("api_url")

    api_url = f"{host}:{port}{url}"

    sender = VideoInfoSender(api_url=url, api_token=config_file.get("api_token"))


    app_config = config_file.get("app")
    # Caminho do arquivo de vídeo no servidor do cliente
    source_path = "C:/Users/dmari/Desktop/home/publico/imagens/"
    videos = os.listdir(source_path)
    # Extrair informações e enviar
    for video in videos:
        video_info = sender.get_video_info(os.path.join(source_path, video))
        # sender.send_video_info(video_info)