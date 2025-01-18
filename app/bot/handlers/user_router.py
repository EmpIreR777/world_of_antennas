import logging
from typing import Union
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.api.dao import UserDAO
from app.bot.keyboards.kbs_user import app_keyboard, home_user_keyboard, main_keyboard
from app.bot.utils.utils import get_back_home_user_text, get_compliments, greet_user, get_about_us_text, send_message_with_delay

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
    await send_message_with_delay(message=message)
    await greet_user(message=message, is_new_user=False)

@router.callback_query(F.data == 'back_about_us')
@router.message(F.text == 'ℹ️ О нас')
async def about_us(event: Union[Message, CallbackQuery]):
    if isinstance(event, CallbackQuery):
        call = event.message
        await send_message_with_delay(message=call)
        await call.delete()  # Удаляем предыдущее сообщение если хотим TODO
        await event.answer(text='Возвращаемся назад')
    else:
        # Если это обычное сообщение
        message = event
        # Можно удалить сообщение пользователя, если нужно
        # await message.delete() # Удаляем предыдущее сообщение если хотим TODO
    await send_message_with_delay(message=message)
    # Отправляем информацию "О нас"
    await message.answer(
        get_about_us_text(),
        reply_markup=app_keyboard()
    )


@router.callback_query(F.data.in_(['Васильева 75', 'Горный Алтайская улица, 26Б']))
async def process_shop_selection(call: CallbackQuery):
    # Удаляем предыдущее сообщение с текстом "О нас" и инлайн кнопками
    # await call.message.delete() # оставить кнопки или удалять? TODO

    if call.data == 'Васильева 75':
        await send_message_with_delay(message=call.message)
        await call.message.edit_text(
            text='Информация о магазине на Васильева 75',
            reply_markup=home_user_keyboard()
        )
    else:
        await send_message_with_delay(message=call.message)
        await call.message.edit_text(
            text='Информация о магазине в Горном',
            reply_markup=home_user_keyboard()
        )


@router.callback_query(F.data == 'user_back_home')
async def cmd_back_home_user(call: CallbackQuery):
    # Удаляем предыдущее сообщение с текстом "О нас" и инлайн кнопками
    await call.answer(f'{await get_compliments()} \n👤{call.from_user.full_name}!')
    await send_message_with_delay(message=call.message)
    await call.message.delete() # Удаляем предыдущее сообщение если хотим TODO
    await call.message.answer(
        get_back_home_user_text(call.from_user.full_name),
        reply_markup=main_keyboard(user_id=call.from_user.id,
                                first_name=call.from_user.first_name)
    )