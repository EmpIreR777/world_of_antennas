import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.api.dao import UserDAO
from app.bot.keyboards.kbs_user import app_keyboard, main_keyboard
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
    # Удаляем сообщение пользователя
    await message.delete() # оставить кнопки или удалять? TODO
    # Отправляем информацию "О нас"
    await message.answer(get_about_us_text(), reply_markup=app_keyboard())


@router.callback_query(F.data.in_(['Васильева 75', 'Горный Алтайская улица, 26Б']))
async def process_shop_selection(callback: CallbackQuery):
    # Удаляем предыдущее сообщение с текстом "О нас" и инлайн кнопками
    await callback.message.delete() # оставить кнопки или удалять? TODO
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    # Создаем клавиатуру только с кнопкой "На главную"
    kb = InlineKeyboardBuilder()
    kb.button(text='🏠 На главную', callback_data='user_back_home')

    if callback.data == 'Васильева 75':
        await callback.message.answer(
            text='Информация о магазине на Васильева 75',
            reply_markup=kb.as_markup()
        )
    else:
        await callback.message.answer(
            text='Информация о магазине в Горном',
            reply_markup=kb.as_markup()
        )


@router.callback_query(F.data == 'user_back_home')
async def cmd_back_home_admin(callback: CallbackQuery):
    # Удаляем предыдущее сообщение с текстом "О нас" и инлайн кнопками
    await callback.message.delete() # оставить кнопки или удалять? TODO
    await callback.answer(f'С возвращением, {callback.from_user.full_name}!')
    await callback.message.answer(
        f'С возвращением, <b>{callback.from_user.full_name} </b>! '
        'Надеемся, что вы ознакомились и готовы написать нам или сделать заявку. '
        'Если у вас есть предложения по улучшению функционала, '
        'пожалуйста, сообщите нам. '
        'Чем еще я могу помочь вам сегодня?',
        reply_markup=main_keyboard(user_id=callback.from_user.id,
                                first_name=callback.from_user.first_name)
    )