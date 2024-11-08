from consumers import SectransAPI
from utils import Utils
import os


if __name__ == '__main__':

    util = Utils()
    
    config_file = util.read_config_json_data()
    api_config = config_file.get("api")
    host = api_config.get("api_host")
    port = api_config.get("api_port")
    api_url = f"{host}:{port}"

    api_sectrans = SectransAPI(api_url=api_url, api_token=config_file.get("api_token"))

    app_config = config_file.get("app")

    print("Pegando carros na api ...")
    api_cars = api_sectrans.get_cars_by_company_id(app_config.get("servidor_id"))
    
    server_cars = os.listdir(app_config.get("source_video_path"))
    
    cars_to_process = []
    for server_car in server_cars:
        
        api_car_id = None
        for api_car in api_cars:
            if api_car["nome"] == server_car:
                api_car_id = api_car["id"]
        
        if api_car_id is None:
            print(f"ID do carro {server_car} não encontrada")
            continue

        else:
            data = {"id": api_car_id, "name": server_car}
            cars_to_process.append(data)

    for car in cars_to_process:
        car_path = os.path.join(app_config.get("source_video_path"), car["name"])

        print(f'[{car.get("name")}] Iniciando coleta de informações de vídeos.')
        videos_info = util.get_list_of_all_videos_info(os.path.join(app_config["source_video_path"], car["name"]))
        
        formater_send_data = util.get_formated_data_to_send(car["id"], videos_info)
        api_sectrans.send_videos_info(formater_send_data)
        print(f'[{car["name"]}] End')