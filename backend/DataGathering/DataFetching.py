import pandas as pd
from GeoAdminData import main
from Meteostat import fetch_weather_data
from datetime import datetime
from openweathermap import fetch_weatherdata

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
allstations=pd.read_csv('backend/DataGathering/AllStations_with_location_info.csv')


stations_meteostat = allstations[allstations['id_meteostat'].notna()]
meteostat_final = fetch_weather_data(stations_meteostat, rounded_hour, rounded_hour)
meteostat_final.to_csv(f'backend/DataGathering/Files/Meteostat_{rounded_hour_csv}.csv', index=False)
print("Meteostat data saved successfully.")

stations_openweather = allstations[allstations['id_openweathermap'].notna()]
openweather_final = fetch_weatherdata(stations_openweather, rounded_hour)
openweather_final.to_csv(f'backend/DataGathering/Files/OpenWeatherMap_{rounded_hour_csv}.csv', index=False)
print("OpenWeather data saved successfully.")