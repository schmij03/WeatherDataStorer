import pandas as pd
import googlemaps

# Lade die CSV-Daten
csv_path = 'backend/DataGathering/MeteomaticsStations.csv'  # Passe den Pfad entsprechend an
data = pd.read_csv(csv_path)
csv_path2='meteostat_neighbouringstations.csv'
data2=pd.read_csv(csv_path2)

# Initialisiere den Google Maps Client
google_maps_key = 'AIzaSyBPPQk2MCl9gqa18jjUtg-1fj5pmb2ABhc'  # Dein API-Schlüssel
gmaps = googlemaps.Client(key=google_maps_key)

# Funktion, um ein Land, eine Region und eine Stadt zu erhalten
def get_location_info(latlon):
    try:
        lat, lon = map(float, latlon.split(','))
        # Verwende die Google Maps API
        result = gmaps.reverse_geocode((lat, lon))
        if result:
            country = region = city = 'Unknown'
            for component in result[0]['address_components']:
                if 'country' in component['types']:
                    country = component['short_name'].upper()
                if 'administrative_area_level_1' in component['types']:
                    region = component['long_name']
                if 'locality' in component['types']:
                    city = component['long_name']
            return country, region, city
        return 'Unknown', 'Unknown', 'Unknown'
    except Exception as e:
        print(f"Error: {e} - with coordinates {latlon}")
        return 'Unknown', 'Unknown', 'Unknown'

# Die Funktion auf jede Zeile anwenden, um die 'country', 'region' und 'city'-Spalten zu erstellen
data[['country', 'region1', 'city']] = data.apply(lambda row: pd.Series(get_location_info(row["Location Lat,Lon"])), axis=1)
data2[['country1','region', 'city']] = data2.apply(lambda row: pd.Series(get_location_info(row["Location Lat,Lon"])), axis=1)
# Speichere das aktualisierte DataFrame zurück in eine CSV
output_path = 'backend/DataGathering/MeteomaticsStations_with_location_info.csv'
output_path2 = 'backend/DataGathering/meteostat_neighbouringstations_with_location_info.csv'
data.to_csv(output_path, index=False)
data2.to_csv(output_path2, index=False)
