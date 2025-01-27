from sqladmin import ModelView
from sqlalchemy.orm import Session
from wtforms import SelectField

from app.api.models import User, Shop, Service, Application, InventoryItem


# Административная панель для модели Пользователь
class UserAdmin(ModelView, model=User):
    # Название модели в единственном числе
    name = 'Пользователь'
    # Название модели во множественном числе
    name_plural = 'Пользователи'
    # Иконка для отображения в интерфейсе
    icon = 'fa fa-users'

    # Метки колонок на русском языке
    column_labels = {
        'telegram_id': 'Telegram ID',
        'username': 'Имя пользователя',
        'first_name': 'Имя',
        'role': 'Роль',
    }

    # Список колонок, отображаемых в таблице пользователей
    column_list = [User.telegram_id, User.username, User.first_name, User.role]

    # Список полей для поиска
    column_searchable_list = [User.username, User.first_name]

    # Список полей для сортировки
    column_sortable_list = [User.telegram_id, User.username, User.role]

    # Фильтры для колонок
    column_filters = [User.role]

    # Исключенные поля из форм создания и редактирования
    form_excluded_columns = ['applications', 'master_applications', 'inventory_items']

    # Разрешения на действия
    can_create = True           # Разрешить создание новых записей
    can_edit = True             # Разрешить редактирование записей
    can_delete = True           # Разрешить удаление записей
    can_view_details = True     # Разрешить просмотр деталей записи

    # Дополнительные настройки
    column_export_exclude_list = ['password']  # Исключить пароль из экспорта
    column_editable_list = ['role']            # Разрешить редактирование поля роли прямо из списка
    detail_columns = column_list               # Колонки для отображения в деталях записи

    # Настройка размера страницы
    page_size = 20

# Административная панель для модели Магазин
class ShopAdmin(ModelView, model=Shop):
    # Название модели в единственном числе
    name = 'Магазин'
    # Название модели во множественном числе
    name_plural = 'Магазины'
    # Иконка для отображения в интерфейсе
    icon = 'fa fa-store'

    # Метки колонок на русском языке
    column_labels = {
        'shop_id': 'ID магазина',
        'address_name': 'Адрес',
        'phone': 'Телефон',
        'working_hours': 'Часы работы',
        'coordinates': 'Координаты',
        'image_url': 'Изображение',
        'services': 'Услуги',
    }

    # Список колонок, отображаемых в таблице магазинов
    column_list = [Shop.shop_id, Shop.address_name, Shop.image_url, Shop.phone, Shop.working_hours]

    # Список полей для поиска
    column_searchable_list = [Shop.address_name]

    # Список полей для сортировки
    column_sortable_list = [Shop.shop_id, Shop.address_name]

    # Поля, отображаемые в формах создания и редактирования
    form_columns = [
        Shop.address_name, 
        Shop.phone,
        Shop.working_hours,
        Shop.coordinates,
        Shop.image_url,
    ]

    # Разрешения на действия
    can_create = True      # Разрешить создание новых записей
    can_edit = True        # Разрешить редактирование записей
    can_delete = True      # Разрешить удаление записей
    can_view_details = True# Разрешить просмотр деталей записи

    # Фильтры для колонок
    column_filters = [Shop.services]

    # Настройка отображения изображений в списке
    # column_formatters = {
    #     Shop.image_url: lambda v, c, m, p: f'<img src="{m.image_url}" width="50" height="50" />'
    # }
    # column_formatters_detail = column_formatters

    # Настройка размера страницы
    page_size = 20

# Административная панель для модели Услуга
class ServiceAdmin(ModelView, model=Service):
    # Название модели в единственном числе
    name = 'Услуга'
    # Название модели во множественном числе
    name_plural = 'Услуги'
    # Иконка для отображения в интерфейсе
    icon = 'fa fa-tools'

    # Метки колонок на русском языке
    column_labels = {
        'service_id': 'ID услуги',
        'service_name': 'Название услуги',
        'description': 'Описание',
    }

    # Список колонок, отображаемых в таблице услуг
    column_list = [Service.service_id, Service.service_name, Service.description]

    # Список полей для поиска
    column_searchable_list = [Service.service_name]

    # Список полей для сортировки
    column_sortable_list = [Service.service_id, Service.service_name]

    # Поля, отображаемые в формах создания и редактирования
    form_columns = [Service.service_name, Service.description]

    # Разрешения на действия
    can_create = True      # Разрешить создание новых записей
    can_edit = True        # Разрешить редактирование записей
    can_delete = True      # Разрешить удаление записей
    can_view_details = True# Разрешить просмотр деталей записи

    # Дополнительные колонки для отображения в деталях записи
    detail_columns = column_list + [Service.shops]

    # Настройка размера страницы
    page_size = 20

