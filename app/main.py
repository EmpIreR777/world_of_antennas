import logging
from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from contextlib import asynccontextmanager

from app.api.admin_panel import ApplicationAdmin, InventoryItemAdmin, \
      ServiceAdmin, ShopAdmin, UserAdmin
from app.database import engine
from app.bot.create_bot import bot, dp, stop_bot, start_bot
from app.bot.handlers.user_router import router as user_router
from app.bot.handlers.admin_router import router as admin_router
from app.pages.user_router import router as user_router_pages
from app.pages.admin_router import router as admin_router_pages
from app.pages.master_inventory_router import router as workers_router_pages
from app.api.utils import router as suggest_address_router
from app.api.router import router as api_router
from app.config import settings


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('Starting bot setup...')
    dp.include_router(user_router)
    dp.include_router(admin_router)

    await start_bot()
    webhook_url = settings.get_webhook_url()
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )
    logging.info(f'Webhook set to {webhook_url}')
    yield
    logging.info('Shutting down bot...')
    await bot.delete_webhook()
    await stop_bot()
    logging.info('Webhook deleted')


app = FastAPI(lifespan=lifespan)

app.mount('/static', StaticFiles(directory='app/static'), name='static')


admin = Admin(app=app, engine=engine)

admin.add_view(UserAdmin)
admin.add_view(ShopAdmin)
admin.add_view(ServiceAdmin)
admin.add_view(ApplicationAdmin)
admin.add_view(InventoryItemAdmin)
admin.title = 'Панель Администратора'




# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/webhook')
async def webhook(request: Request) -> None:
    logging.info('Received webhook request')
    update = Update.model_validate(await request.json(), context={'bot': bot})
    await dp.feed_update(bot, update)
    logging.info('Update processed')

app.include_router(user_router_pages)
app.include_router(admin_router_pages)
app.include_router(workers_router_pages)
app.include_router(suggest_address_router)
app.include_router(api_router)