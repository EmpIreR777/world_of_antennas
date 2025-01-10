from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.dao.base import BaseDAO
from app.api.models import User, Service, Application, Shop
from app.database import async_session_maker


class UserDAO(BaseDAO):
    model = User


class ServiceDAO(BaseDAO):
    model = Service


class ShopDAO(BaseDAO):
    model = Shop


class ApplicationDAO(BaseDAO):
    model = Application

    @classmethod
    async def get_applications_by_user(cls, user_id: int):
        """
        Возвращает все заявки пользователя по user_id с дополнительной информацией
        о магазине и услуге.

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            Список заявок пользователя с именами магазинов и услуг.
        """
        async with async_session_maker() as session:
            try:
                # Используем joinedload для ленивой загрузки связанных объектов
                query = (
                    select(cls.model)
                    .options(joinedload(cls.model.shop), joinedload(cls.model.service))
                    .filter_by(user_id=user_id)
                )
                result = await session.execute(query)
                applications = result.scalars().all()

                # Возвращаем список словарей с нужными полями
                return [
                    {
                        'application_id': app.id,
                        'service_name': app.service.service_name,
                        'address_name': app.shop.address_name,
                        'appointment_date': app.appointment_date,
                        'appointment_time': app.appointment_time,
                        'local': app.local.value,
                        'comment': app.comment,
                        'number': app.phone_number,
                        'is_completed': app.is_completed
                    }
                    for app in applications
                ]
            except SQLAlchemyError as e:
                print(f'Error while fetching applications for user {user_id}: {e}')
                return None

    @classmethod
    async def get_all_applications(cls):
        """
        Возвращает все заявки в базе данных с дополнительной информацией о магазине и услуге.

        Возвращает:
            Список всех заявок с именами магазинов и услуг.
        """
        async with async_session_maker() as session:
            try:
                # Используем joinedload для загрузки связанных данных
                query = (
                    select(cls.model)
                    .options(joinedload(cls.model.shop), joinedload(cls.model.service))
                )
                result = await session.execute(query)
                applications = result.scalars().all()

                # Возвращаем список словарей с нужными полями
                return [
                    {
                        'application_id': app.id,
                        'user_id': app.user_id,
                        'service_name': app.service.service_name,
                        'address_name': app.shop.address_name,
                        'appointment_date': app.appointment_date,
                        'appointment_time': app.appointment_time,
                        'client_name': app.client_name,
                        'local': app.local.value,
                        'comment': app.comment,
                        'number': app.phone_number,
                        'is_completed': app.is_completed
                    }
                    for app in applications
                ]
            except SQLAlchemyError as e:
                print(f'Error while fetching all applications: {e}')
                return None