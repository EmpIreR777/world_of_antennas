from aiogram.types import ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.config import settings


def admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для администратора, отправка медиа всем пользователям и всем работникам.
    """
    url_applications_admin = f'{settings.BASE_SITE}/admin?worker_id={user_id}'
    url_worker_items = f'{settings.BASE_SITE}/worker/worker_list?worker_id={user_id}'
    kb = InlineKeyboardBuilder()
    kb.button(text='📝 Смотреть заявки', web_app=WebAppInfo(url=url_applications_admin))
    kb.button(text='💱 Смотреть задолженности', web_app=WebAppInfo(url=url_worker_items))
    if user_id in settings.ADMIN_IDS:
        kb.button(text='✉️ Отправить всем пользователям', callback_data='send_all')
        kb.button(text='✉️ Отправить всем работникам', callback_data='send_roles')
    kb.button(text='📊 Статистика', callback_data='statistic')
    kb.button(text='🏠 На главную', callback_data='back_home')
    kb.adjust(2, 2, 2)
    return kb.as_markup()


def send_message_keyboard(target: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора отправки медиа.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text='📄 Текст', callback_data=f'send_text_{target}')
    kb.button(text='🎥 Видео', callback_data=f'send_video_{target}')
    kb.button(text='🎵 Аудио', callback_data=f'send_audio_{target}')
    kb.button(text='🖼 Изображение', callback_data=f'send_image_{target}')
    kb.button(text='⬅️ Назад', callback_data='🔑 Админ панель')
    kb.adjust(2)
    return kb.as_markup()


