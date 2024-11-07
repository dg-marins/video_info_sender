import json

class Utils:

    def __init__(self) -> None:
        pass

    def readJsonFile(self, file):

        with open(file, 'r') as json_file:
            dados = json.load(json_file)

            return dados
        
    