from meteostat import Stations, Hourly
from datetime import datetime, timedelta

# Standort und Zeitraum definieren
latitude = 47.3769  # Beispiel: Zürich, Schweiz
longitude = 8.5417
start = datetime(2023, 4, 4)
end = start + timedelta(days=1)

# Nächstgelegene Wetterstation finden
stations = Stations()
stations = stations.nearby(latitude, longitude)
station = stations.fetch(1)

if not station.empty:
    # Die ID der ersten Station im DataFrame verwenden
    station_id = station.index[0]
    print(f"Verwendete Station ID: {station_id}")

    # Stündliche Daten für diese Station-ID abrufen
    data = Hourly(station_id, start, end)
    data = data.fetch()

    # Ergebnisse ausgeben
    print(data)
else:
    print("Keine Stationen gefunden.")