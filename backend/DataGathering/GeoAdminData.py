import pandas as pd
import requests
from datetime import datetime
from io import StringIO
import numpy as np
from backend.DataGathering.region_mapping import get_region

# Funktion zum Laden von CSV-Daten aus einer Datei
def load_csv_data(filepath):
    try:
        return pd.read_csv(filepath, sep=',')
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        return None

# Funktion zum Abrufen von CSV-Daten von einer URL
def fetch_csv_data_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        response.encoding = 'iso-8859-1'  # Encoding für Sonderzeichen
        return pd.read_csv(StringIO(response.text), sep=';')
    else:
        print(f"Fehler beim Abrufen der Daten: {response.status_code}")
        return None

# Funktion zum Konvertieren eines Datumsformats
def convert_date(date_str):
    date_str = str(date_str)  # Sicherstellen, dass das Datum ein String ist
    return datetime.strptime(date_str, '%Y%m%d%H%M').strftime('%Y-%m-%d %H:%M:%S')

# Funktion zum Ersetzen von Spaltennamen basierend auf einer Zuordnung
def replace_column_names(df, mapping):
    df.columns = [mapping.get(col, col) for col in df.columns]
    return df

# Funktion zum Hinzufügen von Kantonsinformationen zu einem DataFrame
def add_canton_information(df, stations_df):
    df = df.merge(stations_df[['Abk.', 'Kanton']], left_on='Station/Location', right_on='Abk.', how='left')
    df.drop(columns=['Abk.'], inplace=True)
    return df

# Funktion zum Lesen einer Mapping-Datei und Umbenennen von Spalten gemäss der Zuordnung
def read_weather_mapping(mapping_filepath, weather_df):
    mapping_df = pd.read_csv(mapping_filepath)
    mapping_dict = dict(zip(mapping_df['Parameter'], mapping_df['Beschreibung']))
    data_df = weather_df
    data_df.rename(columns=mapping_dict, inplace=True)
    return data_df

# Funktion zum Laden von Parameterbeschreibungen aus einer CSV-Datei
def load_parameter_descriptions(filepath):
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        print(f"Fehler beim Laden der Parameterbeschreibungen: {e}")
        return pd.DataFrame()

