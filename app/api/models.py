import enum
from sqlalchemy import Column, String, BigInteger, Integer, Date, Table, \
      Text, Time, ForeignKey, Enum
from sqlalchemy.orm import validates
from sqlalchemy.orm import Mapped, mapped_column, relationship, object_session
from fastapi_storages.integrations.sqlalchemy import FileType

from app.config import settings
from app.database import Base


class User(Base):
    class RoleEnum(enum.StrEnum):
        SUPERUSER = 'Администратор'
        MASTER = 'Мастер'
        OPERATOR = 'Продавец'
        USER = 'Пользователь'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
    # Как создавать 1 пользователя, лучше самому добавить или сделать отдельную урлу для него, чтобы он мог создать суперпользователя себе.

    # Заявки, где пользователь является клиентом
    applications: Mapped[list['Application']] = relationship(
        'Application',
        foreign_keys='Application.user_id',
        back_populates='user'
    )
    # Заявки, где пользователь является мастером
    master_applications: Mapped[list['Application']] = relationship(
        'Application',
        foreign_keys='Application.master_id',
        back_populates='master'
    )
    # Список долга в виде товара перед магазином
    inventory_items: Mapped[list['InventoryItem']] = relationship(
        'InventoryItem',
        back_populates='user'
    )

    @property
    def is_superuser(self) -> bool:
        return self.role == self.RoleEnum.SUPERUSER

    @property
    def is_master(self) -> bool:
        return self.role == self.RoleEnum.MASTER

    @property
    def is_operator(self) -> bool:
        return self.role == self.RoleEnum.OPERATOR

    @property
    def full_name(self) -> str:
        return f'{self.first_name} ({self.username})' if self.first_name and self.username else self.first_name or self.username

    def __repr__(self) -> str:
        return f'Username: {self.username}, telegram_id: {self.telegram_id}'


class InventoryItem(Base):

    class UnitType(enum.StrEnum):
        PIECES = 'шт.' # штуки
        METERS = 'м.' # метры

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_type: Mapped[UnitType] = mapped_column(
        Enum(UnitType), nullable=False
    )
    comment: Mapped[str] = mapped_column(String(200), nullable=True)

    user: Mapped['User'] = relationship('User', back_populates='inventory_items')

    def __repr__(self) -> str:
        return (
            f'Задолженность: id={self.id}, '
            f'Название товара={self.item_name}, '
            f'количество={self.quantity} {self.unit_type.value})'
        )

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity < 0:
            raise ValueError('Количество не может быть отрицательным')
        return quantity


# Вспомогательная таблица для связи многие-ко-многим между Shop и Service
shop_services = Table(
    'shop_services',
    Base.metadata,
    Column('shop_id', Integer, ForeignKey('shops.shop_id'), primary_key=True),
    Column('service_id', Integer, ForeignKey('services.service_id'), primary_key=True)
    )


class Shop(Base):
    shop_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    address_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    working_hours: Mapped[str] = mapped_column(
        String(100), nullable=True)  # Часы работы
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    photo: Mapped[str] = mapped_column(String(255), nullable=True)
    applications: Mapped[list['Application']] = relationship('Application', back_populates='shop')
    # Связь многие-ко-многим с услугами через вспомогательную таблицу
    services: Mapped[list['Service']] = relationship(
        'Service',
        secondary=shop_services,
        back_populates='shops'
    )

    def __repr__(self) -> str:
        return f'Магазин: {self.address_name}'


class Service(Base):
    service_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)  # Описание услуги

    # Связь с заявками (одна услуга может быть частью нескольких заявок)
    applications: Mapped[list['Application']] = relationship('Application', back_populates='service')
    # Связь многие-ко-многим с магазинами через вспомогательную таблицу
    shops: Mapped[list['Shop']] = relationship(
        'Shop',
        secondary=shop_services,
        back_populates='services'
    )

    def __repr__(self) -> str:
        return f'Услуга: {self.service_name}'


class Application(Base):
    class StatusEnum(enum.StrEnum):
        PENDING = 'Не обработана'
        ACCEPTED = 'Принята'
        COMPLETED = 'Выполнена'
        CANCELLED = 'Отменена'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    master_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.telegram_id'), nullable=True)
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey('shops.shop_id'), nullable=False)
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey('services.service_id'), nullable=False)
    appointment_date: Mapped[Date] = mapped_column(Date, nullable=False)  # Дата заявки
    appointment_time: Mapped[Time] = mapped_column(Time, nullable=False)  # Время заявки
    client_name: Mapped[str] = mapped_column(String(50), nullable=False)  # Имя пользователя
    address: Mapped[str] = mapped_column(String(255), nullable=False)  # Адрес
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum), default=StatusEnum.PENDING, nullable=False)
    comment: Mapped[str] = mapped_column(
        String(255), nullable=True)  # Комментарий к заявке
    phone_number: Mapped[str] = mapped_column(
        String(20), nullable=True)  # Номер телефона (необязательное поле)

    # Связи с пользователем, магазином и услугой
    user: Mapped['User'] = relationship(
        'User',
        foreign_keys=[user_id],
        back_populates='applications'
    )
    master: Mapped['User'] = relationship(
        'User',
        foreign_keys=[master_id],
        back_populates='master_applications'
    )
    shop: Mapped['Shop'] = relationship('Shop', back_populates='applications')
    service: Mapped['Service'] = relationship('Service', back_populates='applications')

    @validates('master_id')
    def validate_master(self, key, master_id):
        if master_id is not None:
            session = object_session(self)
            if session is not None:
                master = session.query(User).filter_by(telegram_id=master_id).first()
                if not master:
                    raise ValueError('Назначенный мастер не найден')
                if master.role == User.RoleEnum.USER:
                    raise ValueError('Назначенный пользователь не имеет право')
        return master_id

    def __repr__(self) -> str:
        return f'Заявка: Имя клиента={self.client_name}, статус={self.status})'
