import pandas as pd
import requests
from datetime import datetime

def fetch_weather(api_username, api_password, latitude, longitude):
    # Datum und Zeit für die Abfrage aufbereiten
    now = datetime.now(datetime.UTC).isoformat() + "Z"  # Zulu (UTC) Zeitformat

    # URL zusammenstellen
    url = f"https://api.meteomatics.com/{now}/t_2m:C/{latitude},{longitude}/json"

    # API-Anfrage durchführen
    response = requests.get(url, auth=(api_username, api_password))

    # Prüfen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        data = response.json()
        # Temperatur auslesen
        temperature = data['data'][0]['coordinates'][0]['dates'][0]['value']
        return temperature
    else:
        return "API-Anfrage fehlgeschlagen: " + response.text

# CSV-Datei laden
file_path = 'backend\DataGathering\meteomatics_stations_filtered.csv'
stations_df = pd.read_csv(file_path)

# Spalte für Breiten- und Längengrade trennen
stations_df[['latitude', 'longitude']] = stations_df['Location Lat,Lon'].str.split(',', expand=True)
stations_df['latitude'] = pd.to_numeric(stations_df['latitude'])
stations_df['longitude'] = pd.to_numeric(stations_df['longitude'])

# API-Zugangsdaten
api_username = 'zhaw_schmid_jan'
api_password = 'T36iwL9Sik'

# Neues DataFrame zur Speicherung der Ergebnisse
results_df = pd.DataFrame(columns=['Ort', 'latitude', 'longitude', 'temperature', 'elevation'])

# Durchlaufen des DataFrames und Abfrage der Wetterdaten für jede Station
for index, row in stations_df.iterrows():
    temperature = fetch_weather(api_username, api_password, row['latitude'], row['longitude'])
    results_df = results_df.append({
        'Ort': row['Ort'],
        'latitude': row['latitude'],
        'longitude': row['longitude'],
        'temperature': temperature,
        'elevation': row['elevation']
    }, ignore_index=True)

# Ergebnisse anzeigen
print(results_df.head())
