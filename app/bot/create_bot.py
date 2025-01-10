from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings


bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))
dp = Dispatcher()

admins = settings.ADMIN_IDS

async def start_bot():
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Я запущен 🥳')
        except:
            pass


async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен 😔')
    except:
        pass