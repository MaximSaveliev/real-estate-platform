from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # JWT Settings
    JWT_SECRET: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    SESSION_TOKEN_EXPIRE_DAYS: int
    SESSION_UPDATE_THRESHOLD_DAYS: int
    ISSUER: str

    # Redis Settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str
    REDIS_DB_INDEX: int

    # RabbitMQ Settings
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASS: str

    # User Service URL
    USER_SERVICE_URL: str

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB_INDEX}?password={self.REDIS_PASS}"

    @property
    def RABBITMQ_URL(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()