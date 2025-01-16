from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.api.dao import ApplicationDAO, UserDAO
from app.database import async_session_maker
from app.bot.keyboards.kbs_user import main_keyboard
from app.bot.keyboards.kbs_admin import admin_keyboard
from app.config import settings

router = Router()


@router.message(F.text == '🔑 Админ панель', F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_panel(message: Message):
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
    await call.answer('Запрос на получение статистики...')
    await call.answer('📊 Собираем статистику...')
    async with async_session_maker() as session:
        stats_people = await UserDAO.get_statistics(session=session)
        stats_app = await ApplicationDAO.get_statistics_applications(session=session)

    stats_message = (
         '📈 Статистика пользователей и заявок:\n'
         f'👥 Всего пользователей: {stats_people["total_users"]} = Заявок: {stats_app["total_app"]}\n'
         f'🆕 Новых пользователей за сегодня: {stats_people["new_today"]} = Заявок: {stats_app["new_today_app"]}\n'
         f'📅 Новых пользователей за неделю: {stats_people["new_week"]} = Заявок: {stats_app["new_week_app"]}\n'
         f'📆 Новых пользователей за месяц: {stats_people["new_month"]} = Заявок: {stats_app["new_month_app"]}\n'
         '🕒 Данные актуальны на текущий момент.'
     )
    await call.message.edit_text(
        text=stats_message, reply_markup=admin_keyboard(user_id=call.from_user.id)
    )



@router.callback_query(F.data == 'back_home')
async def cmd_back_home_admin(callback: CallbackQuery):
    await callback.answer(f'С возвращением, {callback.from_user.full_name}!')
    await callback.message.answer(
        f'С возвращением, <b>{callback.from_user.full_name}</b>!\n\n'
        'Надеемся, что работа в панели администратора была продуктивной. '
        'Если у вас есть предложения по улучшению функционала, '
        'пожалуйста, сообщите нам.\n\n'
        'Чем еще я могу помочь вам сегодня?',
        reply_markup=main_keyboard(user_id=callback.from_user.id,
                                first_name=callback.from_user.first_name)
    )