# Административная панель для модели Заявка
class ApplicationAdmin(ModelView, model=Application):
    # Название модели в единственном числе
    name = 'Заявка'
    # Название модели во множественном числе
    name_plural = 'Заявки'
    # Иконка для отображения в интерфейсе
    icon = 'fa fa-clipboard-list'

    # Метки колонок на русском языке
    column_labels = {
        'id': 'ID заявки',
        'client_name': 'Имя клиента',
        'appointment_date': 'Дата записи',
        'appointment_time': 'Время записи',
        'status': 'Статус',
        'address': 'Адрес',
        'phone_number': 'Номер телефона',
        'comment': 'Комментарий',
        'shop.address_name': 'Магазин',
        'service.service_name': 'Услуга',
        'user': 'Пользователь',
        'master': 'Мастер',
    }


    # Список колонок, отображаемых в таблице заявок
    column_list = [
        Application.id,
        Application.client_name,
        'shop.address_name',
        'service.service_name',
        Application.status,
        Application.appointment_date,
    ]

    # Переопределяем поле статуса в форме
    # form_overrides = {
    #     'status': SelectField
    # }

    # # Указываем варианты выбора для поля статуса
    # form_args = {
    #     'status': {
    #         'choices': [
    #             (status.name, status.value) for status in Application.StatusEnum
    #         ]
    #     }
    # }

    # Список полей для поиска
    column_searchable_list = [Application.client_name, 'shop.address_name',
        'service.service_name',]

    # Список полей для сортировки
    column_sortable_list = [
        Application.id,
        'shop.name',
        'service.name',
        Application.appointment_date,
        Application.appointment_time
    ]

    # Фильтры для колонок
    column_filters = [
        Application.status,
        Application.appointment_date,
        Application.shop_id,
        Application.service_id
    ]

    form_ajax_refs = {
    'user': {
        'fields': ('username',),  # Поле для отображения в выпадающем списке
        'order_by': 'username',  # Сортировка по username
        'minimum_input_length': 1,  # Минимальное количество символов для поиска
        'page_size': 10  # Количество результатов на странице
    },
    'master': {
        'fields': ('username',),  # Поле для отображения в выпадающем списке
        'order_by': 'username',  # Сортировка по username
        'minimum_input_length': 1,
        'page_size': 10
    }}

    # Исключенные поля из форм создания и редактирования
    # form_excluded_columns = ['user', 'master', 'shop', 'service']

    # Разрешения на действия
    can_create = True      # Разрешить создание новых записей
    can_edit = True        # Разрешить редактирование записей
    can_delete = True      # Разрешить удаление записей
    can_view_details = True# Разрешить просмотр деталей записи

    # Список колонок для отображения в деталях записи
    column_details_list = [
        Application.id,
        Application.client_name,
        Application.address,
        Application.phone_number,
        Application.appointment_date,
        Application.appointment_time,
        Application.status,
        Application.shop_id,
        Application.service_id,
        Application.comment
    ]

    # Настройка отображения статуса с цветовой индикацией
    column_formatters = {
        'status': lambda model, prop: model.status.value
    }

    # Настройка размера страницы
    page_size = 20


# Административная панель для модели Товар
class InventoryItemAdmin(ModelView, model=InventoryItem):
    # Название модели в единственном числе
    name = 'Товар'
    # Название модели во множественном числе
    name_plural = 'Товары'
    # Иконка для отображения в интерфейсе
    icon = 'fa fa-box'

    # Метки колонок на русском языке
    column_labels = {
        'id': 'ID товара',
        'user.username': 'Имя пользователя',
        'item_name': 'Название товара',
        'quantity': 'Количество',
        'unit_type': 'Единица измерения',
        'user_id': 'ID пользователя',
        'comment': 'Комментарий',
    }

    # Список колонок, отображаемых в таблице товаров
    column_list = [
        InventoryItem.id,
        InventoryItem.user,
        InventoryItem.item_name,
        InventoryItem.quantity,
        InventoryItem.unit_type
    ]

    # Список полей для поиска
    column_searchable_list = [InventoryItem.item_name]

    # Список полей для сортировки
    column_sortable_list = [InventoryItem.id, InventoryItem.item_name]

    # Фильтры для колонок
    column_filters = [InventoryItem.unit_type]

    # Поля, отображаемые в формах создания и редактирования
    form_columns = [
        'user',
        'item_name',
        'quantity',
        'unit_type',
        'comment'
    ]

    # AJAX-выбор для пользователя
    form_ajax_refs = {
        'user': {
            'fields': ('username',),  # Поля, которые будут отображаться в выпадающем списке
            'order_by': 'username',  # Сортировка по username
            'minimum_input_length': 1,  # Минимальное количество символов для поиска
            'page_size': 10  # Количество результатов на странице
        }
    }

    # Разрешения на действия
    can_create = True      # Разрешить создание новых записей
    can_edit = True        # Разрешить редактирование записей
    can_delete = True      # Разрешить удаление записей
    can_view_details = True# Разрешить просмотр деталей записи

    # Добавление валидации для количества
    form_args = {
        'quantity': {
            'validators': [
                lambda form, field: field.data >= 0 or 'Количество не может быть отрицательным'
            ],
            'render_kw': {
                'min': 0  # HTML-атрибут для минимального значения
            }
        }
    }

    # Отображение имени пользователя вместо ID
    column_formatters = {
    'user_id': lambda v, c, m, p: m.user.username if m.user else 'Не назначен'
    }

    # Настройка размера страницы
    page_size = 20