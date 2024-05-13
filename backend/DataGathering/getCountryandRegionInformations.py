import pandas as pd
import googlemaps
import json
from getStationInformations import meteostat_filtered, meteomatics_filtered, openweathermap_filtered
from GeoAdminData import main
from mongodb_connection import save_to_mongodb
# Load the data
data2 = meteomatics_filtered
data3 = meteostat_filtered
data4 = openweathermap_filtered
time_str, weather_geoadmin_df, geoadmin_stations = main()
data = geoadmin_stations
data = data.dropna(subset=['Location Lat,Lon'])
data.to_csv('backend/DataGathering/GeoAdminStationsTEST.csv', index=False)
# DataFrames zusammenführen
df_combined_filtered = pd.merge(data, data2, on='Location Lat,Lon', how='outer', suffixes=('_geoadmin', '_meteom'))
df_combined_filtered = pd.merge(df_combined_filtered, data3, on='Location Lat,Lon', how='outer', suffixes=('', '_meteos'))
df_combined_filtered = pd.merge(df_combined_filtered, data4, on='Location Lat,Lon', how='outer', suffixes=('', '_openweather'))

# Konsolidieren doppelter Spalten (z.B. 'elevation_x' und 'elevation_y')
# Generieren einer Liste der Spalten, die mit '_meteomatics', '_meteostat' und '_openweathermap' enden
suffixes = ('_meteom', '_meteos', '_openweather', '_geoadmin')
# Generieren einer Liste der Spalten, die mit '_meteomatics', '_meteostat' oder '_openweathermap' enden
to_consolidate = [col.split(suffix)[0] for col in df_combined_filtered.columns for suffix in suffixes if col.endswith(suffix)]

# Entfernen der Duplikate aus der Liste
to_consolidate = list(set(to_consolidate))

# Zusammenführen der Spalten mit den Suffixen
for col in to_consolidate:
    # Initialisieren des main_col mit der Basisversion der Spalte, falls vorhanden
    main_col = df_combined_filtered[col] if col in df_combined_filtered.columns else pd.Series()
    # Konsolidieren der Werte aus den verschiedenen DataFrames
    for suffix in suffixes:
        suffix_col = col + suffix
        if suffix_col in df_combined_filtered.columns:
            main_col = main_col.fillna(df_combined_filtered[suffix_col])
    # Zuweisen der konsolidierten Daten zur Basis-Spalte
    df_combined_filtered[col] = main_col
    # Entfernen der alten Spalten mit Suffixen
    df_combined_filtered.drop([col + suffix for suffix in suffixes if (col + suffix) in df_combined_filtered.columns], axis=1, inplace=True)

df_combined_filtered = df_combined_filtered.drop_duplicates(subset=['Location Lat,Lon'])
df_combined_filtered.to_csv('backend/DataGathering/AllStationswithNaN.csv', index=False)
# Initialize the Google Maps Client
with open('backend/DataGathering/pwd.json') as f:
    credentials = json.load(f)
    google_maps_key = credentials['google_api_key']

gmaps = googlemaps.Client(key=google_maps_key)


def get_location_info(latlon):
    # Überprüfen, ob latlon überhaupt einen sinnvollen Wert enthält
    try:
        lat, lon = map(float, latlon.split(','))
        # Prüfen, ob lat und lon gültige Koordinaten sind
        if pd.isna(lat) or pd.isna(lon) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Ungültige Koordinaten")
    except (ValueError, TypeError):
        print(f"Fehler: Ungültige Koordinaten {latlon}")
        return {"country": "Unknown", "region": "Unknown", "city": "Unknown"}

    try:
        # Verwendung der Google Maps API
        result = gmaps.reverse_geocode((lat, lon))
        if result:
            country = region = city = 'Unknown'
            for component in result[0]['address_components']:
                if 'country' in component['types']:
                    country = component['short_name'].upper()
                if 'administrative_area_level_1' in component['types']:
                    region = component['long_name']
                if 'locality' in component['types']:
                    city = component['long_name']
            return {"country": country, "region": region, "city": city}
    except Exception as e:
        print(f"Fehler bei der API-Anfrage: {e} - mit Koordinaten {latlon}")
        return {"country": "Unknown", "region": "Unknown", "city": "Unknown"}

    return {"country": "Unknown", "region": "Unknown", "city": "Unknown"}


def update_location_info(row):
    # Stelle sicher, dass alle notwendigen Spalten vorhanden sind
    for col in ['country', 'region', 'city']:
        if pd.isna(row[col]):
            row[col] = None

    # Holen der neuen Daten aus der Funktion
    new_data = get_location_info(row["Location Lat,Lon"])
    
    # Überprüfung und Aktualisierung der Daten
    # Vergleiche mit `None` sind sicher, auch wenn `row['country']` NA ist
    if row['country'] is None or row['country'] != new_data['country']:
        row['country'] = new_data['country']
    if row['region'] is None or row['region'] != new_data['region']:
        row['region'] = new_data['region']
    if row['city'] is None or row['city'] != new_data['city']:
        row['city'] = new_data['city']

    return pd.Series([row['country'], row['region'], row['city']], index=['country', 'region', 'city'])

# Stelle sicher, dass die Spalten vorhanden sind, bevor die apply-Funktion aufgerufen wird
for col in ['country', 'region', 'city']:
    if col not in df_combined_filtered.columns:
        df_combined_filtered[col] = None

# Update Location Information
df_combined_filtered[['country', 'region', 'city']] = df_combined_filtered.apply(update_location_info, axis=1)

# Save the updated DataFrame back to a CSV
output_path = 'backend/DataGathering/AllStations_with_location_info.csv'
df_combined_filtered.to_csv(output_path, index=False)