# Hauptfunktion, die den gesamten Workflow steuert
def main():
    # URLs und Dateipfade zu den Daten
    weather_data_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv'
    rainfall_data_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA98.csv'
    foehn_data_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-foehn-10min/ch.meteoschweiz.messwerte-foehn-10min_de.csv'
    weather_data_description = r'backend/DataGathering/GeoAdmin/WetterdatenBeschreibung.csv'
    stations_description = r'backend/DataGathering/GeoAdmin/Stationsbeschreibungen.csv'
    rainfall_description = r'backend/DataGathering/GeoAdmin/Niederschlagsmenge.csv'

    # Abrufen von Daten aus verschiedenen Quellen
    rainfall_df = fetch_csv_data_from_url(rainfall_data_url)
    weather_df = fetch_csv_data_from_url(weather_data_url)
    foehn_df = fetch_csv_data_from_url(foehn_data_url)
    
    # Zuordnung für den Föhnindex
    mapping_foehn = {"Kein Föhn": 0, "Föhnmischluft": 1, "Föhn": 2}
    
    # Laden der Stationsdaten
    stations_df = load_csv_data(stations_description)

    def combine_latitude_longitude(row):
        return f"{row['Breitengrad']},{row['Längengrad']}"

    # Wenn die Daten erfolgreich geladen wurden, weitere Schritte durchführen
    if weather_df is not None and stations_df is not None:
        # Setzen der Indizes für effiziente Datenmanipulation
        foehn_df.set_index('Abk.', inplace=True)
        stations_df.set_index('Abk.', inplace=True)
        
        # Hinzufügen von Kantonsinformationen zu Wetter- und Niederschlagsdaten
        weather_df = weather_df.merge(stations_df[['Kanton', 'Stationstyp', 'Station', 'Breitengrad', 'Längengrad']], left_on='Station/Location', right_index=True, how='left')
        rainfall_df = rainfall_df.merge(stations_df[['Kanton', 'Stationstyp', 'Station', 'Breitengrad', 'Längengrad']], left_on='Station/Location', right_index=True, how='left')
        weather_df['Location Lat,Lon'] = weather_df.apply(combine_latitude_longitude, axis=1)
        rainfall_df['Location Lat,Lon'] = rainfall_df.apply(combine_latitude_longitude, axis=1)
        weather_df = weather_df.drop(columns=['Breitengrad', 'Längengrad'])
        rainfall_df = rainfall_df.drop(columns=['Breitengrad', 'Längengrad'])

        # Standardisieren der Stationstypen
        weather_df['Stationstyp'] = weather_df['Stationstyp'].apply(lambda x: 'W' if x == 'Wetterstation' else 'N')
        rainfall_df['Stationstyp'] = rainfall_df['Stationstyp'].apply(lambda x: 'W' if x == 'Wetterstation' else 'N')

        # Konvertieren der Daten und Bereinigen der Spalten
        weather_df['Datum'] = weather_df['Date'].apply(convert_date)
        rainfall_df['Datum'] = rainfall_df['Date'].apply(convert_date)
        weather_df.drop(columns=['Date'], inplace=True)
        rainfall_df.drop(columns=['Date'], inplace=True)

        # Ersetzen von NaN-Werten
        rainfall_df.replace('-', np.nan, inplace=True)
        weather_df.replace('-', np.nan, inplace=True)
        
        # Umbenennen der Spalten und Anwenden der Zuordnung
        weather_df.rename(columns={'Station/Location': 'Kürzel', 'Station': 'Ort'}, inplace=True)
        rainfall_df.rename(columns={'Station/Location': 'Kürzel', 'Station': 'Ort'}, inplace=True)
        weather_df = read_weather_mapping(weather_data_description, weather_df)
        rainfall_df = read_weather_mapping(rainfall_description, rainfall_df)
        
        # Hinzufügen des Föhnindex zu den Wetterdaten und Anwenden der Zuordnung
        weather_df = weather_df.merge(foehn_df[['Föhnindex']], left_on='Kürzel', right_index=True, how='left')
        weather_df['Föhnindex'] = weather_df['Föhnindex'].map(mapping_foehn)
        
        # Zusammenführen der Daten
        merged_df = pd.merge(weather_df, rainfall_df, on=['Kürzel', 'Datum', 'Kanton', 'Niederschlag; Zehnminutensumme', 'Stationstyp', 'Ort'], how='outer')

        # Anzeigen der aktuellen Uhrzeit
        current_time = datetime.now().strftime("%H:%M:%S")
        mapping = {
            "Lufttemperatur 2 m über Boden; Momentanwert": "Temperatur",
            "Taupunkt 2 m über Boden; Momentanwert": "Taupunkt",
            "Relative Luftfeuchtigkeit 2 m über Boden; Momentanwert": "Luftfeuchtigkeit",
            "Niederschlag; Zehnminutensumme": "Niederschlagsmenge (letzte Stunde)",
            "Windrichtung; Zehnminutenmittel": "Windrichtung",
            "Windgeschwindigkeit in km/h; Zehnminutenmittel": "Windgeschwindigkeit",
            "Böenspitze (Sekundenböe); Maximum": "Windböen",
            "Luftdruck auf Stationshöhe (QFE); Momentanwert": "Luftdruck",
            "Sonnenscheindauer; Zehnminutensumme": "Sonneneinstrahlungsdauer",
            "Globalstrahlung; Zehnminutenmittel": "Globalstrahlung",
            "Luftdruck reduziert auf Meeresniveau (QFF); Momentanwert": "Luftdruck reduziert auf Meeresniveau",
            "Luftdruck reduziert auf Meeresniveau mit Standardatmosphäre (QNH); Momentanwert": "Luftdruck reduziert auf Meeresniveau mit Standardatmosphäre",
            "Geopotentielle Höhe der 850 hPa-Fläche; Momentanwert": "Geopotentielle Höhe der 850 hPa-Fläche",
            "Geopotentielle Höhe der 700 hPa-Fläche; Momentanwert": "Geopotentielle Höhe der 700 hPa-Fläche",
            "Windrichtung vektoriell; Zehnminutenmittel; Instrument 1": "Windrichtung vektoriell",
            "Windgeschwindigkeit Turm in km/h; Zehnminutenmittel": "Windgeschwindigkeit Turm",
            "Böenspitze (Sekundenböe) Turm; Maximum": "Böenspitze Turm",
            "Relative Luftfeuchtigkeit Turm; Momentanwert": "Relative Luftfeuchtigkeit Turm",
            "Ort": "Ort",
            "Location Lat,Lon": "Koordinaten"
        }
        weather_df = weather_df.rename(columns=mapping)
        weather_df = weather_df[weather_df['Koordinaten'] != 'nan,nan']
        weather_df = weather_df.drop(columns=['Kürzel', 'Stationstyp'])
        weather_df = weather_df[weather_df['Ort']!="Eggishorn"]
        weather_df = weather_df.apply(get_region, axis=1)
        geoadmin_stations = weather_df[['Ort', 'Koordinaten','Region']].drop_duplicates()
        
        # Entfernen von Zeilen, bei denen die Koordinaten "nan,nan" sind
        weather_time = weather_df.iloc[0]['Datum']
        return weather_time, weather_df, geoadmin_stations