from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, time
from app.database import Base
from app.api.models import User, InventoryItem, Shop, Service, Application

# Подключение к базе данных
DATABASE_URL = 'sqlite:///db.sqlite3'  # Укажите вашу базу данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Создание сессии
db = SessionLocal()

# Добавление пользователей
users = [
    User(telegram_id=123456789, first_name="Иван", username="ivan123", role=User.RoleEnum.USER),
    User(telegram_id=987654321, first_name="Мария", username="maria456", role=User.RoleEnum.OPERATOR),
    User(telegram_id=555555555, first_name="Алексей", username="alex789", role=User.RoleEnum.MASTER),
    User(telegram_id=111111111, first_name="Админ", username="admin", role=User.RoleEnum.SUPERUSER),
    User(telegram_id=999999999, first_name="Петр", username="peter321", role=User.RoleEnum.USER),
]
db.add_all(users)
db.commit()

# Добавление магазинов
shops = [
    Shop(
        address_name="Васильево 75",
        phone="+79998887766",
        working_hours="09:00-18:00",
        latitude=55.7558,
        longitude=37.6176,
        photo=None,
    ),
    Shop(
        address_name="Горно-Алтайск",
        phone="+79997776655",
        working_hours="10:00-19:00",
        latitude=51.9581,
        longitude=85.9603,
        photo=None,
    ),
]

db.add_all(shops)
db.commit()

# Добавление услуг
services = [
    Service(service_name="Установка антенны", description="Установка и настройка спутниковой антенны"),
    Service(service_name="Ремонт антенны", description="Ремонт и замена компонентов антенны"),
    Service(service_name="Консультация по антеннам", description="Консультация по выбору и эксплуатации антенн"),
    Service(service_name="Диагностика антенны", description="Проверка и диагностика работы антенны"),
    Service(service_name="Замена кабеля", description="Замена кабеля антенны"),
]
db.add_all(services)
db.commit()

# Связь магазинов и услуг
shops[0].services.extend(services[:3])  # Васильево 75 предлагает первые 3 услуги
shops[1].services.extend(services[2:])  # Горно-Алтайск предлагает последние 3 услуги
db.commit()

# Добавление заявок
applications = [
    Application(
        user_id=123456789,
        shop_id=shops[0].shop_id,
        service_id=services[0].service_id,
        appointment_date=date(2023, 10, 1),
        appointment_time=time(10, 0),
        client_name="Иван",
        address="Васильево 75",
        status=Application.StatusEnum.PENDING,
        comment="Нужна установка антенны на крыше",
    ),
    Application(
        user_id=987654321,
        shop_id=shops[1].shop_id,
        service_id=services[1].service_id,
        appointment_date=date(2023, 10, 2),
        appointment_time=time(11, 0),
        client_name="Мария",
        address="Горно-Алтайск",
        status=Application.StatusEnum.ACCEPTED,
        comment="Ремонт антенны после шторма",
    ),
    Application(
        user_id=555555555,
        shop_id=shops[0].shop_id,
        service_id=services[2].service_id,
        appointment_date=date(2023, 10, 3),
        appointment_time=time(12, 0),
        client_name="Алексей",
        address="Васильево 75",
        status=Application.StatusEnum.COMPLETED,
        comment="Консультация по выбору антенны",
    ),
    Application(
        user_id=111111111,
        shop_id=shops[1].shop_id,
        service_id=services[3].service_id,
        appointment_date=date(2023, 10, 4),
        appointment_time=time(13, 0),
        client_name="Админ",
        address="Горно-Алтайск",
        status=Application.StatusEnum.CANCELLED,
        comment="Диагностика антенны",
    ),
    Application(
        user_id=999999999,
        shop_id=shops[0].shop_id,
        service_id=services[4].service_id,
        appointment_date=date(2023, 10, 5),
        appointment_time=time(14, 0),
        client_name="Петр",
        address="Васильево 75",
        status=Application.StatusEnum.PENDING,
        comment="Замена кабеля антенны",
    ),
]
db.add_all(applications)
db.commit()

# Добавление задолженностей
inventory_items = [
    InventoryItem(
        user_id=123456789,
        item_name="Кабель антенный",
        quantity=5,
        unit_type=InventoryItem.UnitType.METERS,
        comment="Для установки антенны",
    ),
    InventoryItem(
        user_id=987654321,
        item_name="Крепление антенны",
        quantity=2,
        unit_type=InventoryItem.UnitType.PIECES,
        comment="Для ремонта антенны",
    ),
    InventoryItem(
        user_id=555555555,
        item_name="Антенна спутниковая",
        quantity=1,
        unit_type=InventoryItem.UnitType.PIECES,
        comment="Для замены",
    ),
    InventoryItem(
        user_id=111111111,
        item_name="Переходник",
        quantity=3,
        unit_type=InventoryItem.UnitType.PIECES,
        comment="Для диагностики",
    ),
    InventoryItem(
        user_id=999999999,
        item_name="Кабель HDMI",
        quantity=1,
        unit_type=InventoryItem.UnitType.METERS,
        comment="Для замены кабеля",
    ),
]
db.add_all(inventory_items)
db.commit()

# Закрытие сессии
db.close()

print("База данных успешно заполнена тестовыми данными!")