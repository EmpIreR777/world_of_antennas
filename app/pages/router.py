from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app.api.dao import ShopDAO, ServiceDAO, ApplicationDAO, UserDAO


router = APIRouter(prefix='', tags=['Фронтенд'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        'index.html', {'request': request, 'title': 'Мир Антенн'}
    )


@router.get('/form', response_class=HTMLResponse)
async def read_root(request: Request, user_id: int = None, first_name: str = None):
    shops = await ShopDAO.find_all()
    services = await ServiceDAO.find_all()
    data_page = {'request': request,
                 'user_id': user_id,
                 'first_name': first_name,
                 'title': 'Мир антенн',
                 'shops': shops,
                 'services': services}
    return templates.TemplateResponse('application-form.html', data_page)