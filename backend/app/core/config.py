from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Leitura Estrita e Tipada do Ecossistema (.env).
    Garante integridade Stark para falhar rápido caso as chaves vitais não existam.
    """
    DB_URL: str
    X_TENANT_ID: str
    SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
