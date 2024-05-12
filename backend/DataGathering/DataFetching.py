import pandas as pd
from GeoAdminData import main
from Meteostat import fetch_weather_data
from datetime import datetime, timedelta
from openweathermap import get_weather

# Call the main function to obtain a time value
time_str, weather_geoadmin_df, geoadmin_stations = main()  # This should return a string representing a timestamp
print(f"Original time (string): {time_str}")

# Convert the string into a datetime object using `datetime.strptime`
time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
print(f"Converted time (datetime): {time_obj}")

# Round to the nearest whole hour by zeroing out minutes and seconds
rounded_hour = time_obj.replace(minute=0, second=0, microsecond=0)
print(f"Rounded to the nearest whole hour: {rounded_hour}")

# Read Stations from csv file
allstations=pd.read_csv('backend/DataGathering/AllStations_with_location_info.csv')

stations_meteostat = allstations[allstations['id_meteostat'] != ""]
for index, stationmeteostat in stations_meteostat.iterrows():
    # Prüfen, ob das 'id_meteostat' Feld leer ist
    weather_meteostat_df = fetch_weather_data(stationmeteostat, rounded_hour, rounded_hour)
        # Füge das Ergebnis zum resultierenden DataFrame hinzu
    meteostat_final = pd.concat([meteostat_final, weather_meteostat_df], ignore_index=True)

meteostat_final.to_csv('backend/DataGathering/Meteostat{rounded_hour}.csv', index=False)


for index, stationopenweather in allstations.iterrows():
    # Prüfen, ob das 'id_openweather' Feld leer ist
    if stationopenweather['id_openweather'] != "":
        # Wenn nicht leer, Funktion aufrufen um Wetterdaten für die gesamte Station zu holen
        weather_openweather_df = get_weather(stationopenweather, rounded_hour, rounded_hour)
        
        # Füge das Ergebnis zum resultierenden DataFrame hinzu
        openweather_final = pd.concat([openweather_final, weather_openweather_df])

openweather_final.to_csv('backend/DataGathering/OpenWeather{rounded_hour}.csv', index=False)