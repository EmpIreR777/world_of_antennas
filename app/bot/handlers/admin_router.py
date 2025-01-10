from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.bot.keyboards.kbs import main_keyboard, admin_keyboard
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