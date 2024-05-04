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
        return pd.read_csv(StringIO(response.text), sep=';')
    else:
        print(f"Fehler beim Holen der Daten: {response.status_code}")
        return None

def konvertiere_datum(date_str):
    date_str = str(date_str)  # Konvertiere das Datum zu einem String, falls es noch kein String ist
    return datetime.strptime(date_str, '%Y%m%d%H%M').strftime('%Y-%m-%d %H:%M')

def ersetze_spaltennamen(df, mapping):
    df.columns = [mapping.get(col, col) for col in df.columns]
    return df

def fuege_kantonsinformation_hinzu(df, stations_df):
    df = df.merge(stations_df[['Abk.', 'Kanton']], left_on='Station/Location', right_on='Abk.', how='left')
    df.drop(columns=['Abk.'], inplace=True)
    return df

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
    stationsbeschreibungen = r'backend\DataGathering\GeoAdmin\Stationsbeschreibungen.csv'
    regendaten_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA98.csv'
    wetterDatenBeschreibung = r'backend\DataGathering\GeoAdmin\WetterdatenBeschreibung.csv'

    regen_df = hole_csv_daten_von_url(regendaten_url)
    wetter_df = hole_csv_daten_von_url(wetterdaten_url)
    stations_df = lade_csv_daten(stationsbeschreibungen)
    parameter_df = lade_parameter_beschreibungen(wetterDatenBeschreibung)

    if wetter_df is not None and stations_df is not None:
        stations_df.set_index('Abk.', inplace=True)
        wetter_df = wetter_df.merge(stations_df[['Kanton', 'Stationstyp']], left_on='Station/Location', right_index=True, how='left')
        regen_df = regen_df.merge(stations_df[['Kanton', 'Stationstyp']], left_on='Station/Location', right_index=True, how='left')
        wetter_df['Stationstyp'] = wetter_df['Stationstyp'].apply(lambda x: 'W' if x == 'Wetterstation' else 'N')
        regen_df['Stationstyp'] = regen_df['Stationstyp'].apply(lambda x: 'W' if x == 'Wetterstation' else 'N')

        wetter_df['Datum'] = wetter_df['Date'].apply(konvertiere_datum)
        regen_df['Datum'] = regen_df['Date'].apply(konvertiere_datum)
        wetter_df.drop(columns=['Date'], inplace=True)
        regen_df.drop(columns=['Date'], inplace=True)

        regen_df.replace('-', np.nan, inplace=True)
        wetter_df.replace('-', np.nan, inplace=True)

        verbundene_df = pd.merge(wetter_df, regen_df, on=['Station/Location', 'Datum', 'Kanton', 'rre150z0', 'Stationstyp'], how='outer')
        verbundene_df.rename(columns={'Station/Location': 'Station'}, inplace=True)

        print(verbundene_df.head())
        print("Verfügbare meteorologische Parameter und deren Beschreibung:")
        print(parameter_df.head())

        aktuelle_zeit = datetime.now()
        formatierte_zeit = aktuelle_zeit.strftime("%H:%M:%S")
        wetter_df.to_csv(f"backend/DataGathering/GeoAdminData_{3}.csv", index=False)
        print(verbundene_df.head())
        print("Aktuelle Zeit:", formatierte_zeit)

while True:
    main()
    time.sleep(1800)
