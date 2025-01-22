from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app.config import settings
from app.api.dao import ApplicationDAO


router = APIRouter(prefix='', tags=['frontend admin'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/admin', response_class=HTMLResponse)
async def read_root(request: Request, admin_id: int = None):
    """
    Обработчик маршрута /admin для отображения панели администратора с пагинацией заявок.
    """
    data_page = {'request': request, 'access': False,
                  'title_h1': 'Панель работников магазина'}
    if False: # admin_id is None or admin_id != settings.ADMIN_ID:
        data_page['message'] = 'У вас не прав для получения информации о заявках!'
        return templates.TemplateResponse('applications.html', data_page)
    else:
        data_page['access'] = True
        data_page['applications'] = await ApplicationDAO.get_all_applications()
        return templates.TemplateResponse('applications.html', data_page)
    #  data_page = {
    #     'request': request,
    #     'access': False,
    #     'title_h1': 'Панель работников магазина',
    #     'page': page,
    #     'page_size': page_size
    # }


