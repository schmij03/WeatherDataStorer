import pandas as pd
import requests
from datetime import datetime
from io import StringIO
import time
import numpy as np
from mongodb_connection import connect_mongodb

def lade_csv_daten(filepath):
    try:
        return pd.read_csv(filepath, sep=',')
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        return None

def hole_csv_daten_von_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        response.encoding = 'iso-8859-1'
        return pd.read_csv(StringIO(response.text), sep=';')
    else:
        print(f"Fehler beim Holen der Daten: {response.status_code}")
        return None

def konvertiere_datum(date_str):
    date_str = str(date_str)  # Konvertiere das Datum zu einem String, falls es noch kein String ist
    return datetime.strptime(date_str, '%Y%m%d%H%M').strftime('%Y-%m-%d %H:%M:%S')

def ersetze_spaltennamen(df, mapping):
    df.columns = [mapping.get(col, col) for col in df.columns]
    return df

def fuege_kantonsinformation_hinzu(df, stations_df):
    df = df.merge(stations_df[['Abk.', 'Kanton']], left_on='Station/Location', right_on='Abk.', how='left')
    df.drop(columns=['Abk.'], inplace=True)
    return df

def read_weather_mapping(mapping_filepath, weather_df):
    # Lese das Mapping CSV-File
    mapping_df = pd.read_csv(mapping_filepath)
    # Erstelle ein Dictionary aus dem Mapping
    mapping_dict = dict(zip(mapping_df['Parameter'], mapping_df['Beschreibung']))
    
    # Lese die Haupt-CSV-Datei
    data_df = weather_df
    
    # Umbenennen der Spalten entsprechend des Mappings
    data_df.rename(columns=mapping_dict, inplace=True)
    
    return data_df

def lade_parameter_beschreibungen(filepath):
    """
    Lädt die Beschreibungen der Wetterparameter aus einer CSV-Datei.
    """
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        print(f"Fehler beim Laden der Parameterbeschreibungen: {e}")
        return pd.DataFrame()

def main():
    wetterdaten_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv'
    regendaten_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA98.csv'
    foehn_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-foehn-10min/ch.meteoschweiz.messwerte-foehn-10min_de.csv'
    wetterDatenBeschreibung = r'backend\DataGathering\GeoAdmin\WetterdatenBeschreibung.csv'
    stationsbeschreibungen = r'backend\DataGathering\GeoAdmin\Stationsbeschreibungen.csv'
    niederschlagsbeschreibungen = r'backend\DataGathering\GeoAdmin\Niederschlagsmenge.csv'

    regen_df = hole_csv_daten_von_url(regendaten_url)
    wetter_df = hole_csv_daten_von_url(wetterdaten_url)
    foehn_df = hole_csv_daten_von_url(foehn_url)
    print(foehn_df)
    mapping_foehn = {"Kein Föhn": 0, "Föhnmischluft": 1, "Föhn": 2}
    
    stations_df = lade_csv_daten(stationsbeschreibungen)
    
    print(foehn_df)

    if wetter_df is not None and stations_df is not None:
        foehn_df.set_index('Abk.', inplace=True)
        stations_df.set_index('Abk.', inplace=True)
        wetter_df = wetter_df.merge(stations_df[['Kanton', 'Stationstyp', 'Station']], left_on='Station/Location', right_index=True, how='left')
        
        regen_df = regen_df.merge(stations_df[['Kanton', 'Stationstyp', 'Station']], left_on='Station/Location', right_index=True, how='left')
        wetter_df.to_csv(f"backend/DataGathering/GeoAdminData_beforemerging.csv", index=False)
        wetter_df['Stationstyp'] = wetter_df['Stationstyp'].apply(lambda x: 'W' if x == 'Wetterstation' else 'N')
        regen_df['Stationstyp'] = regen_df['Stationstyp'].apply(lambda x: 'W' if x == 'Wetterstation' else 'N')
        

        wetter_df['Datum'] = wetter_df['Date'].apply(konvertiere_datum)
        regen_df['Datum'] = regen_df['Date'].apply(konvertiere_datum)
        wetter_df.drop(columns=['Date'], inplace=True)
        regen_df.drop(columns=['Date'], inplace=True)

        regen_df.replace('-', np.nan, inplace=True)
        wetter_df.replace('-', np.nan, inplace=True)
        wetter_df.rename(columns={'Station/Location': 'Abk.','Station':'Ort' }, inplace=True)
        regen_df.rename(columns={'Station/Location': 'Abk.','Station':'Ort'}, inplace=True)
        wetter_df = read_weather_mapping(wetterDatenBeschreibung, wetter_df)
        regen_df = read_weather_mapping(niederschlagsbeschreibungen, regen_df)
        wetter_df=wetter_df.merge(foehn_df[['Föhnindex']], left_on='Abk.', right_index=True, how='left')
        wetter_df['Föhnindex'] = wetter_df['Föhnindex'].map(mapping_foehn)
        verbundene_df = pd.merge(wetter_df, regen_df, on=['Abk.', 'Datum', 'Kanton', 'Niederschlag; Zehnminutensumme', 'Stationstyp', 'Ort'], how='outer')
        verbundene_df.rename(columns={'Abk.': 'Abkuerzung'}, inplace=True)
        
        print(verbundene_df.head())
        print("Verfügbare meteorologische Parameter und deren Beschreibung:")

        aktuelle_zeit = datetime.now()
        formatierte_zeit = aktuelle_zeit.strftime("%H:%M:%S")
        
        wetter_df.to_csv(f"backend/DataGathering/GeoAdminData_{10}.csv", index=False)
        regen_df.to_csv(f"backend/DataGathering/GeoAdminData_{4}.csv", index=False)
        print(verbundene_df.head())
        print("Aktuelle Zeit:", formatierte_zeit)

while True:
    main()
    time.sleep(1800)
