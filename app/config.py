import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

ENV_FILE = ".env" if os.getenv("DOCKER_ENV", "").lower() == "true" else ".env.local"
load_dotenv(dotenv_path=ENV_FILE)


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
    HARD_DELETE_USER_DAYS: int = 30
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7일

    # mail
    ADMIN_MAIL: str
    ADMIN_PWD: str

    # test
    TEST_DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",  # .env 파일 경로 지정
        env_file_encoding="utf-8",  # 환경 변수 파일 값을 우선
        # 추가 옵션
        extra="ignore",  # 정의되지 않은 환경 변수 무시
        case_sensitive=True,  # 환경 변수 대소문자 구분
    )


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
    ADMIN_MAIL=os.getenv("ADMIN_MAIL"),
    ADMIN_PWD=os.getenv("ADMIN_PWD"),
    TEST_DATABASE_URL=os.getenv("TEST_DATABASE_URL"),
)
