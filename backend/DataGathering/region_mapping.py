from shapely.geometry import Polygon, Point
import json

namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}

def extract_polygons_from_json(json_data):
    polygons = []
    for feature in json_data:
        name = feature['name']
        coordinates = feature['coordinates']
        for coord_set in coordinates:
            polygon_coords = [(float(coord[0]), float(coord[1])) for coord in coord_set]
            # Überprüfen, ob das Polygon mindestens 4 Koordinaten hat
            if len(polygon_coords) >= 4:
                polygons.append((name, Polygon(polygon_coords)))
            else:
                print(f"Polygon {name} hat weniger als 4 Koordinaten und wird übersprungen.")
    return polygons

with open('backend/DataGathering/Regionsmapping/All_Regions.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

polygons = extract_polygons_from_json(json_data)

def get_region(row):
    lat, lon = map(float, row['Koordinaten'].split(','))
    point = Point(lon, lat)
    for name, polygon in polygons:
        if polygon.contains(point):
            row['Region'] = name
            return row
    row['Region'] = None
    return row
