import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    BASE_IP: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"
    API_VERSION: str

    class Config:
        env_file = ".env"


settings = Settings(
    DATABASE_URL=os.getenv("DATABASE_URL"),
    SECRET_KEY=os.getenv("SECRET_KEY"),
    BASE_IP=os.getenv("BASE_IP"),
    API_VERSION=os.getenv("API_VERSION"),
)
