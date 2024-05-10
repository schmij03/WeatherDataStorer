import json
import pandas as pd
from meteostat import Stations
from shapely.geometry import Polygon, Point

# Load and prepare polygon coordinates
with open('backend/DataGathering/rendercoordinates.json', 'r') as file:
    coords = json.load(file)['rendercoordinates']
    polygon = Polygon([(coord['lat'], coord['lng']) for coord in coords])

# Helper function to check if a station is within the polygon
def is_in_polygon(station):
    point = Point(station['latitude'], station['longitude'])
    return polygon.contains(point)

def fetch_and_prepare_stations(countries):
    data_frames = []
    for country in countries:
        try:
            # Fetch stations and ensure they are fetched correctly
            stations = Stations().region(country).fetch()
            if stations.empty:
                continue  # Skip if no data is available
            data_frames.append(stations)
        except Exception as e:
            # Optionally log the error to a file or logging system
            pass

    if not data_frames:
        return pd.DataFrame()  # Return an empty DataFrame if no data was fetched

    # Concatenate all DataFrames, reset index, and reformat columns
    result = pd.concat(data_frames)
    result['Location Lat,Lon'] = result['latitude'].astype(str) + ',' + result['longitude'].astype(str)
    return result


# List of countries
countries = ['CH', 'DE', 'AT', 'IT', 'FR']
stations = fetch_and_prepare_stations(countries)

stations = stations.reset_index()

# Filter stations inside the polygon
stations['In Polygon'] = stations.apply(is_in_polygon, axis=1)

filtered_stations = stations[stations['In Polygon']].drop(columns='In Polygon')
filtered_stations = filtered_stations.rename(columns={'name': 'Ort', 'id': 'id_meteostat'})

filtered_stations = filtered_stations.drop(columns=['latitude', 'longitude', 'region', 'hourly_start', 'hourly_end', 'daily_start', 'daily_end', 'monthly_start', 'monthly_end'])
# Save to CSV
filtered_stations.to_csv('meteostat_stations_filtered.csv')
import json
import pandas as pd
from meteostat import Stations
from shapely.geometry import Polygon, Point

# Load and prepare polygon coordinates
with open('backend/DataGathering/rendercoordinates.json', 'r') as file:
    coords = json.load(file)['rendercoordinates']
    polygon = Polygon([(coord['lat'], coord['lng']) for coord in coords])

# Helper function to check if a station is within the polygon
def is_in_polygon(station):
    point = Point(station['latitude'], station['longitude'])
    return polygon.contains(point)

def fetch_and_prepare_stations(countries):
    data_frames = []
    for country in countries:
        try:
            # Fetch stations and ensure they are fetched correctly
            stations = Stations().region(country).fetch()
            if stations.empty:
                continue  # Skip if no data is available
            data_frames.append(stations)
        except Exception as e:
            # Optionally log the error to a file or logging system
            pass

    if not data_frames:
        return pd.DataFrame()  # Return an empty DataFrame if no data was fetched

    # Concatenate all DataFrames, reset index, and reformat columns
    result = pd.concat(data_frames)
    result['Location Lat,Lon'] = result['latitude'].astype(str) + ',' + result['longitude'].astype(str)
    return result


# List of countries
countries = ['CH', 'DE', 'AT', 'IT', 'FR']
stations = fetch_and_prepare_stations(countries)

stations = stations.reset_index()

# Filter stations inside the polygon
stations['In Polygon'] = stations.apply(is_in_polygon, axis=1)

filtered_stations = stations[stations['In Polygon']].drop(columns='In Polygon')
filtered_stations = filtered_stations.rename(columns={'name': 'Ort', 'id': 'id_meteostat'})

filtered_stations = filtered_stations.drop(columns=['latitude', 'longitude', 'region', 'hourly_start', 'hourly_end', 'daily_start', 'daily_end', 'monthly_start', 'monthly_end'])
# Save to CSV
filtered_stations.to_csv('meteostat_stations_filtered.csv')
