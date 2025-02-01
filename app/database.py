from decimal import Decimal
import uuid
from sqlalchemy import func, inspect
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import (
    AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
    )

from app.config import settings

# Этот код создает асинхронное подключение к базе данных

engine = create_async_engine(url=settings.get_database_url())
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)



class Base(AsyncAttrs, DeclarativeBase):
    """
    Класс Base будет использоваться для создания моделей таблиц, которые автоматически добавляют поля created_at и updated_at для отслеживания времени создания и обновления записей.
    """
    __abstract__ = True  # Этот класс не будет создавать отдельную таблицу

    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(server_default=func.now(),
                                                onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f'{cls.__name__.lower()}s'

    def to_dict(self, exclude_none: bool = False):
        """
        Преобразует объект модели в словарь.
        Args: exclude_none (bool): Исключать ли None значения из результата
        Returns: dict: Словарь с данными объекта
        """
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)

            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)

            if not exclude_none or value is not None:
                result[column.key] = value

        return result