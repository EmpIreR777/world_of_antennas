from aiogram.types import ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.config import settings


def admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    url_applications = f'{settings.BASE_SITE}/admin?ADMIN_IDS={user_id}'
    kb = InlineKeyboardBuilder()
    kb.button(text='🏠 На главную', callback_data='back_home')
    kb.button(text='📝 Смотреть заявки', web_app=WebAppInfo(url=url_applications))
    kb.button(text='📊 Статистика', callback_data='statistic')
    kb.adjust(1)
    return kb.as_markup()