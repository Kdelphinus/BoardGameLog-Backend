import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # app
    BASE_IP: str
    API_VERSION: str
    SECRET_KEY: str

    # db
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # redis
    REDIS_URL: str

    # fastapi
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"


settings = Settings(
    DATABASE_URL=os.getenv("DATABASE_URL"),
    SECRET_KEY=os.getenv("SECRET_KEY"),
    BASE_IP=os.getenv("BASE_IP"),
    API_VERSION=os.getenv("API_VERSION"),
)
