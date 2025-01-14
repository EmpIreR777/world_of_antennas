import enum
from sqlalchemy import Column, String, BigInteger, Integer, Date, Table, \
      Text, Time, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    class RoleEnum(enum.Enum):
        SUPERUSER = 'superuser'
        MASTER = 'master'
        OPERATOR = 'operator'
        USER = 'user'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
    # как создавать 1 пользователя, лучше самому добавить или сделать отдельную урлу для него, что бы он мог создать суперпользователя себе

    # Связь с заявками (один пользователь может иметь несколько заявок)
    applications: Mapped[list['Application']] = relationship(back_populates='user')

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
        return f'{self.first_name} ({self.username})' if self.first_name else self.username

    def __repr__(self) -> str:
        return f'User(telegram_id={self.telegram_id}, username={self.username})'


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
    coordinates: Mapped[str] = mapped_column(
        String(50), nullable=True)  # Координаты для карты
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)

    # Связь с заявками (один мастер может иметь несколько заявок)
    applications: Mapped[list['Application']] = relationship(back_populates='shop')
    # Связь многие-ко-многим с услугами через вспомогательную таблицу
    services = relationship(
        'Service',
        secondary=shop_services,
        back_populates='shops'
    )

    def __repr__(self) -> str:
        return f'Shop(address_name={self.address_name})'


class Service(Base):
    service_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)  # Описание услуги

    # Связь с заявками (одна услуга может быть частью нескольких заявок)
    applications: Mapped[list['Application']] = relationship(back_populates='service')
    # Связь многие-ко-многим с магазинами через вспомогательную таблицу
    shops = relationship(
        'Shop',
        secondary=shop_services,
        back_populates='services'
    )

    def __repr__(self) -> str:
        return f'Service(service_name={self.service_name})'


class Application(Base):
    class StatusEnum(enum.Enum):
        pending = 'Не обработана'
        accepted = 'Принята'
        completed = 'Выполнена'
        cancelled = 'Отменена'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id'))
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey('shops.shop_id'))
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey('services.service_id'))
    appointment_date: Mapped[Date] = mapped_column(Date, nullable=False)  # Дата заявки
    appointment_time: Mapped[Time] = mapped_column(Time, nullable=False)  # Время заявки
    client_name: Mapped[str] = mapped_column(String(50), nullable=False)  # Имя пользователя
    address: Mapped[str] = mapped_column(String(255), nullable=False)  # Адрес
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum), default=StatusEnum.pending, nullable=False)
    comment: Mapped[str] = mapped_column(
        String(255), nullable=True)  # Комментарий к заявке
    phone_number: Mapped[str] = mapped_column(
        String(20), nullable=True)  # Номер телефона (необязательное поле)

    # Связи с пользователем, магазином и услугой
    user: Mapped['User'] = relationship(back_populates='applications')
    shop: Mapped['Shop'] = relationship(back_populates='applications')
    service: Mapped['Service'] = relationship(back_populates='applications')

    def __repr__(self) -> str:
        return f'Application(client_name={self.client_name}, status={self.status})'
