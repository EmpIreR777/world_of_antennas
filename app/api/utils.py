import logging
from fastapi import HTTPException, APIRouter
import httpx
from urllib.parse import unquote

from app.config import settings


router = APIRouter()

YANDEX_API_KEY = settings.get_key_yandex_geo()


@router.get('/suggest-address/')
async def suggest_address(query: str):
    decoded_query = unquote(query)

    # Добавляем "Алтайский край" к запросу
    if "алтайский край" not in decoded_query.lower():
        search_query = f"{decoded_query}, Алтайский край"
    else:
        search_query = decoded_query

    url = 'https://geocode-maps.yandex.ru/1.x/'
    params = {
        'apikey': YANDEX_API_KEY,
        'format': 'json',
        'geocode': search_query,
        'kind': 'house',
        'results': 20,  # Увеличиваем количество результатов
        'bbox': '77.88,50.93~87.36,54.59'  # Ограничивающий прямоугольник для Алтайского края
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        suggestions = []
        features = data['response']['GeoObjectCollection']['featureMember']

        for feature in features:
            geo_object = feature['GeoObject']
            address_details = geo_object['metaDataProperty']['GeocoderMetaData']

            # Проверяем, находится ли адрес в Алтайском крае
            address_components = address_details['Address'].get('Components', [])
            is_altai_krai = any(
                component['name'].lower() == "алтайский край"
                for component in address_components
            )

            if is_altai_krai:
                address = address_details['text']
                pos = geo_object['Point']['pos']
                longitude, latitude = map(float, pos.split())
                suggestions.append({
                    "address": address,
                    "latitude": latitude,
                    "longitude": longitude
                })
                if len(suggestions) >= 5:  # Ограничиваем до 5 результатов
                    break

        return suggestions

    except Exception as e:
        logging.error(f'Error: {e}')
        raise HTTPException(status_code=500, detail=str(e))
