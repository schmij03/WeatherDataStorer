import json
import pandas as pd
from shapely.geometry import Point, Polygon

# Lade deine Stationsdaten
csv_path = 'backend/DataGathering/MeteomaticsStations.csv'
data = pd.read_csv(csv_path)



# Correct path to the JSON file
json_path = 'backend/DataGathering/rendercoordinates.json'

# Load the JSON data directly
with open(json_path, 'r') as f:
    json_data = json.load(f)
    polygon_coords = [(item['lat'], item['lng']) for item in json_data['rendercoordinates']]  # Adjust the key if necessary

# Create the polygon using the loaded coordinates
polygon = Polygon(polygon_coords)


# Funktion, um festzustellen, ob ein Punkt im Polygon liegt
def is_in_polygon(latlon):
    lat, lon = map(float, latlon.split(','))
    point = Point(lat, lon)
    return polygon.contains(point)

# Filtern der Stationsdaten
filtered_data = data[data["Location Lat,Lon"].apply(is_in_polygon)]

# Speichern der gefilterten Daten
output_path = 'backend/DataGathering/FilteredStations.csv'
filtered_data.to_csv(output_path, index=False)


