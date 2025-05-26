from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings

class AppSettings(BaseModel):
    app_name: str
    debug: bool
    env: str

class DatabaseSettings(BaseModel):
    db_login: str
    db_pass: str
    db_host: str
    db_port: str
    db_name: str
    database_url: str

class JwtSettings(BaseModel):
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int

class SmtpSettings(BaseModel):
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    from_email: EmailStr

class MinioSettings(BaseModel):
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket_name: str
    minio_secure: bool

class GoogleSettings(BaseModel):
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

class YandexSettings(BaseModel):
    yandex_client_id: str
    yandex_client_secret: str
    yandex_redirect_uri: str

class Settings(BaseSettings):
    app: AppSettings
    database: DatabaseSettings
    jwt: JwtSettings
    smtp: SmtpSettings
    minio: MinioSettings
    google: GoogleSettings
    yandex: YandexSettings

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"  # allows env vars like APP__NAME


settings = Settings()