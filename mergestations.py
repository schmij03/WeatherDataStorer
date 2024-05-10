import pandas as pd

# CSV-Dateien einlesen
stations = pd.read_csv('backend/DataGathering/Stations.csv')
meteomatics_stations = pd.read_csv('backend/DataGathering/MeteomaticsStations.csv')

# Daten vorbereiten
meteomatics = meteomatics_stations.drop_duplicates(subset=['Name'])
meteomatics = meteomatics.reset_index(drop=True)
meteomatics = meteomatics.rename(columns={"Name": "Ort"})
meteomatics = meteomatics.dropna(subset=['Ort'])
stations = stations.dropna(subset=['Ort'])

# Zusammenführung der Daten mittels outer join
merged_data = pd.merge(meteomatics, stations, on=['Ort', 'Location Lat,Lon'], how='outer', suffixes=('_meteomatics', '_stations'))

# Liste der Spalten, die gefüllt werden sollen
columns_to_fill = ['Kürzel', 'Kanton', 'id', 'country']


merged_data.to_csv('backend/DataGathering/Merged_Stationsbeforedrop.csv', index=False)


merged_data['country'] = 'CH'
# Zusammengeführte Daten in eine neue CSV-Datei speichern
merged_data.to_csv('backend/DataGathering/Merged_Stations.csv', index=False)

print("Die CSV-Dateien wurden erfolgreich zusammengeführt und als 'Merged_Stations.csv' gespeichert.")

# Zeilen filtern, bei denen "Location Lat, Lon" fehlt
filtered_data = merged_data[merged_data['Location Lat,Lon'].isna()]

# Gefiltertes DataFrame in eine neue CSV-Datei speichern
filtered_data.to_csv('backend/DataGathering/Filtered_Stations_No_Location_Lat_Lon.csv', index=False)
