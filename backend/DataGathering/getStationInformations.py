import json
import pandas as pd
from meteostat import Stations
from shapely.geometry import Polygon, Point
import requests
import gzip

# Polygon-Koordinaten aus JSON-Datei laden und Polygon-Objekt erstellen
with open('backend/DataGathering/rendercoordinates.json', 'r') as file:
    coords = json.load(file)['rendercoordinates']
    polygon = Polygon([(coord['lat'], coord['lng']) for coord in coords])

def is_in_polygon(station):
    # Prüfen, ob eine Station innerhalb des definierten Polygons liegt
    point = Point(station['latitude'], station['longitude'])
    return polygon.contains(point)

def fetch_and_prepare_stations(countries):
    data_frames = []
    for country in countries:
        try:
            # Stationen für das jeweilige Land abrufen
            stations = Stations().region(country).fetch()
            if stations.empty:
                continue  # Überspringen, wenn keine Daten verfügbar sind
            data_frames.append(stations)
        except Exception as e:
            # Optional: Fehler protokollieren
            pass

    if not data_frames:
        return pd.DataFrame()  # Leeres DataFrame zurückgeben, wenn keine Daten abgerufen wurden

    # Alle DataFrames zusammenführen, Index zurücksetzen und Spalten umformatieren
    result = pd.concat(data_frames)
    result['Location Lat,Lon'] = result['latitude'].astype(str) + ',' + result['longitude'].astype(str)
    return result

# Liste der Länder und Ländercodes
countries = ["switzerland", "italy", "austria", "germany", "france"]
country_codes = ['CH', 'DE', 'AT', 'IT', 'FR']
stations = fetch_and_prepare_stations(country_codes)

stations = stations.reset_index()

# Stationen innerhalb des Polygons filtern
stations['In Polygon'] = stations.apply(is_in_polygon, axis=1)
filtered_stations = stations[stations['In Polygon']].drop(columns='In Polygon')
filtered_stations = filtered_stations.rename(columns={'name': 'Ort', 'id': 'id_meteostat', 'Location Lat,Lon': 'Koordinaten'})

# Unnötige Spalten entfernen und gefilterte Stationen speichern
meteostat_filtered = filtered_stations.drop(columns=['latitude', 'longitude', 'region', 'hourly_start', 'hourly_end', 'daily_start', 'daily_end', 'monthly_start', 'monthly_end'])
meteostat_filtered.to_csv('backend/DataGathering/meteostat_stations_filtered.csv', index=False)

def download_and_create_dataframe(url, country_codes):
    response = requests.get(url)
    if response.status_code == 200:
        compressed_file = response.content
        decompressed_file = gzip.decompress(compressed_file)
        json_data = json.loads(decompressed_file)
        filtered_data = [city for city in json_data if city['country'] in country_codes]
        df = pd.DataFrame(filtered_data)
        df['longitude'] = df['coord'].apply(lambda x: x['lon'])
        df['latitude'] = df['coord'].apply(lambda x: x['lat'])
        df.drop('coord', axis=1, inplace=True)
        return df
    else:
        print("Fehler beim Herunterladen der Datei:", response.status_code)
        return None

# URL der GZIP-Datei
url_openweathermap = "https://bulk.openweathermap.org/sample/city.list.json.gz"

# DataFrame erstellen und Stationen nach Polygon filtern
openweathermap_df = download_and_create_dataframe(url_openweathermap, country_codes)

openweathermap_df['in_polygon'] = openweathermap_df.apply(is_in_polygon, axis=1)
openweathermap_filtered = openweathermap_df[openweathermap_df['in_polygon']].drop(columns='in_polygon')
openweathermap_filtered = openweathermap_filtered.drop(columns={'state'})
openweathermap_filtered['Koordinaten'] = openweathermap_filtered['latitude'].astype(str) + ',' + openweathermap_filtered['longitude'].astype(str)
openweathermap_filtered = openweathermap_filtered.drop(columns=['latitude', 'longitude'])
openweathermap_filtered = openweathermap_filtered.reset_index(drop=True).rename(columns={'id': 'id_openweathermap', 'name': 'Ort'})

# Gefilterte Daten in CSV speichern
openweathermap_filtered.to_csv('backend/DataGathering/openweathermap_stations_filtered.csv', index=False)

print("Alle Stationen wurden gefiltert und in CSV-Dateien gespeichert.")