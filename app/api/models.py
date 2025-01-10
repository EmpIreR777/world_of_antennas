import enum
from sqlalchemy import (Boolean, String, BigInteger,
                        Integer, Date, Time, ForeignKey, Enum)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=True)

    # Связь с заявками (один пользователь может иметь несколько заявок)
    applicatioons: Mapped[list['Application']] = relationship(back_populates='users')


class Shop(Base):
    shop_id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                         autoincrement=True)
    address_name: Mapped[str] = mapped_column(String, nullable=False)

    # Связь с заявками (один мастер может иметь несколько заявок)
    applications: Mapped[list['Application']] = relationship(back_populates='shop')


class Service(Base):
    __tablename__ = 'services'

    service_id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                            autoincrement=True)
    service_name: Mapped[str] = mapped_column(String, nullable=False)

    # Связь с заявками (одна услуга может быть частью нескольких заявок)
    applications: Mapped[list['Application']] = relationship(back_populates='service')


class Application(Base):
    class LocalEnum(enum.Enum):
        city = 'Город'
        intercity = 'Межгород'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id'))
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey('shops.shop_id'))
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey('services.service_id'))
    appointment_date: Mapped[Date] = mapped_column(Date, nullable=False)  # Дата заявки
    appointment_time: Mapped[Time] = mapped_column(Time, nullable=False)  # Время заявки
    client_name: Mapped[str] = mapped_column(String, nullable=False)  # Имя пользователя
    local: Mapped[LocalEnum] = mapped_column(Enum(LocalEnum), nullable=False) # Город\межгород
    comment: Mapped[str] = mapped_column(String(255), nullable=True) # Комментарий к заявке
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True) # Номер телефона (необязательное поле)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False) # Статус выполнения заявки (по умолчанию - не выполнена)

    # Связи с пользователем, магазином и услугой
    user: Mapped['User'] = relationship(back_populates='applications')
    shop: Mapped['Shop'] = relationship(back_populates='applications')
    service: Mapped['Service'] = relationship(back_populates='applications')
