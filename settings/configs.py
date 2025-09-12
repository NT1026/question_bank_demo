import json


class Settings:
    def __init__(self):
        with open("settings/configs.json") as file:
            self.configs = json.load(file)

        # App settings
        self.APP_NAME = self.configs["app"]["name"]
        self.APP_HOST = self.configs["app"]["host"]
        self.APP_PORT = self.configs["app"]["port"]
        
        # Admin settings
        self.ADMIN_USERNAME = self.configs["admin"]["username"]
        self.ADMIN_PASSWORD = self.configs["admin"]["password"]

        # Database settings
        self.DB_HOST = self.configs["mysql"]["host"]
        self.DB_PORT = self.configs["mysql"]["port"]
        self.DB_USER = self.configs["mysql"]["user"]
        self.DB_PASSWORD = self.configs["mysql"]["password"]
        self.DB_NAME = self.configs["mysql"]["db_name"]

        # Secret keys settings
        self.SESSION_SECRET_KEY = self.configs["secret_keys"]["session"]
        self.IMAGE_SECRET_KEY = self.configs["secret_keys"]["image"]

        # Paths settings
        self.PROTECTED_IMG_DIR = self.configs["paths"]["protected_img_dir"]
        self.MATH_DIRNAME = self.configs["paths"]["math_dirname"]
        self.NATURE_SCIENCE_DIRNAME = self.configs["paths"]["nature_science_dirname"]
