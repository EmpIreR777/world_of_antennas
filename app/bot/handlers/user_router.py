import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.api.dao import UserDAO
from app.bot.keyboards.kbs import app_keyboard
from app.bot.utils.utils import greet_user, get_about_us_text

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обрабатывает команду /start.
    """
    logging.info(f'Searching for user with telegram_id: {message.from_user.id}')

    user = await UserDAO.find_one_or_none(telegram_id=message.from_user.id)
    try:
        if not user:
            await UserDAO.add(
                telegram_id=message.from_user.id,
                first_name=message.from_user.first_name,
                username=message.from_user.username
            )
    except Exception as e:
       logging.error(f'Error adding user: {str(e)}')
    await greet_user(message=message, is_new_user=not user)


@router.message(F.text == '🔙 Назад')
async def cmd_back_home(message: Message) -> None:
    """
    Обрабатывает нажатие кнопки 'Назад'.
    """
    await greet_user(message=message, is_new_user=False)


@router.message(F.text == 'ℹ️ О нас')
async def about_us(message: Message):
    kb = app_keyboard(user_id=message.from_user.id,
                    first_name=message.from_user.first_name)
    await message.answer(get_about_us_text(), reply_markup=kb)