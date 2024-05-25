import requests
import pandas as pd
from datetime import datetime, timezone
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import numpy as np
import logging

# Einrichten des Loggings für Debugging-Zwecke
logging.basicConfig(level=logging.DEBUG)

# Mapping der Wetterbedingungen zu OpenWeatherMap-Wettercodes
weatherID_mapping = {
    1: 800,   # klarer Himmel
    2: 801,   # wenige Wolken: 11-25%
    3: 802,   # verstreute Wolken: 25-50%
    4: 803,   # gebrochene Wolken: 51-84%
    4: 804,   # bedeckter Himmel: 85-100%
    5: 701,   # Dunst
    5: 711,   # Rauch
    5: 721,   # Dunstschleier
    5: 731,   # Sand-/Staubwirbel
    5: 741,   # Nebel
    5: 751,   # Sand
    5: 761,   # Staub
    5: 762,   # Vulkanasche
    5: 771,   # Böen
    7: 300,   # leichter Nieselregen
    7: 301,   # Nieselregen
    7: 310,   # leichter Nieselregen
    7: 311,   # Nieselregen
    7: 321,   # Schauerregen
    7: 500,   # leichter Regen
    7: 520,   # leichter Regenschauer
    8: 501,   # mässiger Regen
    8: 302,   # starker Nieselregen
    8: 312,   # starker Nieselregen
    8: 313,   # Regenschauer und Nieselregen
    8: 521,   # Regenschauer
    9: 502,   # starker Regen
    9: 503,   # sehr starker Regen
    9: 504,   # extremer Regen
    9: 522,   # starker Regenschauer
    9: 531,   # unregelmässiger Regenschauer
    9: 314,   # starker Regenschauer und Nieselregen
    10: 511,  # gefrierender Regen
    12: 611,  # Schneeregen
    12: 612,  # leichter Schneeregen
    12: 613,  # Schneeregen
    12: 615,  # leichter Regen und Schnee
    12: 616,  # Regen und Schnee
    14: 600,  # leichter Schneefall
    14: 620,  # leichter Schneeschauer
    15: 601,  # Schneefall
    15: 621,  # Schneeschauer
    16: 602,  # starker Schneefall
    16: 622,  # starker Schneeschauer
    25: 200,  # Gewitter mit leichtem Regen
    25: 201,  # Gewitter mit Regen
    25: 202,  # Gewitter mit starkem Regen
    25: 210,  # leichtes Gewitter
    25: 211,  # Gewitter
    25: 230,  # Gewitter mit leichtem Nieselregen
    25: 231,  # Gewitter mit Nieselregen
    25: 232,  # Gewitter mit starkem Nieselregen
    26: 212,  # starkes Gewitter
    26: 221,  # unregelmässiges Gewitter
    27: 781   # Tornado
}

def get_api_key():
    # Laden des API-Schlüssels aus der JSON-Datei
    with open('backend/DataGathering/pwd.json') as f:
        credentials = json.load(f)
        api_key = credentials['openweathermap_api_key']
    return api_key

def fetch_weatherdata_hour(stations, start_end_openweather):
    # Umwandeln der Startzeit in ein datetime-Objekt und dann in einen UNIX-Zeitstempel
    start_datetime = datetime.strptime(str(start_end_openweather), "%Y-%m-%d %H:%M:%S")
    hour = int(start_datetime.timestamp())
    openweather_final = pd.DataFrame()
    
    # Abrufen der stündlichen Wetterdaten für jede Station
    for index, stationopenweather in stations.iterrows():
        weather_openweather_df = get_weather_hour(int(stationopenweather['id_openweathermap']), hour)
        openweather_final = pd.concat([openweather_final, weather_openweather_df])
        openweather_final['Region'] = stationopenweather['Region']
        openweather_final['Koordinaten'] = stationopenweather['Koordinaten']
        openweather_final['Ort'] = stationopenweather['Ort']
    return openweather_final

def fetch_weatherdata_current(stations):
    openweather_final = pd.DataFrame()
    
    # Abrufen der aktuellen Wetterdaten für jede Station
    for index, stationopenweather in stations.iterrows():
        weather_openweather_df = get_weather_current(int(stationopenweather['id_openweathermap']))
        openweather_final = pd.concat([openweather_final, weather_openweather_df])
        openweather_final['Region'] = stationopenweather['Region']
        openweather_final['Koordinaten'] = stationopenweather['Koordinaten']
        openweather_final['Ort'] = stationopenweather['Ort']
    return openweather_final

def get_weather_hour(city_id, hour):
    # Aufbau der API-Anfrage-URL für stündliche Wetterdaten
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
    # Aufbau der API-Anfrage-URL für aktuelle Wetterdaten
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
    # Aufbau der HTTP-Anfrage mit Retry-Mechanismus
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
        response = session.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Anfrage fehlgeschlagen: {e}")
        raise

def extract_weather_details(weather_data):
    # Extrahieren relevanter Wetterdetails aus den API-Daten
    weather_id = weather_data['weather'][0]['id']
    mapped_id = weatherID_mapping.get(weather_id)
    
    return {
        'Zeit': [datetime.fromtimestamp(weather_data['dt'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],        
        'Land': [weather_data['sys']['country']],
        'Temperatur': [weather_data['main']['temp']],
        'Luftdruck': [weather_data['main']['pressure']],
        'Luftfeuchtigkeit': [weather_data['main']['humidity']],
        'Wetterbedingung': [mapped_id],
        'Windgeschwindigkeit in km/h': [weather_data['wind']['speed']],
        'Windrichtung': [weather_data['wind']['deg']],
        'Wolkenbedeckung': [weather_data['clouds']['all']],
        'Niederschlagsmenge (letzte Stunde)': [weather_data.get('rain', {}).get('1h', np.nan)],
        'Schneefallmenge (letzte Stunde)': [weather_data.get('snow', {}).get('1h', np.nan)],
        'Windböen': [weather_data.get('wind', {}).get('gust', np.nan)],
        'Sonnenaufgang': [datetime.fromtimestamp(weather_data['sys']['sunrise'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],
        'Sonnenuntergang': [datetime.fromtimestamp(weather_data['sys']['sunset'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],
    }

def create_weather_dataframe(weather_details):
    # Erstellen eines DataFrames aus den Wetterdetails
    df_weather = pd.DataFrame(weather_details)    
    df_weather['Taupunkt'] = df_weather['Temperatur'] - ((100 - df_weather['Luftfeuchtigkeit']) / 5)
    return df_weather
