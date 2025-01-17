import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from sqlalchemy import select

from app.api.dao import ApplicationDAO, UserDAO
from app.api.models import User
from app.bot.utils.utils import send_message_with_delay
from app.database import async_session_maker
from app.bot.keyboards.kbs_user import main_keyboard
from app.bot.keyboards.kbs_admin import admin_keyboard, send_message_keyboard
from app.config import settings

router = Router()


class SendMessage(StatesGroup):
    target = State()  # 'all' or 'roles'
    media_type = State()  # 'text', 'video', 'audio', 'image'
    waiting_for_content = State()


@router.message(F.text == '🔑 Админ панель', F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_panel(message: Message):
    await send_message_with_delay(message=message)
    await message.answer(
        f'Здравствуйте, <b>{message.from_user.full_name}</b>!\n\n'
        'Добро пожаловать в панель администратора. Здесь вы можете:\n'
        '• Просматривать все текущие заявки\n'
        '• Управлять статусами заявок\n'
        '• Анализировать статистику\n\n'
        'Для доступа к полному функционалу, пожалуйста, перейдите по ссылке ниже.\n'
        'Мы постоянно работаем над улучшением и расширением возможностей панели.',
        reply_markup=admin_keyboard(user_id=message.from_user.id)
    )


@router.callback_query(F.data == 'statistic', F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_statistic(call: CallbackQuery):
    await call.answer('📊 Собираем статистику...')
    async with async_session_maker() as session:
        stats_people = await UserDAO.get_statistics(session=session)
        stats_app = await ApplicationDAO.get_statistics_applications(session=session)
        
# all_count_user_in_db = 100  # Например, общее число пользователей  
# for user_id in users:  
#     try:  
#         chat = await bot.get_chat(chat_id=user_id)  
#         alive_users += 1  
#     except TelegramBadRequest as e:  
#         # Пользователь заблокировал бота или чат недоступен  
#         print(f"Ошибка при проверке пользователя {user_id}: {e}")  
#     except Exception as e:  
#         # Обработка других непредвиденных ошибок  
#         print(f"Неожиданная ошибка для пользователя {user_id}: {e}")  

# await message.answer(  
#     f"📊 В базе данных: {all_count_user_in_db} пользователей.\n"  
#     f"✅ Доступны: {alive_users}.\n"  
#     f"🚫 Недоступны: {all_count_user_in_db - alive_users}."  
# )  

    stats_message = (
         '📈 Статистика пользователей и заявок:\n\n'
         f'👥 Всего пользователей: {stats_people["total_users"]} = Заявок: {stats_app["total_app"]}\n'
         f'🆕 Новых пользователей за сегодня: {stats_people["new_today"]} = Заявок: {stats_app["new_today_app"]}\n'
         f'📅 Новых пользователей за неделю: {stats_people["new_week"]} = Заявок: {stats_app["new_week_app"]}\n'
         f'📆 Новых пользователей за месяц: {stats_people["new_month"]} = Заявок: {stats_app["new_month_app"]}\n\n'
         '🕒 Данные актуальны на текущий момент.'
     )
    try:
        await send_message_with_delay(message=call.message)
        await call.message.edit_text(
            text=stats_message, reply_markup=admin_keyboard(user_id=call.from_user.id)
        )
    except Exception:
        pass


@router.callback_query(F.data == 'back_home', F.from_user.id.in_(settings.ADMIN_IDS))
async def cmd_back_home_admin(call: CallbackQuery):
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

# Обработчик основных кнопок админки
@router.callback_query(
    F.data.in_(['send_all', 'send_roles']),
    F.from_user.id.in_(settings.ADMIN_IDS)
)
async def handle_admin_keyboard_callbacks(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    target = 'all' if data == 'send_all' else 'roles'
    await callback.message.edit_text(
        'Выберите тип сообщения для отправки:',
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
    if not match:
        await callback.answer('❗️Некорректные данные.')
        return
    media_type, target = match.groups()
    await state.update_data(media_type=media_type, target=target)

    prompts = {
        'text': '📝 Пожалуйста, отправьте текст, который вы хотите разослать.',
        'video': '🎥 Пожалуйста, отправьте видео, которое вы хотите разослать.',
        'audio': '🎵 Пожалуйста, отправьте аудио, которое вы хотите разослать.',
        'image': '🖼️ Пожалуйста, отправьте изображение, которое вы хотите разослать.'
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
            users = await session.execute(select(User))
        else:  # target == 'roles'
            users = await session.execute(
                select(User).where(User.role != User.RoleEnum.USER)
            )
        users = users.scalars().all()
    
    failed_users = []
    content = None
    caption = None
    
    # Проверка соответствия типа контента
    if media_type == 'text':
        if message.text:
            content = message.text
        else:
            await message.answer('❗️Неправильный формат. Пожалуйста, отправьте **текстовое сообщение**.')
            return  # Не очищаем состояние, чтобы ожидать правильный ввод
    elif media_type == 'video':
        if message.video:
            content = message.video.file_id
        else:
            await message.answer('❗️Неправильный формат. Пожалуйста, отправьте **видео**.')
            return
    elif media_type == 'audio':
        if message.audio:
            content = message.audio.file_id
        else:
            await message.answer('❗️Неправильный формат. Пожалуйста, отправьте **аудио**.')
            return
    elif media_type == 'image':
        if message.photo:
            content = message.photo[-1].file_id  # Наивысшее разрешение
            caption = message.caption or ""
        else:
            await message.answer('❗️Неправильный формат. Пожалуйста, отправьте **изображение**.')
            return
    else:
        await message.answer('❗️Неизвестный тип контента.')
        return
    
    # Функция для отправки контента пользователю
    async def send_content(user):
        if media_type == 'text':
            await message.bot.send_message(chat_id=user.telegram_id, text=content)
        elif media_type == 'video':
            await message.bot.send_video(chat_id=user.telegram_id, video=content)
        elif media_type == 'audio':
            await message.bot.send_audio(chat_id=user.telegram_id, audio=content)
        elif media_type == 'image':
            await message.bot.send_photo(chat_id=user.telegram_id, photo=content, caption=caption)
    
    # Отправка контента всем целевым пользователям
    for user in users:
        try:
            await send_content(user)
        except Exception as e:
            print(f'Не удалось отправить сообщение пользователю {user.telegram_id}: {e}')
            failed_users.append(f'<b>Телеграм ID:</b> {user.telegram_id}, <b>Имя:</b> {user.username}')
    
    # Формирование ответа администратору
    if failed_users:
        response = (
            '✅ Сообщение отправлено всем пользователям, кроме:\n' +
            '\n'.join(failed_users)
        )
    else:
        response = '✅ Сообщение успешно отправлено всем пользователям.'
    
    await message.answer(response, reply_markup=admin_keyboard(user_id=message.from_user.id))
    await state.clear()

# <-----------------------------------------end_send_media----------------------------------------->
