import json


class Settings:
    def __init__(self):
        with open("settings/configs.json") as file:
            self.configs = json.load(file)

        # App settings
        self.APP_NAME = self.configs["app"]["name"]
        self.APP_HOST = self.configs["app"]["host"]
        self.APP_PORT = self.configs["app"]["port"]
        self.API_KEY = self.configs["app"]["api_key"]

        # Database settings
        self.DB_HOST = self.configs["mysql"]["host"]
        self.DB_PORT = self.configs["mysql"]["port"]
        self.DB_USER = self.configs["mysql"]["user"]
        self.DB_PASSWORD = self.configs["mysql"]["password"]
        self.DB_NAME = self.configs["mysql"]["db_name"]

        # Session settings
        self.SESSION_SECRET_KEY = self.configs["session"]["secret_key"]
