import requests
import pandas as pd
from datetime import datetime, timezone
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Einrichten des Loggings für Debugging-Zwecke
logging.basicConfig(level=logging.DEBUG)

def get_api_key():
    # Laden des API-Schlüssels aus der JSON-Datei
    with open('backend/DataGathering/pwd.json') as f:
        credentials = json.load(f)
        api_key = credentials['openweathermap_api_key']
    return api_key

def fetch_weatherdata_hour(stations, start_end_openweather):
    # Konvertieren der Startzeit in ein datetime-Objekt und dann in einen UNIX-Zeitstempel
    start_datetime = datetime.strptime(str(start_end_openweather), "%Y-%m-%d %H:%M:%S")
    hour = int(start_datetime.timestamp())
    openweather_final = pd.DataFrame()
    
    # Abrufen der stündlichen Wetterdaten für jede Station
    for index, stationopenweather in stations.iterrows():
        weather_openweather_df = get_weather_hour(int(stationopenweather['id_openweathermap']), hour)
        openweather_final = pd.concat([openweather_final, weather_openweather_df])
    return openweather_final

def fetch_weatherdata_current(stations):
    openweather_final = pd.DataFrame()
    
    # Abrufen der aktuellen Wetterdaten für jede Station
    for index, stationopenweather in stations.iterrows():
        weather_openweather_df = get_weather_current(int(stationopenweather['id_openweathermap']))
        openweather_final = pd.concat([openweather_final, weather_openweather_df])
    return openweather_final

def get_weather_hour(city_id, hour):
    api_key = get_api_key()
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}id={city_id}&start={hour}&end={hour}&appid={api_key}&units=metric&lang=de"
    response = make_request(complete_url)
    weather_data = response.json()
    
    # Überprüfen des API-Antwortcodes und Extrahieren der Wetterdetails
    if weather_data['cod'] == 200:
        weather_details = extract_weather_details(weather_data)
        df_weather = create_weather_dataframe(weather_details)
        return df_weather
    else:
        print(f"Ortschaft mit ID {city_id} nicht gefunden oder API-Schlüssel ist ungültig.")
        return pd.DataFrame()

def get_weather_current(city_id):
    api_key = get_api_key()
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}id={city_id}&appid={api_key}&units=metric&lang=de"
    response = make_request(complete_url)
    weather_data = response.json()
    
    # Überprüfen des API-Antwortcodes und Extrahieren der Wetterdetails
    if weather_data['cod'] == 200:
        weather_details = extract_weather_details(weather_data)
        df_weather = create_weather_dataframe(weather_details)
        return df_weather
    else:
        print(f"Ortschaft mit ID {city_id} nicht gefunden oder API-Schlüssel ist ungültig.")
        return pd.DataFrame()

def make_request(url):
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    try:
        response = session.get(url)  # SSL-Verifizierung ist standardmäßig aktiviert
        response.raise_for_status()  # HTTPError bei schlechten Antworten auslösen
        return response
    except requests.exceptions.RequestException as e:
        print(f"Anfrage fehlgeschlagen: {e}")
        raise

def extract_weather_details(weather_data):
    # Extrahieren der relevanten Wetterdetails aus den API-Daten
    return {
        'Zeit': [datetime.fromtimestamp(weather_data['dt'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],
        'Ort': [weather_data['name']],
        'Land': [weather_data['sys']['country']],
        'Temperatur': [weather_data['main']['temp']],
        'Luftdruck': [weather_data['main']['pressure']],
        'Luftfeuchtigkeit': [weather_data['main']['humidity']],
        'Wetterbedingung': [weather_data['weather'][0]['description']],
        'Windgeschwindigkeit': [weather_data['wind']['speed']],
        'Windrichtung': [weather_data['wind']['deg']],
        'Wolkenbedeckung': [weather_data['clouds']['all']],
        'Niederschlagsmenge (letzte Stunde)': [weather_data.get('rain', {}).get('1h', 'Keine Daten')],
        'Schneefallmenge (letzte Stunde)': [weather_data.get('snow', {}).get('1h', 'Keine Daten')],
        'Windböen': [weather_data.get('wind', {}).get('gust', 'Keine Daten')],
        'Sonnenaufgang': [datetime.fromtimestamp(weather_data['sys']['sunrise'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],
        'Sonnenuntergang': [datetime.fromtimestamp(weather_data['sys']['sunset'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],
        'Lat': [weather_data['coord']['lat']],
        'Lon': [weather_data['coord']['lon']],
    }

def create_weather_dataframe(weather_details):
    # Erstellen eines DataFrames aus den Wetterdetails
    df_weather = pd.DataFrame(weather_details)
    df_weather['Koordinaten'] = df_weather['Lat'].astype(str) + ',' + df_weather['Lon'].astype(str)
    df_weather.drop(columns=['Lat', 'Lon'], inplace=True)
    df_weather['Taupunkt'] = df_weather['Temperatur'] - ((100 - df_weather['Luftfeuchtigkeit']) / 5)
    return df_weather