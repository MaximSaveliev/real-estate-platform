from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AUTH_DATABASE_URL: str
    JWT_SECRET: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str
    REDIS_DB_INDEX: int = 0
    LOOPS_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()