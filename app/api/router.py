from aiohttp import request
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.api.models import Application, User
from app.api.schemas import AppointmentData
from app.bot.create_bot import bot
from app.api.dao import ApplicationDAO
from app.bot.keyboards.kbs_user import main_keyboard
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

@router.post('/api/update-application-status', response_class=JSONResponse)
async def update_application_status(
    data: dict,
    current_user: User =  select(User).where(User.role == User.RoleEnum.USER)
):
    if current_user.role == User.RoleEnum.USER:
        return JSONResponse(
            status_code=403,
            content={'success': False, 'message': 'Недостаточно прав'}
        )
    try:
        application_id = int(data.get('application_id'))
        new_status = data.get('status')

        if not application_id or not new_status:
            return JSONResponse(
                status_code=400,
                content={'success': False, 'message': 'Неверные параметры запроса'}
            )
        # Проверяем существует ли такой статус
        try:
            status_enum = Application.StatusEnum(new_status)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={'success': False, 'message': 'Некорректный статус'}
            )
        # Обновление статуса и master_id заявки
        rows_updated = await ApplicationDAO.update(
            filter_by={'id': application_id},
            status=status_enum,
            master_id=current_user.telegram_id
        )
        if rows_updated == 0:
            return JSONResponse(
                status_code=404,
                content={'success': False, 'message': 'Заявка не найдена'}
            )
        return JSONResponse(content={'success': True})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'success': False, 'message': str(e)}
        )