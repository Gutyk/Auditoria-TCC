from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/tcc_auditoria"
    JWT_SECRET: str = "devsecret"
    JWT_ALG: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
