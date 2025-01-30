import logging
from fastapi import APIRouter, status
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.api.models import InventoryItem, User
from app.config import settings
from app.api.dao import InventoryItemDAO, UserDAO, UserDAO
from app.pages.schemas import ItemCreateRequest


router = APIRouter(prefix='/worker', tags=['frontend worker'])

templates = Jinja2Templates(directory='app/templates')


@router.get('/worker_list', response_class=HTMLResponse)
async def get_worker_list_and_items_lists(request: Request, worker_id: int):
    """
    Обработчик маршрута /worker_list для отображения панели администратора.
    """
    data_page = {
        'request': request, 
        'access': False,
        'title_h1': 'Панель задолженности работников магазина'
    }
    try:
        items_workers = await UserDAO.get_all_items_worker_list()
        data_page['access'] = True
        # data_page['worker_id'] = worker_id

        data_page['items_workers'] = items_workers
        if not items_workers:
            data_page['message'] = 'В базе данных нет работников с задолженностями'
    except Exception as e:
        logging.error(f'Ошибка при получении списка работников: {e}')
        data_page['message'] = 'Произошла ошибка при получении данных'
        data_page['items_workers'] = []
    return templates.TemplateResponse('workers.html', data_page)


@router.post('/create_worker_items')
async def create_worker_items(request: Request, data: ItemCreateRequest):
    """
    Обработчик маршрута для добавления товара в задолженность магазина.
    """
    try:
        user = await UserDAO.find_one_or_none_by_roles(telegram_id=data.worker_id)
        if not user or user.role == User.RoleEnum.USER:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={'message': 'У вас нет прав для добавления товара в задолженность!'}
            )
        await InventoryItemDAO.add(
            user_id=data.worker_id,
            item_name=data.item_name,
            quantity=data.quantity,
            unit_type=data.unit_type,
            comment=data.comment
        )
        return JSONResponse(
            content={'message': 'Товар успешно добавлен'}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': str(e)}
        )


@router.post('/update_worker_quantity', response_class=HTMLResponse)
async def update_worker_items(request: Request, worker_id: int):
    """
    Обработчик маршрута /update_worker_quantity для отображения панели администратора.
    """
    data_page = {'request': request, 'access': False,
                  'title_h1': 'Панель задолженности работников магазина'}
    if worker_id is None or worker_id != settings.ADMIN_ID:
        data_page['message'] = 'У вас не прав для получения информации о заявках!'
        return templates.TemplateResponse('workers.html', data_page)
    else:
        data_page['access'] = True
        data_page['workers'] = await UserDAO.get_all_applications()
        return templates.TemplateResponse('workers.html', data_page)


@router.post('/delete_worker_item', response_class=HTMLResponse)
async def delete_worker_item(request: Request, worker_id: int):
    """
    Обработчик маршрута /inventory_item для отображения панели администратора.
    """
    data_page = {'request': request, 'access': False,
                  'title_h1': 'Панель задолженности работников магазина'}
    if worker_id is None or worker_id != settings.ADMIN_ID:
        data_page['message'] = 'У вас не прав для получения информации о заявках!'
        return templates.TemplateResponse('workers.html', data_page)
    else:
        data_page['access'] = True
        data_page['workers'] = await UserDAO.get_all_applications()
        return templates.TemplateResponse('workers.html', data_page)