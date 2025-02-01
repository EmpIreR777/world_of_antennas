from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app.api.models import User
from app.config import settings
from app.api.dao import ShopDAO, ServiceDAO, ApplicationDAO, UserDAO


router = APIRouter(prefix='', tags=['frontend user'])

templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Обработчик маршрута / главная страница.
    """
    return templates.TemplateResponse(
        'index.html', {'request': request, 'title': 'Мир Антенн'}
    )


@router.get('/form', response_class=HTMLResponse)
async def read_root(request: Request, user_id: int = None, first_name: str = None):
    """
    Обработчик маршрута /form для регистрации заявки.
    """
    shops = await ShopDAO.find_all()
    services = await ServiceDAO.find_all()
    data_page = {'request': request,
                 'user_id': user_id,
                 'first_name': first_name,
                 'title': 'Мир антенн',
                 'shops': shops,
                 'services': services}
    return templates.TemplateResponse('application-form.html', data_page)


@router.get('/applications', response_class=HTMLResponse)
async def read_root(request: Request, user_id: int = None):
    """
    Обработчик маршрута /applications{user_id} для отображения заявок с пагинацией.
    """
    data_page = {'request': request, 'access': False, 'title_h1': 'Мои заявки'}
    user_check = await UserDAO.find_one_or_none(telegram_id=user_id)
    if user_id is None or user_check is None:
        data_page['message'] = 'Пользователь, по которому нужно отобразить заявки, не указан или не найден в базе данных'
        return templates.TemplateResponse('applications.html', data_page)
    else:
        applications = await ApplicationDAO.get_applications_by_user(user_id=user_id)

        data_page['access'] = True
        data_page['user_role'] = user_check.role != User.RoleEnum.USER

        if len(applications):
            data_page['applications'] = applications  # Используйте уже полученные данные
            return templates.TemplateResponse('applications.html', data_page)
        else:
            data_page['message'] = 'У вас нет заявок!'
            return templates.TemplateResponse('applications.html', data_page)
