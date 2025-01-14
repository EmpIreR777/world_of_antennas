from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from urllib.parse import unquote

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

YANDEX_API_KEY = "8866969e-a8bc-408e-abd5-3991ce7a0b33"

@app.get("/suggest-address/{query}")
async def suggest_address(query: str):
    decoded_query = unquote(query)
    print(f"Received query: {query}") 
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": YANDEX_API_KEY,
        "format": "json",
        "geocode": query
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        suggestions = []
        features = data['response']['GeoObjectCollection']['featureMember']
        
        for feature in features:
            address = feature['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
            suggestions.append({"address": address})
            
        return suggestions[:5]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
