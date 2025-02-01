from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.api.models import Application

class ItemCreateRequest(BaseModel):
    worker_id: int = Field(..., description='ID работника')
    item_name: str = Field(..., min_length=1, max_length=100, description='Название предмета')
    quantity: float = Field(..., gt=0, description='Количество предметов')
    unit_type: str = Field(..., min_length=1, max_length=20, description='Тип единицы измерения')
    comment: Optional[str] = Field(None, max_length=255, description='Комментарий к предмету')

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'worker_id': 123,
                'item_name': 'Молоток',
                'quantity': 5.0,
                'unit_type': 'шт',
                'comment': 'Для строительных работ'
            }
        }


class ItemUpdateQuantity(BaseModel):
    worker_id: int = Field(..., description='ID работника')
    item_id: int = Field(..., description='ID товара')
    quantity: float = Field(..., gt=0, description='Количество предметов')

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'worker_id': 123,
                'quantity': 5.0,
            }
        }


class AppointmentUpdateStatusData(BaseModel):
    application_id: int = Field(..., alias='application_id')
    master_id: int = Field(..., alias='master_id')
    status: str = Field(..., alias='status')

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True

    @field_validator('status')
    def validate_status(cls, value):
        if value not in [status.name for status in Application.StatusEnum]:
            raise ValueError(f"Неверный статус: {value}")
        return value