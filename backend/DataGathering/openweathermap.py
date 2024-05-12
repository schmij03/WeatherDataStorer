import requests
import pandas as pd
from datetime import datetime, timezone
api_key = '06f4684f04692eef55eaca387497e196'

def get_wind_direction(degrees):
    directions = ["N", "NNO", "NO", "ONO", "O", "OSO", "SO", "SSO", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]

def get_weather(start,end,city_id):
    start = int(start.timestamp())
    end = int(end.timestamp())
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}id={city_id}&start={start}&end={end}&appid={api_key}&units=metric&lang=de"
    response = requests.get(complete_url)
    weather_data = response.json()
    
    if weather_data['cod'] == 200:
        # Extrahieren der notwendigen Daten
        weather_details = {
            'Zeit': [datetime.fromtimestamp(weather_data['dt'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],
            'Ort': [weather_data['name']],
            'Land': [weather_data['sys']['country']],
            'Temperatur': [weather_data['main']['temp']],
            'Luftdruck': [weather_data['main']['pressure']],
            'Luftfeuchtigkeit': [weather_data['main']['humidity']],
            'Wetterbedingung': [weather_data['weather'][0]['description']],
            'Windgeschwindigkeit': [weather_data['wind']['speed']],
            'Windrichtung': [f"{weather_data['wind']['deg']}° {get_wind_direction(weather_data['wind']['deg'])}"],
            'Wolkenbedeckung': [weather_data['clouds']['all']],
            'Niederschlagsmenge (letzte Stunde)': [weather_data.get('rain', {}).get('1h', 'Keine Daten')],
            'Schneefallmenge (letzte Stunde)': [weather_data.get('snow', {}).get('1h', 'Keine Daten')],
            'Windböen': [weather_data.get('wind', {}).get('gust', 'Keine Daten')],
            'Sonnenaufgang': [datetime.fromtimestamp(weather_data['sys']['sunrise'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],
            'Sonnenuntergang': [datetime.fromtimestamp(weather_data['sys']['sunset'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],
            'Lat': [weather_data['coord']['lat']],
            'Lon': [weather_data['coord']['lon']]
        }
        
        # Konvertierung zu DataFrame
        df_weather = pd.DataFrame(weather_details)
        df_weather['Koordinaten']=df_weather['Lat'].astype(str)+','+df_weather['Lon'].astype(str)
        df_weather.drop(columns=['Lat','Lon'],inplace=True)
        df_weather['Taupunkt'] = df_weather['Temperatur'] - ((100 - df_weather['Luftfeuchtigkeit']) / 5)
        return df_weather
    else:
        print("Stadt nicht gefunden oder API-Schlüssel ist ungültig.")