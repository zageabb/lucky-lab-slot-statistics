import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "local-classroom-only")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///lucky_lab.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"check_same_thread": False}}
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "5020"))
