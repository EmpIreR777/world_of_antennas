import asyncio
import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.schemas import AppointmentData
from app.bot.create_bot import bot
from app.api.dao import ApplicationDAO, ServiceDAO, ShopDAO
from app.bot.keyboards.kbs_user import main_keyboard
from app.config import settings
from app.bot.utils.utils import send_message_add_user_workers


router = APIRouter(prefix='/api', tags=['API'])


@router.post('/appointment', response_class=JSONResponse)
async def create_appointment(request: Request):
    try:
        data = await request.json()
        print(data)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        validated_data = AppointmentData(**data)

        shop_id = validated_data.shop_id
        service_id = validated_data.service_id
        shop = await ShopDAO.find_one_or_none_by_id(shop_id=shop_id)
        service = await ServiceDAO.find_one_or_none_by_id(service_id=service_id)
        
        user_message = (
            f'(﹙˓ 📶 ˒﹚) <a href="https://mir-ant.ru/">МИР АНТЕНН</a> (﹙˓ 📶 ˒﹚)\n'
            f'🎉 <b>{validated_data.client_name}, ваша заявка успешно принята!</b>\n\n'
            f'💬 <b>Информация о вашей записи:</b>\n'
            f'👤 <b>Имя клиента:</b> {validated_data.client_name}\n'
            f'📞 <b>Телефон:</b> {validated_data.phone_number or "Не указан"}\n'
            f'📍 <b>Адрес:</b> {validated_data.address}\n'
            f'🏪 <b>Магазин:</b> {shop.address_name}\n'
            f'🔧 <b>Услуга:</b> {service.service_name}\n'
            f'📅 <b>Дата:</b> {validated_data.appointment_date}\n'
            f'⏰ <b>Время:</b> {validated_data.appointment_time}\n'
            f'📊 <b>Статус:</b> ⚠️ Не обработана\n'
            f'💭 <b>Комментарий:</b> {validated_data.comment or "Нет комментария"}\n\n'
            'Спасибо за выбор нашего магазина! ✨ Мы свяжемся с вами для подтверждения.\n'
        )

        admin_message = (
            f'🔔 <b>Новая заявка!</b>\n\n'
            f'📄 <b>Детали заявки:</b>\n'
            f'👤 <b>Имя клиента:</b> {validated_data.client_name}\n'
    f'📞 <b>Телефон:</b> <a href="tel:{validated_data.phone_number}">{validated_data.phone_number or "Не указан"}</a>\n'
            f'📍 <b>Адрес:</b> {validated_data.address}\n'
            f'🏪 <b>Магазин:</b> {shop.address_name}\n'
            f'🔧 <b>Услуга:</b> {service.service_name}\n'
            f'📅 <b>Дата:</b> {validated_data.appointment_date}\n'
            f'⏰ <b>Время:</b> {validated_data.appointment_time}\n'
            f'💭 <b>Комментарий:</b> {validated_data.comment or "Нет комментария"}\n'
            f'📊 <b>Статус:</b> ⚠️ Не обработана\n'
        )

        await ApplicationDAO.add(
            user_id=validated_data.user_id,
            shop_id=shop_id,
            service_id=service_id,
            appointment_date=validated_data.appointment_date,
            appointment_time=validated_data.appointment_time,
            client_name=validated_data.client_name,
            phone_number=validated_data.phone_number,
            address=validated_data.address,
            comment=validated_data.comment,
        )

        kb = main_keyboard(user_id=validated_data.user_id, first_name=validated_data.client_name)
        
        # Асинхронная отправка сообщений
        asyncio.create_task(
            send_message_add_user_workers(
                bot=bot,
                chat_id=validated_data.user_id,
                text=user_message,
                delay=5,
            )
        )

        for admin_id in settings.ADMIN_IDS:
            asyncio.create_task(
                send_message_add_user_workers(
                    bot=bot,
                    chat_id=admin_id,
                    text=admin_message,
                    delay=2,
                    latitude=latitude,
                    longitude=longitude
                )
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'message': 'success!'}
        )
    except Exception as e:
        logging.error(f'Error in create_appointment: {e}')
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': 'Internal Server Error', 'detail': str(e)}
        )


