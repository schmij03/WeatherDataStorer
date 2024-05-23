import requests
import pandas as pd
from datetime import datetime, timezone
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Einrichten des Loggings für Debugging-Zwecke
logging.basicConfig(level=logging.DEBUG)

weatherID_mapping={
    1: 800,   # clear sky
    2: 801,   # few clouds: 11-25%
    3: 802,   # scattered clouds: 25-50%
    4: 803,   # broken clouds: 51-84%
    4: 804,   # overcast clouds: 85-100%
    5: 701,   # mist
    5: 711,   # smoke
    5: 721,   # haze
    5: 731,   # sand/dust whirls
    5: 741,   # fog
    5: 751,   # sand
    5: 761,   # dust
    5: 762,   # volcanic ash
    5: 771,   # squalls
    7: 300,   # light intensity drizzle
    7: 301,   # drizzle
    7: 310,   # light intensity drizzle rain
    7: 311,   # drizzle rain
    7: 321,   # shower drizzle
    7: 500,   # light rain
    7: 520,   # light intensity shower rain
    8: 501,   # moderate rain
    8: 302,   # heavy intensity drizzle
    8: 312,   # heavy intensity drizzle rain
    8: 313,   # shower rain and drizzle
    8: 521,   # shower rain
    9: 502,   # heavy intensity rain
    9: 503,   # very heavy rain
    9: 504,   # extreme rain
    9: 522,   # heavy intensity shower rain
    9: 531,   # ragged shower rain
    9: 314,   # heavy shower rain and drizzle
    10: 511,  # freezing rain
    12: 611,  # sleet
    12: 612,  # light shower sleet
    12: 613,  # shower sleet
    12: 615,  # light rain and snow
    12: 616,  # rain and snow
    14: 600,  # light snow
    14: 620,  # light shower snow
    15: 601,  # snow
    15: 621,  # shower snow
    16: 602,  # heavy snow
    16: 622,  # heavy shower snow
    25: 200,  # thunderstorm with light rain
    25: 201,  # thunderstorm with rain
    25: 202,  # thunderstorm with heavy rain
    25: 210,  # light thunderstorm
    25: 211,  # thunderstorm
    25: 230,  # thunderstorm with light drizzle
    25: 231,  # thunderstorm with drizzle
    25: 232,  # thunderstorm with heavy drizzle
    26: 212,  # heavy thunderstorm
    26: 221,  # ragged thunderstorm
    27: 781   # tornado
}

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
        openweather_final['Region'] = stationopenweather['Region']
    return openweather_final

def fetch_weatherdata_current(stations):
    openweather_final = pd.DataFrame()
    
    # Abrufen der aktuellen Wetterdaten für jede Station
    for index, stationopenweather in stations.iterrows():
        weather_openweather_df = get_weather_current(int(stationopenweather['id_openweathermap']))
        openweather_final = pd.concat([openweather_final, weather_openweather_df])
        openweather_final['Region'] = stationopenweather['Region']
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
    weather_id = weather_data['weather'][0]['id']
    mapped_id = weatherID_mapping.get(weather_id)
    
    return {
        'Zeit': [datetime.fromtimestamp(weather_data['dt'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')],
        'Ort': [weather_data['name']],
        'Land': [weather_data['sys']['country']],
        'Temperatur': [weather_data['main']['temp']],
        'Luftdruck': [weather_data['main']['pressure']],
        'Luftfeuchtigkeit': [weather_data['main']['humidity']],
        'Wetterbedingung': [mapped_id],
        'Windgeschwindigkeit in km/h': [weather_data['wind']['speed']],
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