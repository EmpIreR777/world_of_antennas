from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import (
    AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
    )

# Этот код создает асинхронное подключение к базе данных
database_url = 'sqlite+iosqlite:///db.sqlite3'
engine = create_async_engine(url=database_url)
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