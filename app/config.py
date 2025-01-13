import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv



env_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..', '.env')

load_dotenv(env_file_path, override=True)

class Settings(BaseSettings):
    BOT_TOKEN: str
    BASE_SITE: str
    ADMIN_IDS: List[int]
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=env_file_path
    )

    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f'{self.BASE_SITE}/webhook'

    def get_database_url(self) -> str:
        """Возвращает путь к базе данных"""
        return self.DATABASE_URL


settings = Settings()