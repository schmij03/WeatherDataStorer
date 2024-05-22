import pandas as pd
import googlemaps
import json
from getStationInformations import meteostat_filtered, openweathermap_filtered
from GeoAdminData import main
from backend.DataGathering.region_mapping import get_region

# Daten laden
data2 = meteostat_filtered
data3 = openweathermap_filtered
time_str, weather_geoadmin_df, geoadmin_stations = main()
data = geoadmin_stations

# Zusammenführen der DataFrames
df_combined_filtered = pd.merge(data, data2, on='Koordinaten', how='outer', suffixes=('_geoadmin', '_meteos'))
df_combined_filtered = pd.merge(df_combined_filtered, data3, on='Koordinaten', how='outer', suffixes=('', '_openweather'))

# Generieren einer Liste der Spalten, die mit den angegebenen Suffixen enden
suffixes = ('_meteos', '_openweather', '_geoadmin')
to_consolidate = [col.split(suffix)[0] for col in df_combined_filtered.columns for suffix in suffixes if col.endswith(suffix)]

# Entfernen der Duplikate aus der Liste
to_consolidate = list(set(to_consolidate))

# Zusammenführen der Spalten mit den Suffixen
for col in to_consolidate:
    main_col = df_combined_filtered[col] if col in df_combined_filtered.columns else pd.Series()
    for suffix in suffixes:
        suffix_col = col + suffix
        if suffix_col in df_combined_filtered.columns:
            main_col = main_col.fillna(df_combined_filtered[suffix_col])
    df_combined_filtered[col] = main_col
    df_combined_filtered.drop([col + suffix for suffix in suffixes if (col + suffix) in df_combined_filtered.columns], axis=1, inplace=True)

df_combined_filtered = df_combined_filtered.drop_duplicates(subset=['Koordinaten'])

# Google Maps Client initialisieren
with open('backend/DataGathering/pwd.json') as f:
    credentials = json.load(f)
    google_maps_key = credentials['google_api_key']

gmaps = googlemaps.Client(key=google_maps_key)

def get_location_info(latlon):
    # Überprüfen, ob die Koordinaten gültig sind
    try:
        lat, lon = map(float, latlon.split(','))
        if pd.isna(lat) or pd.isna(lon) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Ungültige Koordinaten")
    except (ValueError, TypeError):
        print(f"Fehler: Ungültige Koordinaten {latlon}")
        return {"country": "Unknown", "city": "Unknown"}

    try:
        # Verwendung der Google Maps API zur Umkehrsuche der Geokodierung
        result = gmaps.reverse_geocode((lat, lon))
        if result:
            country = region = city = 'Unknown'
            for component in result[0]['address_components']:
                if 'country' in component['types']:
                    country = component['short_name'].upper()
                if 'locality' in component['types']:
                    city = component['long_name']
            return {"country": country,  "city": city}
    except Exception as e:
        print(f"Fehler bei der API-Anfrage: {e} - mit Koordinaten {latlon}")
        return {"country": "Unknown", "city": "Unknown"}

    return {"country": "Unknown", "city": "Unknown"}

def update_location_info(row):
    # Sicherstellen, dass alle notwendigen Spalten vorhanden sind
    for col in ['country', 'city']:
        if pd.isna(row[col]):
            row[col] = None

    # Holen der neuen Daten aus der Funktion
    new_data = get_location_info(row["Koordinaten"])
    
    # Überprüfen und Aktualisieren der Daten
    if row['country'] is None or row['country'] != new_data['country']:
        row['country'] = new_data['country']
    if row['city'] is None or row['city'] != new_data['city']:
        row['city'] = new_data['city']

    return pd.Series([row['country'], row['city']], index=['country' 'city'])

# Sicherstellen, dass die Spalten vorhanden sind, bevor die apply-Funktion aufgerufen wird
for col in ['country', 'city']:
    if col not in df_combined_filtered.columns:
        df_combined_filtered[col] = None

# Standortinformationen aktualisieren
df_combined_filtered[['country', 'city']] = df_combined_filtered.apply(update_location_info, axis=1)

df_combined_filtered=df_combined_filtered.apply(get_region, axis=1)
# Speichern des aktualisierten DataFrames in eine CSV-Datei
output_path = 'backend/DataGathering/AllStations_with_location_info.csv'
df_combined_filtered.to_csv(output_path, index=False)
