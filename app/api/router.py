from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.api.schemas import AppointmentData
from app.bot.create_bot import bot
from app.api.dao import ApplicationDAO
from app.bot.keyboards.kbs import main_keyboard
from app.config import settings

router = APIRouter(prefix='/api', tags=['API'])


@router.post('/appointment', response_class=JSONResponse)
async def create_appointment(request: Request):

    response = JSONResponse(content={"message": "test"})
    print(f"Response: {response}")
    print(f"Response content: {response.body}")
    print(f"Response headers: {response.headers}")

    print(f"Type: {type(JSONResponse)}")
    print(f"MRO: {JSONResponse.__mro__}")
    print(f"Attributes: {dir(JSONResponse)}")
    print(request)
    try:
        # Получаем и валидируем JSON данные
        data = await request.json()
        validated_data = AppointmentData(**data)

        shop_id, address_name = validated_data.shop.split('_')
        service_id, service_name = validated_data.service.split('_')

        # Формируем сообщение для клиента
        message = (
            f'(﹙˓ 📶 ˒﹚) <a href="https://mir-ant.ru/contacts/">МИР АНТЕНН</a> (﹙˓ 📶 ˒﹚)'
            f'🎉 <b>{validated_data.client_name}, ваша заявка успешно принята!</b>'
            f'💬 <b>Информация о вашей записи:</b>'
            f'👤 <b>Имя клиента:</b> {validated_data.client_name}'
            f'📞 <b>Телефон:</b> {validated_data.phone_number or "Не указан"}'
            f'📍 <b>Адрес:</b> {validated_data.address}'
            f'🏪 <b>Магазин:</b> {address_name}'
            f'🔧 <b>Услуга:</b> {service_name}'
            f'📅 <b>Дата:</b> {validated_data.appointment_date}'
            f'⏰ <b>Время:</b> {validated_data.appointment_time}'
            f'💭 <b>Комментарий:</b> {validated_data.comment or "Нет комментария"}'
            'Спасибо за выбор нашего магазина! ✨ Мы свяжемся с вами для подтверждения.'
        )

        # Сообщение администратору
        admin_message = (
            f'🔔 <b>Новая заявка!</b>'
            f'📄 <b>Детали заявки:</b>'
            f'👤 <b>Имя клиента:</b> {validated_data.client_name}'
            f'📞 <b>Телефон:</b> {validated_data.phone_number or "Не указан"}'
            f'📍 <b>Адрес:</b> {validated_data.address}'
            f'🏪 <b>Магазин:</b> {validated_data.shop}'
            f'🔧 <b>Услуга:</b> {validated_data.service}'
            f'📅 <b>Дата:</b> {validated_data.appointment_date}'
            f'⏰ <b>Время:</b> {validated_data.appointment_time}'
            f'💭 <b>Комментарий:</b> {validated_data.comment or "Нет комментария"}'
            f'📊 <b>Статус:</b> ⚠️ Не обработана'
        )

        # Добавление заявки в базу данных
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

        kb = main_keyboard(user_id=validated_data.user_id, first_name=validated_data.name)
        # Отправка сообщений через бота
        await bot.send_message(chat_id=validated_data.user_id, text=message, reply_markup=kb)
        await bot.send_message(chat_id=settings.ADMIN_ID, text=admin_message, reply_markup=kb)

        return JSONResponse(
            status_code=200,
            content={'message': 'success!'}
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={'error': str(e)}
        )