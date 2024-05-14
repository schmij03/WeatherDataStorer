import pandas as pd
import schedule
import time
from backend.DataGathering.GeoAdminData import main
from backend.DataGathering.Meteostat import fetch_weather_data
from datetime import datetime
from backend.DataGathering.openweathermap import fetch_weatherdata_hour, fetch_weatherdata_current
from backend.DataGathering.mongodb_connection import save_to_mongodb

def job():
    empty_df = pd.read_csv('backend/DataGathering/empty_weather_data.csv')

    # Call the main function to obtain a time value
    time_str, weather_geoadmin_df, geoadmin_stations = main()
    print(f"Original time (string): {time_str}")

    # Convert the string into a datetime object using `datetime.strptime`
    time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    print(f"Converted time (datetime): {time_obj}")

    # Round to the nearest whole hour by zeroing out minutes and seconds
    rounded_hour = time_obj.replace(minute=0, second=0, microsecond=0)
    print(f"Rounded to the nearest whole hour: {rounded_hour}")
    rounded_hour_csv = datetime.strptime(str(rounded_hour), "%Y-%m-%d %H:%M:%S").strftime("%Y%m%dT%H%M%S")

    weather_geoadmin_df.to_csv(f'backend/DataGathering/Files/GeoAdminData_{rounded_hour_csv}.csv', index=False)
    print('GeoAdmin data saved successfully.')

    # Read Stations from csv file
    allstations = pd.read_csv('backend/DataGathering/AllStations_with_location_info.csv')

    def merge_data(data):
        suffixes = ('_meteom', '_meteos', '_openweather', '_geoadmin')
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

        data = data.drop_duplicates(subset=['Koordinaten'])
        return data

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

    def get_hourly_dataCH(allstations, rounded_hour):
        current_hour = datetime.now().hour
        allstations = allstations[allstations['country'] == 'CH']
        stations_meteostat = allstations[allstations['id_meteostat'].notna()]
        stations_openweather = allstations[allstations['id_openweathermap'].notna()]
        all_weather_data = empty_df
        if current_hour % 2 == 0:
            meteostat_data = fetch_weather_data(stations_meteostat, rounded_hour, rounded_hour)
            openweather_data = fetch_weatherdata_hour(stations_openweather, rounded_hour)

            all_weather_data = pd.merge(weather_geoadmin_df, openweather_data, on='Koordinaten', how='outer', suffixes=('_geoadmin', '_openweather'))
            all_weather_data = pd.merge(all_weather_data, meteostat_data, on='Koordinaten', how='outer', suffixes=('', '_meteos'))
            all_weather_data = all_weather_data.drop_duplicates()
        else:
            meteostat_data = fetch_weather_data(stations_meteostat, rounded_hour, rounded_hour)
            all_weather_data = pd.merge(weather_geoadmin_df, meteostat_data, on='Koordinaten', how='outer', suffixes=('_geoadmin', '_meteos'))
            all_weather_data = all_weather_data.drop_duplicates()
        # drop first row of all_weather_data
        all_weather_data = all_weather_data[1:]
        all_weather_data = merge_data(all_weather_data)
        all_weather_data['Land'] = "CH"
        all_weather_data = all_weather_data.drop(columns=['Zeit'])
        all_weather_data['Zeit'] = rounded_hour
        return all_weather_data

    pd_test = get_hourly_dataCH(allstations, rounded_hour)
    print("Starting to save data to MongoDB")
    save_to_mongodb(pd_test)
    print('CH data saved successfully.')

    pd_test = get_current_data(allstations)
    print("Starting to save data to MongoDB")
    save_to_mongodb(pd_test)
    print('Not CH data saved successfully.')

# Schedule the job every hour
schedule.every().hour.at(":17").do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
