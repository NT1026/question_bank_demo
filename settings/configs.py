import json


class Settings:
    def __init__(self):
        with open("settings/configs.json") as file:
            self.configs = json.load(file)

        self.APP_NAME = self.configs.get("app_name")
        self.HOST = self.configs.get("host")
        self.PORT = self.configs.get("port")
        self.API_KEY = self.configs.get("api_key")
