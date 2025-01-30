import asyncio
import re
import logging
from typing import List, Union
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from sqlalchemy import and_, select

from app.api.dao import ApplicationDAO, ShopDAO, UserDAO
from app.api.models import User
from app.bot.utils.utils import (
    check_user_availability, format_statistics_message, get_hello_admins_text, send_message_with_delay)
from app.database import async_session_maker
from app.bot.keyboards.kbs_user import main_keyboard
from app.bot.keyboards.kbs_admin import admin_keyboard, send_message_keyboard
from app.config import settings


router = Router()


@router.callback_query(F.data == '🔑 Админ панель', F.from_user.id.in_(settings.ADMIN_IDS))
@router.message(F.text == '🔑 Админ панель', F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_panel(event: Union[Message, CallbackQuery]):
    """
    Обрабатывает нажатие кнопки '🔑 Админ панель' callback_query и message.
    """
    if isinstance(event, CallbackQuery):
        call = event
        await send_message_with_delay(message=call.message)
        await call.answer(text='Возвращаемся назад', show_alert=False)
        await call.message.delete() # Удаляем предыдущее сообщение, если нужно TODO
        # Отправляем новое сообщение с информацией для админа
        await call.message.answer(
            text=get_hello_admins_text(user_full_name=call.from_user.full_name),
            reply_markup=admin_keyboard(user_id=call.from_user.id)
        )
    else:
        message = event
        await message.delete() # Удаляем предыдущее сообщение, если нужно TODO
        await send_message_with_delay(message=message)
        # Отправляем новое сообщение с информацией для админа
        await message.answer(
            text=get_hello_admins_text(user_full_name=message.from_user.full_name),
            reply_markup=admin_keyboard(user_id=message.from_user.id)
        )


@router.callback_query(F.data == 'statistic', F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_statistic(call: CallbackQuery):
    """
    Обработчик callback запроса для получения статистики.
    Собирает и отображает статистику по пользователям и заявкам.
    """
    try:
        await call.answer('📊 Собираем статистику...')
        # Создаем отдельные сессии для каждого запроса
        async with async_session_maker() as session:
            stats_people = await UserDAO.get_statistics(session=session)
            stats_app = await ApplicationDAO.get_statistics_applications(session=session)
            shop_app_counts =  await ShopDAO.get_shop_count_app(session=session)
            users = await UserDAO.find_all() # TODO спросить про сессии где лучше

        # Проверка доступности пользователей батчами
        telegram_ids = [user.telegram_id for user in users]
        batch_size = 25
        alive_users = 0
        
        for i in range(0, len(telegram_ids), batch_size):
            batch = telegram_ids[i:i + batch_size]
            check_tasks = [
                check_user_availability(call.message.bot, telegram_id)
                for telegram_id in batch
            ]
            results = await asyncio.gather(*check_tasks, return_exceptions=True)
            alive_users += sum(1 for result in results if isinstance(result, bool) and result)

        not_alive_users = stats_people['total_users'] - alive_users
        # Формируем сообщение со статистикой
        stats_message = format_statistics_message(
            stats_people, 
            stats_app, 
            alive_users, 
            not_alive_users,
            shop_app_counts
        )
        # Отправляем сообщение с задержкой
        await send_message_with_delay(message=call.message)
        await call.message.edit_text(
            text=stats_message,
            reply_markup=admin_keyboard(user_id=call.from_user.id)
        )
    except Exception as e:
        error_msg = f'Ошибка при сборе статистики: {str(e)}'
        logging.error(error_msg, exc_info=True)
        await call.message.answer(
            '❌ Произошла ошибка при сборе статистики. Попробуйте позже.'
        )


@router.callback_query(F.data == 'back_home', F.from_user.id.in_(settings.ADMIN_IDS))
async def cmd_back_home_admin(call: CallbackQuery):
    """
    Обрабатывает нажатие кнопки На главную.
    """
    await send_message_with_delay(message=call.message)
    await call.answer(f'С возвращением, {call.from_user.full_name}!')
    await call.message.answer(
        f'С возвращением, <b>{call.from_user.full_name}</b>!\n\n'
        'Надеемся, что работа в панели администратора была продуктивной. '
        'Если у вас есть предложения по улучшению функционала, '
        'пожалуйста, сообщите нам.\n\n'
        'Чем еще я могу помочь вам сегодня?',
        reply_markup=main_keyboard(user_id=call.from_user.id,
                                first_name=call.from_user.first_name)
    )

# <---------------------------------------start_send_media----------------------------------------->


# Определение состояний
class SendMessage(StatesGroup):
    target = State()  # 'all' или 'roles'
    media_type = State()  # 'text', 'video', 'audio', 'image'
    waiting_for_content = State()


# Обработчик основных кнопок админки
@router.callback_query(
    F.data.in_(['send_all', 'send_roles']),
    F.from_user.id.in_(settings.ADMIN_IDS)
)
async def handle_admin_keyboard_callbacks(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    target = 'all' if data == 'send_all' else 'roles'
    await send_message_with_delay(message=callback.message)
    await callback.message.edit_text(
        'Выберите тип сообщения для отправки :',
        reply_markup=send_message_keyboard(target)
    )
    await state.update_data(target=target)
    await callback.answer()

# Обработчик кнопок выбора типа контента
@router.callback_query(
    F.data.regexp(r'^send_(text|video|audio|image)_(all|roles)$'),
    F.from_user.id.in_(settings.ADMIN_IDS)
)
async def handle_media_type_selection(callback: CallbackQuery, state: FSMContext):
    match = re.match(r'^send_(text|video|audio|image)_(all|roles)$', callback.data)
    await send_message_with_delay(message=callback.message)
    if not match:
        await callback.answer('❗️Некорректные данные.')
        return
    media_type, target = match.groups()
    await state.update_data(media_type=media_type, target=target)

    prompts = {
        'text': '📝 Пожалуйста, отправьте текст, который вы хотите разослать.',
        'video': '🎥 Пожалуйста, отправьте видео, которое вы хотите разослать.',
        'audio': '🎵 Пожалуйста, отправьте аудио, которое вы хотите разослать.',
        'image': '🖼 Пожалуйста, отправьте изображение, которое вы хотите разослать.'
    }
    await callback.message.answer(prompts.get(media_type, '📝 Отправьте сообщение.'))
    await state.set_state(SendMessage.waiting_for_content)
    await callback.answer()


# Обработчик отправки сообщения администратором
@router.message(
    StateFilter(SendMessage.waiting_for_content),
    F.from_user.id.in_(settings.ADMIN_IDS)
)
async def handle_send_message(message: Message, state: FSMContext):
    data = await state.get_data()
    media_type = data.get('media_type')
    target = data.get('target')
    
    async with async_session_maker() as session:
        if target == 'all':
            # Выбираем только пользователей с ролью USER
            stmt = select(User).where(User.role == User.RoleEnum.USER)
        else:  # target == 'roles'
            # Выбираем всех, кроме USER и SUPERUSER
            stmt = select(User).where(
                and_(
                    User.role != User.RoleEnum.USER,
                    User.role != User.RoleEnum.SUPERUSER
                )
            )
        result = await session.execute(stmt)
        users = result.scalars().all()

    failed_users = []
    content = None
    caption = None

    # Проверка соответствия типа контента
    if media_type == 'text':
        if message.text:
            content = message.text
        else:
            await message.answer('❗️Неправильный формат. Пожалуйста, отправьте текстовое сообщение.')
            return  # Не очищаем состояние, чтобы ожидать правильный ввод
    elif media_type == 'video':
        if message.video:
            content = message.video.file_id
        else:
            await message.answer('❗️Неправильный формат. Пожалуйста, отправьте видео.')
            return
    elif media_type == 'audio':
        if message.audio:
            content = message.audio.file_id
        else:
            await message.answer('❗️Неправильный формат. Пожалуйста, отправьте аудио.')
            return
    elif media_type == 'image':
        if message.photo:
            content = message.photo[-1].file_id
            caption = message.caption or ""
        else:
            await message.answer('❗️Неправильный формат. Пожалуйста, отправьте изображение.')
            return
    else:
        await message.answer('❗️Неизвестный тип контента.')
        return

    # Ограничение количества одновременных отправок
    semaphore = asyncio.Semaphore(20)  # Максимум 20 одновременных задач, настройте по необходимости

    async def send_content(user):
        async with semaphore:
            try:
                if media_type == 'text':
                    await send_message_with_delay(message=message)
                    await message.bot.send_message(chat_id=user.telegram_id, text=content)
                elif media_type == 'video':
                    await send_message_with_delay(message=message, action='upload_video')
                    await message.bot.send_video(chat_id=user.telegram_id, video=content)
                elif media_type == 'audio':
                    await send_message_with_delay(message=message, action='upload_audio')
                    await message.bot.send_audio(chat_id=user.telegram_id, audio=content)
                elif media_type == 'image':
                    await send_message_with_delay(message=message, action='upload_photo')
                    await message.bot.send_photo(chat_id=user.telegram_id, photo=content, caption=caption)
            except Exception as e:
                logging.error(f'❌ Не удалось отправить сообщение пользователю {user.telegram_id}: {e}')
                failed_users.append(f'<b>Телеграм ID:</b> {user.telegram_id}, <b>Имя:</b> {user.username}')

    # Создание и запуск задач отправки сообщений
    tasks = [asyncio.create_task(send_content(user)) for user in users]

    # Ограничение общего времени выполнения или использование gather с ограничениями
    await asyncio.gather(*tasks, return_exceptions=True)

    # Формирование ответа администратору
    user_or_role = 'пользователям' if target == "all" else 'работникам'
    if failed_users:
        response = (
            f'✅ Сообщение отправлено всем {user_or_role}, кроме:\n' +
            f'\n'.join(failed_users)
        )
    else:
        response = f'✅ Сообщение успешно отправлено всем {user_or_role}.'
    
    await message.answer(
        response, reply_markup=admin_keyboard(user_id=message.from_user.id))
    await state.clear()

# <-----------------------------------end_send_media------------------------------------>
