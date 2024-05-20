import xml.etree.ElementTree as ET
import pandas as pd
from shapely.geometry import Polygon, Point

# XML-Datei und Namespace-Dictionary einlesen
tree = ET.parse('backend/DataGathering/Regionsmapping/Schweizer_Karte_inkl_Wetterregionen.kml')
rootCH = tree.getroot()
namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}

# Polygone aus der KML-Datei extrahieren
polygons = []
for placemark in rootCH.findall('.//kml:Placemark', namespaces):
    name = placemark.find('kml:name', namespaces).text
    coordinates = placemark.find('.//kml:coordinates', namespaces).text.strip()
    coords_list = coordinates.split()
    polygon_coords = [(float(coord.split(',')[0]), float(coord.split(',')[1])) for coord in coords_list]
    polygons.append((name, Polygon(polygon_coords)))

# Funktion zur Zuordnung von Regionen basierend auf Koordinaten
def get_region(row):
    lat, lon = map(float, row['Koordinaten'].split(','))
    point = Point(lon, lat)
    for name, polygon in polygons:
        if polygon.contains(point):
            row['Region'] = name
            return row
    row['Region'] = None
    return row
