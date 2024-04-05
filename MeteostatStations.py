from meteostat import Stations
import pandas as pd

# Alle Stationen in der Schweiz abrufen
stations = Stations()
swiss_stations = stations.region('CH').fetch()

# Überprüfen, ob das DataFrame leer ist
if not swiss_stations.empty:
    # Ausgabe der Informationen zu den Stationen
    print(swiss_stations)
else:
    print("Keine Stationen in der Schweiz gefunden.")
