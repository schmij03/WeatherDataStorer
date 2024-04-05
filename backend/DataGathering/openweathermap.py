import requests
import pandas as pd
from datetime import datetime, timezone
from mongodb_connection import connect_mongodb

def get_wind_direction(degrees):
    directions = ["N", "NNO", "NO", "ONO", "O", "OSO", "SO", "SSO", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]

def get_weather(api_key, city_name):
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric&lang=de"
    response = requests.get(complete_url)
    weather_data = response.json()
    
    if weather_data['cod'] == 200:
        # Extrahieren der notwendigen Daten
        weather_details = {
            'Zeit': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'Stadt': [city_name],
            'Temperatur': [weather_data['main']['temp']],
            'Luftdruck': [weather_data['main']['pressure']],
            'Luftfeuchtigkeit': [weather_data['main']['humidity']],
            'Beschreibung': [weather_data['weather'][0]['description']],
            'Windgeschwindigkeit': [weather_data['wind']['speed']],
            'Windrichtung': [f"{weather_data['wind']['deg']}° {get_wind_direction(weather_data['wind']['deg'])}"],
            'Wolkenbedeckung': [weather_data['clouds']['all']],
            'Niederschlagsmenge (letzte Stunde)': [weather_data.get('rain', {}).get('1h', 'Keine Daten')],
            'Schneefallmenge (letzte Stunde)': [weather_data.get('snow', {}).get('1h', 'Keine Daten')],
            'Windböen': [weather_data.get('wind', {}).get('gust', 'Keine Daten')],
            'Sonnenaufgang': [datetime.fromtimestamp(weather_data['sys']['sunrise'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],
            'Sonnenuntergang': [datetime.fromtimestamp(weather_data['sys']['sunset'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')]
        }
        
        # Konvertierung zu DataFrame
        df_weather = pd.DataFrame(weather_details)
        
        db, collection = connect_mongodb()
        if db is not None and collection is not None:
            # Konvertierung des DataFrame zu Dictionary und Speicherung in MongoDB
            collection.insert_one(df_weather.to_dict('records')[0])
            print("Wetterdaten erfolgreich in MongoDB gespeichert.")
    else:
        print("Stadt nicht gefunden oder API-Schlüssel ist ungültig.")

# Beispielaufruf
api_key = '06f4684f04692eef55eaca387497e196'
city_name = 'Zurich'
get_weather(api_key, city_name)
