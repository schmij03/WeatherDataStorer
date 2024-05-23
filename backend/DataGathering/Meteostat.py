import pandas as pd
from meteostat import Hourly

def fetch_weather_data(stations, start_date, end_date):
    """
    Ruft stündliche Wetterdaten für die angegebenen Stationen und den Datumsbereich ab.
    """
    weather_data_list = []

    stations = stations.reset_index(drop=True)

    for index, station in stations.iterrows():
        try:
            hourly_data = Hourly(station['id_meteostat'], start_date, end_date).fetch()
            
            if not hourly_data.empty:
                process_station_data(hourly_data, station)
                weather_data_list.append(hourly_data)
            else:
                print(f"No data available for station {station['id_meteostat']}")

        except Exception as e:
            print(f"Error fetching data for station {station['id_meteostat']}: {str(e)}")
    
    all_weather_data = pd.concat(weather_data_list, ignore_index=True) if weather_data_list else pd.DataFrame()
    
    return all_weather_data

def process_station_data(data, station):
    """
    Verarbeitet und erweitert die Stationsdaten mit zusätzlichen Details und Zuordnungen.
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
        'wspd': 'Windgeschwindigkeit in km/h',
        'wpgt': 'Windböen',
        'pres': 'Luftdruck',
        'tsun': 'Sonneneinstrahlungsdauer'
    }, inplace=True)
    data['station_id'] = station['id_meteostat']
    data['Ort'] = station['Ort']
    data['Region'] = station['Region']
    data['Koordinaten'] = station['Koordinaten']
    data['Land'] = station['country']
