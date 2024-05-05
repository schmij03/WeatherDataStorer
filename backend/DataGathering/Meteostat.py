from datetime import datetime
import pandas as pd
from meteostat import Stations, Hourly
from mongodb_connection import connect_mongodb


def fetch_stations(region):
    """
    Fetches all stations for a specified region using the meteostat API.
    """
    stations = Stations()
    return stations.region(region).fetch()



def fetch_weather_data(stations, start_date, end_date):
    """
    Fetches hourly weather data for the specified stations and date range.
    """
    all_weather_data = pd.DataFrame()
    stations = stations.reset_index()
    
    for index, station in stations.iterrows():
        hourly_data = Hourly(station['id'], start_date, end_date).fetch()
        if not hourly_data.empty:
            process_station_data(hourly_data, station)
            all_weather_data = pd.concat([all_weather_data, hourly_data])
        else:
            print(f"No data available for station {station['id']}")
    return all_weather_data

def process_station_data(data, station):
    """
    Processes and enhances station data with additional details and mapping.
    """
    data.reset_index(inplace=True)
    data['time'] = pd.to_datetime(data['time'])
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
    data['Ort'] = station['name']
    data['Region'] = station['region']

def save_to_mongodb(data):
    """
    Saves processed weather data to MongoDB.
    """
    db, collection = connect_mongodb()
    if db is not None and collection is not None:
        collection.insert_many(data.to_dict('records'))
        print("All weather data successfully stored in MongoDB.")
