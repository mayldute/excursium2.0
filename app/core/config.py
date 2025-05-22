from pydantic_settings import BaseSettings
from pydantic import EmailStr

class Settings(BaseSettings):
    # App settings
    APP_NAME: str
    DEBUG: bool
    ENV: str

    # Database settings
    DB_LOGIN: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DATABASE_URL: str

    # JWT settings
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # SMTP (email) settings
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    FROM_EMAIL: EmailStr

    # Minio settings
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_SECURE: bool

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()