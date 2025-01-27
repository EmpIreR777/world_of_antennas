from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app.api.models import User
from app.config import settings
from app.api.dao import ApplicationDAO, UserDAO


router = APIRouter(prefix='', tags=['frontend admin'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/admin', response_class=HTMLResponse)
async def read_works(request: Request, worker_id: int = None):
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
        applications = await ApplicationDAO.get_all_applications()
        print(applications)
        data_page['access'] = True
        data_page['user_role'] = True

        if len(applications):
            data_page['applications'] = applications
            return templates.TemplateResponse('applications.html', data_page)
        else:
            data_page['message'] = 'У вас нет заявок!'
            return templates.TemplateResponse('applications.html', data_page)


