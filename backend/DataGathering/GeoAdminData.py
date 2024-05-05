import pandas as pd
import requests
from datetime import datetime
from io import StringIO
import time
import numpy as np
from mongodb_connection import connect_mongodb  # Überprüfe, ob dies korrekt eingebunden ist

# Funktion zum Laden von CSV-Daten aus einer Datei
def load_csv_data(filepath):
    try:
        return pd.read_csv(filepath, sep=',')
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Funktion zum Abrufen von CSV-Daten von einer URL
def fetch_csv_data_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        response.encoding = 'iso-8859-1'  # Encoding für spezielle Zeichen
        return pd.read_csv(StringIO(response.text), sep=';')
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

# Funktion zum Konvertieren eines Datumsformats
def convert_date(date_str):
    date_str = str(date_str)  # Stelle sicher, dass das Datum als String vorliegt
    return datetime.strptime(date_str, '%Y%m%d%H%M').strftime('%Y-%m-%d %H:%M:%S')

# Funktion zum Ersetzen von Spaltennamen basierend auf einem Mapping
def replace_column_names(df, mapping):
    df.columns = [mapping.get(col, col) for col in df.columns]
    return df

# Funktion zum Hinzufügen von Kantonsinformationen zu einem DataFrame
def add_canton_information(df, stations_df):
    df = df.merge(stations_df[['Abk.', 'Kanton']], left_on='Station/Location', right_on='Abk.', how='left')
    df.drop(columns=['Abk.'], inplace=True)
    return df

# Funktion zum Lesen eines Mapping-Files und Umbenennen von Spalten entsprechend des Mappings
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
        print(f"Error loading parameter descriptions: {e}")
        return pd.DataFrame()




# Hauptfunktion, die den gesamten Ablauf steuert
def main():
    # URLs und Dateipfade zu den Daten
    weather_data_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv'
    rainfall_data_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA98.csv'
    foehn_data_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-foehn-10min/ch.meteoschweiz.messwerte-foehn-10min_de.csv'
    weather_data_description = r'backend\DataGathering\GeoAdmin\WetterdatenBeschreibung.csv'
    stations_description = r'backend\DataGathering\GeoAdmin\Stationsbeschreibungen.csv'
    rainfall_description = r'backend\DataGathering\GeoAdmin\Niederschlagsmenge.csv'

    # Daten von den verschiedenen Quellen abrufen
    rainfall_df = fetch_csv_data_from_url(rainfall_data_url)
    weather_df = fetch_csv_data_from_url(weather_data_url)
    foehn_df = fetch_csv_data_from_url(foehn_data_url)
    
    # Mapping für den Föhnindex
    mapping_foehn = {"Kein Föhn": 0, "Föhnmischluft": 1, "Föhn":2}
    
    # Stationsdaten laden
    stations_df = load_csv_data(stations_description)

    # Wenn die Daten erfolgreich geladen wurden, führe weitere Schritte aus
    if weather_df is not None and stations_df is not None:
        # Indizes für effiziente Datenmanipulation festlegen
        foehn_df.set_index('Abk.', inplace=True)
        stations_df.set_index('Abk.', inplace=True)
        
        # Kantonsinformationen zu Wetter- und Regendaten hinzufügen
        weather_df = weather_df.merge(stations_df[['Kanton', 'Stationstyp', 'Station']], left_on='Station/Location', right_index=True, how='left')
        rainfall_df = rainfall_df.merge(stations_df[['Kanton', 'Stationstyp', 'Station']], left_on='Station/Location', right_index=True, how='left')
        
        # Stationstypen vereinheitlichen
        weather_df['Stationstyp'] = weather_df['Stationstyp'].apply(lambda x: 'W' if x == 'Wetterstation' else 'N')
        rainfall_df['Stationstyp'] = rainfall_df['Stationstyp'].apply(lambda x: 'W' if x == 'Wetterstation' else 'N')
        
        weather_df.to_csv(f"backend/DataGathering/GeoAdminData_{1}.csv", index=False)
        # Datumskonvertierung und Spaltenbereinigung
        weather_df['Datum'] = weather_df['Date'].apply(convert_date)
        rainfall_df['Datum'] = rainfall_df['Date'].apply(convert_date)
        weather_df.drop(columns=['Date'], inplace=True)
        rainfall_df.drop(columns=['Date'], inplace=True)

        # NaN-Werte ersetzen
        rainfall_df.replace('-', np.nan, inplace=True)
        weather_df.replace('-', np.nan, inplace=True)
        
        # Spalten umbenennen und Mapping anwenden
        weather_df.rename(columns={'Station/Location': 'Kürzel','Station':'Ort' }, inplace=True)
        rainfall_df.rename(columns={'Station/Location': 'Kürzel','Station':'Ort'}, inplace=True)
        weather_df = read_weather_mapping(weather_data_description, weather_df)
        rainfall_df = read_weather_mapping(rainfall_description, rainfall_df)
        
        # Föhnindex zu den Wetterdaten hinzufügen und Mapping anwenden
        weather_df=weather_df.merge(foehn_df[['Föhnindex']], left_on='Kürzel', right_index=True, how='left')
        weather_df['Föhnindex'] = weather_df['Föhnindex'].map(mapping_foehn)
        
        # Daten zusammenführen
        merged_df = pd.merge(weather_df, rainfall_df, on=['Kürzel', 'Datum', 'Kanton', 'Niederschlag; Zehnminutensumme', 'Stationstyp', 'Ort'], how='outer')

        # Aktuelle Zeit anzeigen
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Daten in CSV-Dateien speichern
        weather_df.to_csv(f"backend/DataGathering/GeoAdminData_{11}.csv", index=False)
        rainfall_df.to_csv(f"backend/DataGathering/GeoAdminData_{12}.csv", index=False)

        weather_date = weather_df.iloc[0]['Datum']
        return weather_date, weather_df,rainfall_df,merged_df
