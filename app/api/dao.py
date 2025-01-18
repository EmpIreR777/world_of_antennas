from datetime import datetime, UTC, timedelta
import logging
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func, case
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base import BaseDAO
from app.api.models import User, Service, Application, Shop
from app.database import async_session_maker


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def get_statistics(cls, session: AsyncSession):
        """
        Метод собирает данные о количестве пользователей,
        зарегистрированных за различные временные периоды.
        """
        try:
            now = datetime.now(UTC)
            query = select(
                func.count().label('total_users'),
                func.sum(case((cls.model.create_at >= now - timedelta(days=1), 1), else_=0)).label('new_today'),
                func.sum(case((cls.model.create_at >= now - timedelta(days=7), 1), else_=0)).label('new_week'),
                func.sum(case((cls.model.create_at >= now - timedelta(days=30), 1), else_=0)).label('new_month')
            )

            result = await session.execute(query)
            stats = result.fetchone()

            statistics = {
                'total_users': stats.total_users,
                'new_today': stats.new_today,
                'new_week': stats.new_week,
                'new_month': stats.new_month
            }

            logging.info(f'Статистика успешно получена: {statistics}')
            return statistics
        except SQLAlchemyError as e:
            logging.error(f'Ошибка при получении статистики: {e}')
            raise


class ServiceDAO(BaseDAO):
    model = Service


class ShopDAO(BaseDAO):
    model = Shop


class ApplicationDAO(BaseDAO):
    model = Application


    @classmethod
    async def get_statistics_applications(cls, session: AsyncSession):
        """
        Метод собирает данные о количестве пользователей,
        зарегистрированных за различные временные периоды.
        """
        try:
            now = datetime.now(UTC)
            query = select(
                func.count().label('total_app'),
                func.sum(case((cls.model.create_at >= now - timedelta(days=1), 1), else_=0)).label('new_today_app'),
                func.sum(case((cls.model.create_at >= now - timedelta(days=7), 1), else_=0)).label('new_week_app'),
                func.sum(case((cls.model.create_at >= now - timedelta(days=30), 1), else_=0)).label('new_month_app')
            )

            result = await session.execute(query)
            stats = result.fetchone()

            statistics = {
                'total_app': stats.total_app,
                'new_today_app': stats.new_today_app,
                'new_week_app': stats.new_week_app,
                'new_month_app': stats.new_month_app
            }

            logging.info(f'Статистика успешно получена: {statistics}')
            return statistics
        except SQLAlchemyError as e:
            logging.error(f'Ошибка при получении статистики: {e}')
            raise


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
                        'status': app.status.value,
                        'comment': app.comment,
                        'phone_number': app.phone_number,
                        'address': app.address,
                    }
                    for app in applications
                ]
            except SQLAlchemyError as e:
                logging.error(f'Ошибка при выборке приложений для пользователя {user_id}: {e}')
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
                        'appointment_date': app.appointment_date.strftime('%Y-%m-%d'),
                        'appointment_time': app.appointment_time.strftime('%H:%M'),
                        'client_name': app.client_name,
                        'status': app.status.value,
                        'comment': app.comment,
                        'phone_number': app.phone_number,
                        'address': app.address,
                    }
                    for app in applications
                ]
            except SQLAlchemyError as e:
                logging.error(f'Ошибка при загрузке всех приложений: {e}')
                return None