from GeoAdminData import main
from Meteostat import fetch_stations, fetch_weather_data
from datetime import datetime, timedelta

# Call the main function to obtain a time value
time_str, weather_geoadmin_df, geoadmin_stations = main()  # This should return a string representing a timestamp
print(f"Original time (string): {time_str}")

# Convert the string into a datetime object using `datetime.strptime`
time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
print(f"Converted time (datetime): {time_obj}")

# Round to the nearest whole hour by zeroing out minutes and seconds
rounded_hour = time_obj.replace(minute=0, second=0, microsecond=0)
print(f"Rounded to the nearest whole hour: {rounded_hour}")

# Fetch the Swiss weather stations
stations = fetch_stations('CH')
print(stations)

# Fetch the weather data using the converted datetime object
weather_meteostat_df = fetch_weather_data(stations, rounded_hour, rounded_hour)
print(weather_meteostat_df.count())
weather_meteostat_df.to_csv(f"backend/DataGathering/Meteostat_{11}.csv", index=False)