import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.dao import ApplicationDAO, UserDAO
from app.api.models import Application
from app.bot.create_bot import bot
from app.pages.pagination import paginate
from app.pages.schemas import AppointmentUpdateStatusData


router = APIRouter(prefix='', tags=['frontend admin'])

templates = Jinja2Templates(directory='app/templates')


@router.get('/admin', response_class=HTMLResponse)
async def read_works(
    request: Request, 
    worker_id: int = None,
    sort_by: str = None,  # Поле для сортировки
    order: str = 'asc',   # Направление сортировки (по умолчанию - по возрастанию)
    page: int = 1,        # Номер страницы (по умолчанию - 1)
    page_size: int = 3   # Количество элементов на странице (по умолчанию - 10)
    ):
    """
    Обработчик маршрута /admin{worker_id} для отображения заявок с пагинацией.
    """
    data_page = {'request': request, 'access': False,
                 'title_h1': 'Панель работников магазина'}
    user_check = await UserDAO.find_one_or_none_by_roles(telegram_id=worker_id)
    if worker_id is None or user_check is None:
        data_page['message'] = 'Работник магазина не найден, для которого нужно отобразить все заявки.'
        return templates.TemplateResponse('applications.html', data_page)
    else:
        # Получаем общее количество заявок
        total_applications = await ApplicationDAO.count()

        # Вычисляем параметры пагинации
        pagination = paginate(total_applications, page, page_size)

        # Получаем заявки с пагинацией и сортировкой
        applications = await ApplicationDAO.get_all_applications(
            sort_by=sort_by, 
            order=order, 
            offset=pagination['offset'], 
            limit=pagination['limit']
        )

        data_page['worker_id'] = worker_id
        data_page['statuses'] = Application.StatusEnum
        data_page['access'] = True
        data_page['user_role'] = True
        data_page['applications'] = applications
        data_page['page'] = page
        data_page['page_size'] = page_size
        data_page['total_pages'] = pagination["total_pages"]

        return templates.TemplateResponse('applications_wokers.html', data_page)


@router.post('/update-application-status', response_class=JSONResponse)
async def update_application_status(request: Request, data: AppointmentUpdateStatusData):
    try:
        # Обновление записи в базе данных
        updated_count= await ApplicationDAO.update(
            filter_by={'id': data.application_id},
            status=data.status,
            master_id=data.master_id
        )

        if updated_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Заявка не найдена или не была обновлена.')

        return JSONResponse(content={'success': True})

    except SQLAlchemyError as e:
        # Логирование ошибки
        logging.error(f"Ошибка при обновлении заявки: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail='Внутренняя ошибка сервера.')


