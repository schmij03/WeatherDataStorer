import requests
from datetime import datetime, timezone

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
        print(f"Wetter in {city_name}:")
        print(f"Temperatur: {weather_data['main']['temp']}°C")
        print(f"Luftdruck: {weather_data['main']['pressure']} hPa")
        print(f"Luftfeuchtigkeit: {weather_data['main']['humidity']}%")
        print(f"Beschreibung: {weather_data['weather'][0]['description']}")
        print(f"Windgeschwindigkeit: {weather_data['wind']['speed']} m/s")
        print(f"Windrichtung: {weather_data['wind']['deg']}° {get_wind_direction(weather_data['wind']['deg'])}")
        print(f"Wolkenbedeckung: {weather_data['clouds']['all']}%")
        
        # Niederschlagsmenge
        niederschlag = weather_data.get('rain', {}).get('1h', 'Keine Daten')
        print(f"Niederschlagsmenge (letzte Stunde): {niederschlag} mm")

        # Schneefallmenge
        schneefall = weather_data.get('snow', {}).get('1h', 'Keine Daten')
        print(f"Schneefallmenge (letzte Stunde): {schneefall} mm")
        
        # Windböen
        boeen = weather_data.get('wind', {}).get('gust', 'Keine Daten')
        print(f"Windböen: {boeen} m/s")
        
        sunrise_time = datetime.fromtimestamp(weather_data['sys']['sunrise'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        sunset_time = datetime.fromtimestamp(weather_data['sys']['sunset'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Sonnenaufgang: {sunrise_time} UTC")
        print(f"Sonnenuntergang: {sunset_time} UTC")
    else:
        print("Stadt nicht gefunden oder API-Schlüssel ist ungültig.")

# Beispielaufruf
api_key = '06f4684f04692eef55eaca387497e196'
city_name = 'Zurich'
get_weather(api_key, city_name)
