import json

class Settings():
    def get():
        config_file = open("settings.json")
        config = json.loads(config_file.read())
        config_file.close()
        return config
