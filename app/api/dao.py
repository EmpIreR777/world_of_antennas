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
    async def get_all_items_worker_list(cls):
        """
        Возвращает всех пользователей, кроме роли User, и их предметы, 
        которые они записали на себя.
        """
        async with async_session_maker() as session:
            try:
                query = (
                    select(cls.model)
                    .options(joinedload(cls.model.inventory_items))
                    .where(cls.model.role != cls.model.RoleEnum.USER)
                )
                result = await session.execute(query)
                users = result.unique().scalars().all()  # добавлен unique()
                
                if not users:
                    return []
                return [
                    {
                        'first_name': user.first_name,
                        'username': user.username,
                        'role': user.role.value,
                        'inventory_items': [
                            {
                                'item_name': item.item_name,
                                'quantity': item.quantity,
                                'unit_type': item.unit_type.value,
                                'comment': item.comment,
                            }
                            for item in user.inventory_items
                        ]
                    }
                    for user in users
                ]
            except SQLAlchemyError as e:
                logging.error(f'Ошибка при загрузке всех работников: {e}')
                raise  # выбрасываем ошибку вместо возврата None

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


# class InventoryItemDAO(BaseDAO):
#     model = InventoryItem




class ServiceDAO(BaseDAO):
    model = Service


class ShopDAO(BaseDAO):
    model = Shop

    @classmethod
    async def get_shop_count_app(cls, session: AsyncSession):
        """
        Метод для получения списка магазинов вместе с количеством их заявок.
        """
        try:
            query = select(
                cls.model.address_name, func.count(Application.id).label(
                    'application_count')).outerjoin(
                    Application, Shop.shop_id == Application.shop_id).group_by(Shop.address_name)
            results = await session.execute(query)
            logging.info(f'Статистика успешно получена: {results}')
            return results.all()
        except SQLAlchemyError as e:
            logging.error(f'Ошибка при получении статистики: {e}')
            raise


class ApplicationDAO(BaseDAO):
    model = Application


    @classmethod
    async def get_statistics_applications(cls, session: AsyncSession):
        """
        Метод собирает данные о количестве заявок,
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
                    .options(joinedload(cls.model.shop),
                            joinedload(cls.model.service),
                            joinedload(cls.model.master)
                            )
                    .filter_by(user_id=user_id)
                )
                result = await session.execute(query)
                applications = result.scalars().all()

                # Возвращаем список словарей с нужными полями
                return [
                    {
                        'application_id': app.id,
                        'client_name': app.client_name,
                        'service_name': app.service.service_name,
                        'address_name': app.shop.address_name,
                        'appointment_date': app.appointment_date.strftime('%Y-%m-%d'),
                        'appointment_time': app.appointment_time.strftime('%H:%M'),
                        'status': app.status.value,
                        'comment': app.comment,
                        'phone_number': app.phone_number,
                        'address': app.address,
                        'master_name': app.master.first_name if app.master else 'Мастер не назначен',
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
                    .options(joinedload(cls.model.shop),
                            joinedload(cls.model.service),
                            joinedload(cls.model.master)
                            )
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
                        'master_name': app.master.first_name if app.master else 'Мастер не назначен',
                    }
                    for app in applications
                ]
            except SQLAlchemyError as e:
                logging.error(f'Ошибка при загрузке всех приложений: {e}')
                return None