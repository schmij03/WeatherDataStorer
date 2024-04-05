from meteostat import Stations
import pandas as pd
from datetime import datetime

# Aktuelles Jahr ermitteln
current_year = datetime.now().year

# Alle Stationen in der Schweiz abrufen
stations = Stations()
swiss_stations = stations.region('CH').fetch()

# Filtern nach Stationen, deren Datenaufzeichnungen bis zum aktuellen Jahr reichen
active_stations = swiss_stations[swiss_stations['daily_end'].dt.year >= current_year]

# Überprüfen, ob gefilterte Stationen vorhanden sind
if not active_stations.empty:
    # Exportieren der aktiven Stationen in eine CSV-Datei
    active_stations.to_csv('active_swiss_stations.csv', index=False)
    print(f"Aktive Stationen erfolgreich exportiert nach 'active_swiss_stations.csv'.")
else:
    print(f"Keine aktuell aktiven Stationen in der Schweiz gefunden, die bis {current_year} Daten aufzeichnen.")
