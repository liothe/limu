import os
import json

class Settings():
    @staticmethod
    def get():
        config_file = open(os.path.abspath(os.path.join(os.path.dirname(__file__), "settings.json")))
        config = json.loads(config_file.read())
        config_file.close()
        return config

    @staticmethod
    def ie():
        print(os.path.abspath(os.path.join(os.path.dirname(__file__), "settings.json")))
