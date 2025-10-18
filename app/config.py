import os
from dotenv import load_dotenv
from .services import access
load_dotenv()

# default key if missing
default_key = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def strippers(data: str) -> list[str]:
    if data:
        return [url.strip() for url in data.split(',')]
    return ["http://localhost:5173"]

class Config:
    BACKEND_ADDRESS = os.environ.get("BACKEND_ADDRESS", "0.0.0.0")
    BACKEND_PORT = os.environ.get("BACKEND_PORT", 5000)
    FLASK_ENVIRONMENT = os.environ.get("FLASK_ENVIRONMENT", 'development')

    # flask server
    FLASK_SECRET_KEY = os.environ.get("SECRET_NI_FLASK", default_key)
    JWT_SECRET_KEY = os.environ.get("SECRET_NI_JWT", default_key)

    # mail server credentials
    MAIL_SERVER_ADDRESS = os.environ.get("MAIL_SERVER_ADDRESS")
    MAIL_SERVER_PORT = os.environ.get("MAIL_SERVER_PORT")
    MAIL_ADDRESS = os.environ.get("MAIL_ADDRESS")
    MAIL_PASSKEY =  os.environ.get("MAIL_PASSKEY")

    # web client
    WEB_CLIENT_HOSTS = strippers(os.environ.get("WEB_CLIENT_HOSTS"))

    access_levels = access.access_level_lookup()

config = Config()
