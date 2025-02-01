from typing import Optional
from datetime import date, time
from pydantic import BaseModel, Field



class AppointmentData(BaseModel):
    user_id: int = Field(..., description='id клиента')
    client_name: str = Field(..., min_length=1, max_length=50, description='Имя клиента')
    phone_number: Optional[str] = Field(None, max_length=20, description='Номер телефона')
    address: str = Field(..., min_length=5, max_length=255, description='Адрес')
    shop_id: int = Field(..., description='ID магазина')
    service_id: int = Field(..., description='ID услуги')
    appointment_date: date = Field(..., description='Дата заявки')
    appointment_time: time = Field(..., description='Время заявки')
    comment: Optional[str] = Field(None, max_length=255, description='Комментарий к заявке')
    latitude: float | None = Field(..., description='Широта')
    longitude: float | None = Field(..., description='Долгота')

    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy
        json_schema_extra = {
            'example': {
                'user_id': 123456789,
                'shop_id': 1,
                'service_id': 1,
                'appointment_date': '2024-01-01',
                'appointment_time': '14:30:00',
                'client_name': 'Иван Иванов',
                'status': 'Не обработана',
                'comment': 'Предпочтительно утреннее время',
                'phone_number': '+7(999)123-45-67'
            }
        }