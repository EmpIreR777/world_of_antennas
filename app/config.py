import os
from pathlib import Path
from typing import List
from fastapi_storages import FileSystemStorage
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
    YANDEX_API_KEY: str

    BASE_DIR: Path = Path(__file__).resolve().parent

    STORAGE_IMAGES: Path = BASE_DIR / 'media/images'
    STORAGES: dict = {}

    model_config = SettingsConfigDict(
        env_file=env_file_path
    )

    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f'{self.BASE_SITE}/webhook'

    def get_database_url(self) -> str:
        """Возвращает путь к базе данных"""
        return self.DATABASE_URL

    def get_key_yandex_geo(self) -> str:
        """Возвращает токен Геокодер яндекс. https://developer.tech.yandex.ru/services"""
        return self.YANDEX_API_KEY

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories_exist(
            self.STORAGE_IMAGES,)
        self.STORAGES['image'] = FileSystemStorage(path=self.STORAGE_IMAGES)

    @staticmethod
    def _ensure_directories_exist(*paths: Path):
        """Создаёт директории, если их не существует."""
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)

settings = Settings()