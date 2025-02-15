import logging
from typing import Union
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile

from app.api.dao import UserDAO, ShopDAO
from app.config import settings
from app.bot.keyboards.kbs_user import app_keyboard, home_user_keyboard, main_keyboard
from app.bot.utils.utils import get_back_home_user_text, get_compliments, greet_user, get_about_us_text, send_message_with_delay

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обрабатывает команду /start.
    """
    logging.info(f'Поиск пользователя с помощью telegram_id: {message.from_user.id}')
    user = await UserDAO.find_one_or_none(telegram_id=message.from_user.id)
    try:
        if not user:
            await UserDAO.add(
                telegram_id=message.from_user.id,
                first_name=message.from_user.first_name,
                username=message.from_user.username
            )
    except Exception as e:
       logging.error(f'Ошибка при добавлении пользователя: {str(e)}')
    await send_message_with_delay(message=message)
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
    """
    Обрабатывает нажатие кнопки 'О нас'.
    """
    if isinstance(event, CallbackQuery):
        # Отправляем новое сообщение вместо редактирования старого
        await event.answer(text='Возвращаемся назад')
        await send_message_with_delay(message=event.message)
        await event.message.answer(
            text=get_about_us_text(),
            reply_markup=app_keyboard()
        )
    else:
        await send_message_with_delay(message=event)
        await event.answer(
            text=get_about_us_text(),
            reply_markup=app_keyboard()
        )


@router.callback_query(F.data.in_(['Бийск Васильева 75', 'Горный Алтайская улица, 26Б']))
async def process_shop_selection(call: CallbackQuery):
    """
    Обрабатывает вывод информации о магазинах 'МИР АНТЕНН'.
    """
    shop_id = 1 if call.data == 'Бийск Васильева 75' else 2

    shop = await ShopDAO.find_one_or_none_by_id(shop_id=shop_id)
    if shop:
        # Формируем ссылку на карту Google
        google_maps_link = f"https://www.google.com/maps/search/?api=1&query={shop.latitude},{shop.longitude}"

        # Формируем текстовое сообщение
        shop_info = (
            f'(﹙˓ 📶 ˒﹚) <a href="https://mir-ant.ru/">МИР АНТЕНН</a> (﹙˓ 📶 ˒﹚)\n'
            f"🏪 <b>Адрес:</b> {shop.address_name}\n"
            f"📞 <b>Телефон:</b> {shop.phone}\n"
            f"⏰ <b>Часы работы:</b> {shop.working_hours}\n"
            f"🗺 <a href='{google_maps_link}'>Открыть на карте</a>"
        )

        # Проверяем, есть ли фото магазина
        if shop.photo:
            # Формируем путь к файлу изображения
            photo_path = settings.STORAGE_IMAGES / shop.photo

            # Отправляем фото с подписью
            await call.message.answer_photo(
                photo=FSInputFile(photo_path),  # Путь к файлу
                caption=shop_info,              # Подпись к фото
                reply_markup=home_user_keyboard(),
                parse_mode="HTML"
            )
        else:
            # Если фото нет, отправляем только текст
            await call.message.edit_text(
                text=shop_info,
                reply_markup=home_user_keyboard(),
                parse_mode="HTML"
            )
    else:
        await call.message.edit_text(
            text="Извините, информация о магазине не найдена.",
            reply_markup=home_user_keyboard()
        )

    await call.answer()


@router.callback_query(F.data == 'user_back_home')
async def cmd_back_home_user(call: CallbackQuery):
    """
    Обрабатывает нажатие кнопки 'На главную'.
    """
    # Удаляем предыдущее сообщение с текстом "О нас" и инлайн кнопками
    await call.answer(f'{await get_compliments()} \n {call.from_user.full_name}👤')
    await send_message_with_delay(message=call.message)
    await call.message.delete() # Удаляем предыдущее сообщение если хотим TODO
    await call.message.answer(
        get_back_home_user_text(call.from_user.full_name),
        reply_markup=main_keyboard(user_id=call.from_user.id,
                                first_name=call.from_user.first_name)
    )