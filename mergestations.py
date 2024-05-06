import pandas as pd
from geopy.geocoders import Nominatim
# CSV-Dateien einlesen
stations = pd.read_csv(f'backend\DataGathering\Stations.csv')
meteomatics_stations = pd.read_csv(f'backend\DataGathering\MeteomaticsStations.csv')
meteomatics=meteomatics_stations.drop_duplicates(subset=['Name'])
meteomatics=meteomatics.reset_index(drop=True)
meteomatics=meteomatics.rename(columns={"Name":"Ort"})
meteomatics=meteomatics.dropna(subset=['Ort'])
stations=stations.dropna(subset=['Ort'])


# Funktion zur Koordinatensuche
def find_coordinates(place):
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.geocode(place)
    if location:
        return f"{location.latitude}, {location.longitude}"
    else:
        return None

# Fehlende Koordinaten finden
def update_coordinates(df, column):
    df[column] = df.apply(lambda row: find_coordinates(row['Ort']) if pd.isna(row[column]) else row[column], axis=1)
    return df



# Zusammenführung der Daten anhand der Spalten "Name" und "Ort"
merged_data = pd.merge(meteomatics,stations,  on=['Ort'], how='outer')
merged_data = update_coordinates(merged_data, 'Location Lat,Lon')
# Zusammengeführte Daten in eine neue CSV-Datei speichern
merged_data.to_csv('backend/DataGathering/Merged_Stations.csv', index=False)

print("Die CSV-Dateien wurden erfolgreich zusammengeführt und als 'Merged_Stations.csv' gespeichert.")

# Zeilen filtern, bei denen "Location Lat, Lon" fehlt
filtered_data = merged_data[merged_data['Location Lat,Lon'].isna()]

# Gefiltertes DataFrame in eine neue CSV-Datei speichern
filtered_data.to_csv(r'backend/DataGathering/Filtered_Stations_No_Location_Lat_Lon.csv', index=False)