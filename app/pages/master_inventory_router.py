from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app.config import settings
from app.api.dao import ShopDAO, ServiceDAO, ApplicationDAO, UserDAO


router = APIRouter(prefix='', tags=['frontend master'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/master_list', response_class=HTMLResponse)
async def get_master_list_and_items_lists(request: Request, worker_id: int = None):
    """
    Обработчик маршрута /master_list для отображения панели администратора.
    """
    data_page = {'request': request, 'access': False,
                  'title_h1': 'Панель работников магазина'}
    if False: # worker_id is None or worker_id != settings.ADMIN_ID:
        data_page['message'] = 'У вас не прав для получения информации о заявках!'
        return templates.TemplateResponse('applications.html', data_page)
    else:
        data_page['access'] = True
        data_page['applications'] = await ApplicationDAO.get_all_applications()
        return templates.TemplateResponse('applications.html', data_page)


@router.get('/master_detail{master_id}', response_class=HTMLResponse)
async def get_master_detail_and_item_list(request: Request, worker_id: int = None):
    """
    Обработчик маршрута /master_detail для отображения панели администратора.
    """
    data_page = {'request': request, 'access': False,
                  'title_h1': 'Панель работников магазина'}
    if False: # worker_id is None or worker_id != settings.ADMIN_ID:
        data_page['message'] = 'У вас не прав для получения информации о заявках!'
        return templates.TemplateResponse('applications.html', data_page)
    else:
        data_page['access'] = True
        data_page['applications'] = await ApplicationDAO.get_all_applications()
        return templates.TemplateResponse('applications.html', data_page)


@router.post('/create_master_items', response_class=HTMLResponse)
async def create_master_items(request: Request, worker_id: int = None):
    """
    Обработчик маршрута /inventory_item для отображения панели администратора.
    """
    data_page = {'request': request, 'access': False,
                  'title_h1': 'Панель работников магазина'}
    if False: # worker_id is None or worker_id != settings.ADMIN_ID:
        data_page['message'] = 'У вас не прав для получения информации о заявках!'
        return templates.TemplateResponse('applications.html', data_page)
    else:
        data_page['access'] = True
        data_page['applications'] = await ApplicationDAO.get_all_applications()
        return templates.TemplateResponse('applications.html', data_page)


@router.post('/update_master_items', response_class=HTMLResponse)
async def update_master_items(request: Request, worker_id: int = None):
    """
    Обработчик маршрута /update_master_items для отображения панели администратора.
    """
    data_page = {'request': request, 'access': False,
                  'title_h1': 'Панель работников магазина'}
    if False: # worker_id is None or worker_id != settings.ADMIN_ID:
        data_page['message'] = 'У вас не прав для получения информации о заявках!'
        return templates.TemplateResponse('applications.html', data_page)
    else:
        data_page['access'] = True
        data_page['applications'] = await ApplicationDAO.get_all_applications()
        return templates.TemplateResponse('applications.html', data_page)


@router.post('/delete_master_item', response_class=HTMLResponse)
async def delete_master_item(request: Request, worker_id: int = None):
    """
    Обработчик маршрута /inventory_item для отображения панели администратора.
    """
    data_page = {'request': request, 'access': False,
                  'title_h1': 'Панель работников магазина'}
    if False: # worker_id is None or worker_id != settings.ADMIN_ID:
        data_page['message'] = 'У вас не прав для получения информации о заявках!'
        return templates.TemplateResponse('applications.html', data_page)
    else:
        data_page['access'] = True
        data_page['applications'] = await ApplicationDAO.get_all_applications()
        return templates.TemplateResponse('applications.html', data_page)