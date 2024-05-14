import pandas as pd
from meteostat import Hourly

def fetch_weather_data(stations, start_date, end_date):
    """
    Fetches hourly weather data for the specified stations and date range.
    """
    # Initialisieren einer Liste, um DataFrames zu sammeln
    weather_data_list = []

    # Reset des Indexes für einfacheren Zugriff
    stations = stations.reset_index(drop=True)

    for index, station in stations.iterrows():
        try:
            # Abrufen der stündlichen Wetterdaten
            hourly_data = Hourly(station['id_meteostat'], start_date, end_date).fetch()
            
            if not hourly_data.empty:
                # Optional: Verarbeiten der Station-Daten
                process_station_data(hourly_data, station)
                
                # Hinzufügen des DataFrames zur Liste
                weather_data_list.append(hourly_data)
            else:
                print(f"No data available for station {station['id_meteostat']}")

        except Exception as e:
            print(f"Error fetching data for station {station['id_meteostat']}: {str(e)}")
    
    # Zusammenführen aller gesammelten DataFrames
    all_weather_data = pd.concat(weather_data_list, ignore_index=True) if weather_data_list else pd.DataFrame()
    
    return all_weather_data


def process_station_data(data, station):
    """
    Processes and enhances station data with additional details and mapping.
    """
    data.reset_index(inplace=True)
    data['time'] = pd.to_datetime(data['time'], format='%Y-%m-%d %H:%M:%S')
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
    data['station_id'] = station['id_meteostat']
    data['Ort'] = station['Ort']
    data['Region'] = station['region']
    data['Koordinaten'] = station['Location Lat,Lon']
    data['Land'] = station['country']