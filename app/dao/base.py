import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import func, update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models import User
from app.database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none_by_id(cls, **kwargs):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.
        Аргументы: data_id: Критерии фильтрации в виде идентификатора записи.
        Возвращает: Экземпляр модели или None, если ничего не найдено.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**kwargs)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.
        Аргументы: **filter_by: Критерии фильтрации в виде именованных параметров.
        Возвращает: Экземпляр модели или None, если ничего не найдено.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by) -> List[User]:
        """
        Асинхронно находит и возвращает все экземпляры модели, удовлетворяющие указанным критериям.
        Аргументы: **filter_by: Критерии фильтрации в виде именованных параметров.
        Возвращает: Список экземпляров модели.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add(cls, **values):
        """
        Асинхронно создает новый экземпляр модели с указанными значениями.
        Аргументы: **values: Именованные параметры для создания нового экземпляра модели.
        Возвращает: Созданный экземпляр модели.
        """
        # Добавить одну запись
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance


    @classmethod
    async def add_many(cls, instances: list[dict]):
        """
        Добавляет несколько записей в базу данных.
        instances: Список словарей, каждый из которых содержит данные для создания нового экземпляра модели.
        return: Список созданных экземпляров модели.
        """
        async with async_session_maker() as session:
            async with session.begin():
                new_instances = [cls.model(**values) for values in instances]
                session.add_all(new_instances)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instances

    @classmethod
    async def update(cls, filter_by, **values):
        """
        Обновляет записи в базе данных по заданным условиям.
        Args: filter_by (dict): Словарь с условиями фильтрации {column_name: value}
        **values: Значения для обновления в формате column_name=value
        Returns: int: Количество обновленных записей
        Raises: SQLAlchemyError: При ошибке обновления данных
        """
        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_update(cls.model)
                    .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
                    .values(**values)
                    .execution_options(synchronize_session='fetch')
                )
                try:
                    result = await session.execute(query)
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount

    @classmethod
    async def delete(cls, delete_all: bool = False, **filter_by):
        """
        Удаляет записи из базы данных на основе заданных критериев фильтрации или удаляет все записи.
        param delete_all: Если True, удаляет все записи в таблице модели.
        param filter_by: Ключевые аргументы, представляющие критерии фильтрации для удаления записей.
        return: Количество удаленных записей.
        raises ValueError: Если не указан ни один фильтр при попытке удалить частично.
        """
        if not delete_all and not filter_by:
            raise ValueError("Нужен хотя бы один фильтр для удаления.")

        async with async_session_maker() as session:
            async with session.begin():
                query = sqlalchemy_delete(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    logging.error(f'Ошибка при удаление записей: {e}')
                    raise e
                return result.rowcount

    @classmethod
    async def paginate(cls, page: int = 1, page_size: int = 10, **filter_by):
        """
        Получение пагинированных записей из базы данных.
        
        :param page: Номер текущей страницы
        :param page_size: Количество записей на странице
        :param filter_by: Фильтры для запроса
        :return: Список записей на текущей странице
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(
                query.offset((page - 1) * page_size).limit(page_size)
            )
            return result.scalars().all()

    @classmethod
    async def count(cls, **filter_by):
        """
        Получение общего количества записей, соответствующих фильтрам.
        
        :param filter_by: Фильтры для запроса
        :return: Общее количество записей
        """
        async with async_session_maker() as session:
            try:
                # Используем func.count() для подсчёта записей
                query = select(func.count()).select_from(cls.model)
                if filter_by:
                    query = query.filter_by(**filter_by)
                result = await session.execute(query)
                return result.scalar_one()  # Возвращаем число, а не None
            except SQLAlchemyError as e:
                logging.error(f'Ошибка при подсчёте записей: {e}')
                return 0  # В случае ошибки возвращаем 0
