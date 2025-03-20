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
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DATABASE: int

    # fastapi
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7일

    class Config:
        env_file = ".env"


settings = Settings(
    BASE_IP=os.getenv("BASE_IP"),
    API_VERSION=os.getenv("API_VERSION"),
    SECRET_KEY=os.getenv("SECRET_KEY"),
    DATABASE_URL=os.getenv("DATABASE_URL"),
    POSTGRES_USER=os.getenv("POSTGRES_USER"),
    POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD"),
    POSTGRES_DB=os.getenv("POSTGRES_DB"),
    REDIS_HOST=os.getenv("REDIS_HOST"),
    REDIS_PORT=int(os.getenv("REDIS_PORT")),
    REDIS_DATABASE=int(os.getenv("REDIS_DATABASE")),
)
