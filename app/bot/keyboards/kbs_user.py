from aiogram.types import ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.config import settings


def main_keyboard(user_id: int, first_name: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    url_applications = f'{settings.BASE_SITE}/applications?user_id={user_id}'
    url_add_application = f'{settings.BASE_SITE}/form?user_id={user_id}&first_name={first_name}'
    kb.button(text='🌐 Мои заявки', web_app=WebAppInfo(url=url_applications))
    kb.button(text='📝 Оставить заявку', web_app=WebAppInfo(url=url_add_application))
    kb.button(text='ℹ️ О нас')
    if user_id in settings.ADMIN_IDS:
        kb.button(text='🔑 Админ панель')
    kb.adjust(2, 2)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True,
                        input_field_placeholder='Выберите одну из кнопок:')


def back_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='🔙 Назад')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


#-------------------------inline--------------------------

def home_user_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='🏠 На главную', callback_data='user_back_home')
    kb.button(text='🔙 Вернуться назад', callback_data='back_about_us')
    kb.adjust(2)
    return kb.as_markup()


def app_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Магазин в Бийске', callback_data='Бийск Васильева 75')
    kb.button(text='Магазин в Горно-Алтайске', callback_data='Горный Алтайская улица, 26Б')
    kb.button(text='🏠 На главную', callback_data='user_back_home')
    kb.adjust(2, 1)
    return kb.as_markup()