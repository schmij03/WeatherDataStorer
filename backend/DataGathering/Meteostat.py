from datetime import datetime
import pandas as pd
from meteostat import Stations, Hourly
from mongodb_connection import connect_mongodb

def get_wind_direction(degrees):
    """
    Converts wind direction from degrees to cardinal directions.
    """
    directions = [
        "N", "NNO", "NO", "ONO", "O", "OSO", "SO", "SSO",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]

def fetch_stations(region):
    """
    Fetches all stations for a specified region using the meteostat API.
    """
    stations = Stations()
    return stations.region(region).fetch()

def load_weather_conditions(path):
    """
    Loads weather conditions from a CSV file into a dictionary.
    """
    df = pd.read_csv(path)
    return dict(zip(df['Code'], df['Wetterbedingung']))

def fetch_weather_data(stations, start_date, end_date):
    """
    Fetches hourly weather data for the specified stations and date range.
    """
    all_weather_data = pd.DataFrame()
    stations = stations.reset_index()
    condition_dict = load_weather_conditions("backend\DataGathering\ConditionCodesMeteoStat.csv")
    for index, station in stations.iterrows():
        hourly_data = Hourly(station['id'], start_date, end_date).fetch()
        if not hourly_data.empty:
            process_station_data(hourly_data, station, condition_dict)
            all_weather_data = pd.concat([all_weather_data, hourly_data])
        else:
            print(f"No data available for station {station['id']}")
    return all_weather_data

def process_station_data(data, station, condition_dict):
    """
    Processes and enhances station data with additional details and mapping.
    """
    data.reset_index(inplace=True)
    data['time'] = pd.to_datetime(data['time'])
    data['wdir'] = data['wdir'].apply(get_wind_direction)
    data['coco'] = data['coco'].map(condition_dict)
    data.rename(columns={
        'coco': 'Wetterbedingung',
        'time': 'Zeit',
        'temp': 'Temperatur',
        'dwpt': 'Taupunkt',
        'rhum': 'Luftfeuchtigkeit',
        'prcp': 'Niederschlagsmenge (letzte Stunde)',
        'snow': 'Schneefallmenge (letzte Stunde)',
        'wdir': 'Windrichtung',
        'wspd': 'Windgeschwindigkeit',
        'wpgt': 'Windböen',
        'pres': 'Luftdruck',
        'tsun': 'Sonneneinstrahlungsdauer'
    }, inplace=True)
    data['station_id'] = station['id']
    data['name'] = station['Ort']
    data['region'] = station['Region']

def save_to_mongodb(data):
    """
    Saves processed weather data to MongoDB.
    """
    db, collection = connect_mongodb()
    if db is not None and collection is not None:
        collection.insert_many(data.to_dict('records'))
        print("All weather data successfully stored in MongoDB.")

swiss_stations = fetch_stations("CH")
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 5, 3, 12, 00, 00)
weather_data = fetch_weather_data(swiss_stations, start_date, end_date)
weather_data.to_csv("complete_weather_data.csv")
save_to_mongodb(weather_data)