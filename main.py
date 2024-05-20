import pandas as pd
import schedule
import time
from backend.DataGathering.GeoAdminData import main
from backend.DataGathering.Meteostat import fetch_weather_data
from datetime import datetime
from backend.DataGathering.openweathermap import fetch_weatherdata_hour, fetch_weatherdata_current
from backend.DataGathering.mongodb_connection import save_to_mongodb
from backend.DataGathering.region_mapping import get_region
#from backend.DataGathering.pollendata import collect_pollen_forecasts

def job():
    # Leeren DataFrame aus CSV-Datei laden
    empty_df = pd.read_csv('backend/DataGathering/empty_weather_data.csv')

    # Hauptfunktion aufrufen, um Zeitwert und GeoAdmin-Daten zu erhalten
    time_str, weather_geoadmin_df, geoadmin_stations = main()
    print(f"Original time (string): {time_str}")

    # Konvertieren des Zeitwerts von String zu datetime-Objekt
    time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    print(f"Converted time (datetime): {time_obj}")

    # Auf die nächste volle Stunde runden
    rounded_hour = time_obj.replace(minute=0, second=0, microsecond=0)
    print(f"Rounded to the nearest whole hour: {rounded_hour}")
    rounded_hour_csv = datetime.strptime(str(rounded_hour), "%Y-%m-%d %H:%M:%S").strftime("%Y%m%dT%H%M%S")
    print('GeoAdmin data gathered successfully.')

    # Alle Stationen aus CSV-Datei laden
    allstations = pd.read_csv('backend/DataGathering/AllStations_with_location_info.csv')

    # Funktion zum Zusammenführen von Daten
    def merge_data(data):
        suffixes = ('_meteos', '_openweather', '_geoadmin')
        to_consolidate = list({col.split(suffix)[0] for suffix in suffixes for col in data.columns if col.endswith(suffix)})

        for base_col in to_consolidate:
            relevant_columns = [base_col + suffix for suffix in suffixes if (base_col + suffix) in data.columns]

            if base_col in ['Ort', 'Koordinaten', 'Datum', 'Zeit', 'Wetterbedingung', 'station_id', 'Region']:
                main_col = pd.concat([data[col] for col in relevant_columns], axis=1).bfill(axis=1).iloc[:, 0].infer_objects()
                data[base_col] = main_col
            elif all(pd.api.types.is_numeric_dtype(data[col]) for col in relevant_columns):
                data[base_col] = pd.concat([data[col] for col in relevant_columns], axis=1).mean(axis=1)
            else:
                main_col = pd.concat([data[col] for col in relevant_columns], axis=1).bfill(axis=1).iloc[:, 0].infer_objects()
                data[base_col] = main_col

            data.drop(relevant_columns, axis=1, inplace=True)
        data = data.drop(columns=['Datum'])
        data = data.drop_duplicates(subset=['Koordinaten'])
        return data

    # Funktion zum Abrufen aktueller Wetterdaten
    def get_current_data(allstations):
        allstations = allstations[allstations['country'] != 'CH']
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rounded_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S").replace(minute=0, second=0, microsecond=0)
        stations_meteostat = allstations[allstations['id_meteostat'].notna()]
        meteostat_final = fetch_weather_data(stations_meteostat, rounded_time, rounded_time)

        stations_openweather = allstations[allstations['id_openweathermap'].notna()]
        openweather_final = fetch_weatherdata_current(stations_openweather)
        all_weather_data = empty_df
        all_weather_data = pd.merge(weather_geoadmin_df, openweather_final, on='Koordinaten', how='outer', suffixes=('_meteos', '_openweather'))
        all_weather_data = all_weather_data.drop_duplicates()
        all_weather_data = all_weather_data[1:]
        all_weather_data = merge_data(all_weather_data)
        all_weather_data = all_weather_data.drop(columns=['Zeit'])
        all_weather_data['Zeit'] = rounded_time
        return all_weather_data

    # Funktion zum Abrufen stündlicher Wetterdaten für die Schweiz
    def get_hourly_dataCH(allstations, rounded_hour):
        current_hour = datetime.now().hour
        allstations = allstations[allstations['country'] == 'CH']
        stations_meteostat = allstations[allstations['id_meteostat'].notna()]
        stations_openweather = allstations[allstations['id_openweathermap'].notna()]
        all_weather_data = empty_df
        if current_hour % 2 != 0:
            meteostat_data = fetch_weather_data(stations_meteostat, rounded_hour, rounded_hour)
            openweather_data = fetch_weatherdata_hour(stations_openweather, rounded_hour)

            all_weather_data = pd.merge(weather_geoadmin_df, openweather_data, on='Koordinaten', how='outer', suffixes=('_geoadmin', '_openweather'))
            all_weather_data = pd.merge(all_weather_data, meteostat_data, on='Koordinaten', how='outer', suffixes=('', '_meteos'))
            all_weather_data = all_weather_data.drop_duplicates()
        else:
            meteostat_data = fetch_weather_data(stations_meteostat, rounded_hour, rounded_hour)
            all_weather_data = pd.merge(weather_geoadmin_df, meteostat_data, on='Koordinaten', how='outer', suffixes=('_geoadmin', '_meteos'))
            all_weather_data = all_weather_data.drop_duplicates()
        all_weather_data = all_weather_data[1:]
        all_weather_data = merge_data(all_weather_data)
        all_weather_data['Land'] = "CH"
        all_weather_data = all_weather_data.drop(columns=['Zeit'])
        all_weather_data['Zeit'] = rounded_hour
        all_weather_data = all_weather_data.drop(columns=['Region'])
        all_weather_data=all_weather_data.apply(get_region, axis=1)
        return all_weather_data
    
    # Stündliche Wetterdaten für die Schweiz abrufen
    pd_CH = get_hourly_dataCH(allstations, rounded_hour)
    print("Starting to save data to MongoDB")
    save_to_mongodb(pd_CH)
    print('CH data saved successfully.')

    # Aktuelle Wetterdaten abrufen
    pd_rest = get_current_data(allstations)
    print("Starting to save data to MongoDB")
    save_to_mongodb(pd_rest)
    print('Not CH data saved successfully.')


# Job jede Stunde ausführen
schedule.every().hour.at(":19").do(job)

# Skript am Laufen halten
while True:
    schedule.run_pending()
    time.sleep(1)
