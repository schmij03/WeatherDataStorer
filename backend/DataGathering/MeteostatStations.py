from meteostat import Stations, Hourly
import pandas as pd

def fetch_stations_switzerland():
    stations = Stations()
    swiss_stations = stations.region('CH').fetch()
    return swiss_stations

def fetch_weather_data(station_ids, start_date, end_date):
    all_weather_data = pd.DataFrame()
    for station_id in station_ids:
        hourly = Hourly(station=station_id)
        hourly = hourly.fetch(start=start_date, end=end_date)
        if not hourly.empty:
            hourly['station_id'] = station_id  # Füge die Stations-ID als eine Spalte hinzu
            all_weather_data = all_weather_data.append(hourly, ignore_index=True)
    return all_weather_data

# Funktionen verwenden:
swiss_stations = fetch_stations_switzerland()

# Überprüfe die Spaltennamen und die ersten Zeilen des DataFrame
print(swiss_stations.columns)
print(swiss_stations.head())

# Stelle sicher, dass die Spalte 'id' oder ein ähnlicher Spaltenname vorhanden ist
if 'id' in swiss_stations.columns:
    station_ids = swiss_stations['id'].tolist()  # Zugriff auf die Spalte 'id' für die Station-IDs
else:
    print("Die Spalte 'id' existiert nicht. Überprüfe die Spaltennamen.")
    # Füge hier alternative Spaltennamen oder Handhabungen hinzu, falls nötig

# Stelle sicher, dass station_ids definiert wurde, bevor du weitermachst
if 'station_ids' in locals():
    complete_weather_data = fetch_weather_data(station_ids, '2023-01-01', '2023-12-31')
    complete_weather_data.to_csv('complete_weather_data.csv', index=False)
else:
    print("Station IDs wurden nicht korrekt definiert. Kann nicht fortfahren.")
