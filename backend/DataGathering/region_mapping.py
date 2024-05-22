import xml.etree.ElementTree as ET
import pandas as pd
from shapely.geometry import Polygon, Point

# XML-Datei und Namespace-Dictionary einlesen
tree = ET.parse('backend/DataGathering/Regionsmapping/Schweizer_Karte_inkl_Wetterregionen.kml')
rootCH = tree.getroot()
namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}

tree2 = ET.parse('backend/DataGathering/Regionsmapping/Frankreich.kml')
rootFR = tree2.getroot()

# Polygone aus der KML-Datei extrahieren
polygons = []
polygonsFR = []
for placemark in rootCH.findall('.//kml:Placemark', namespaces):
    name = placemark.find('kml:name', namespaces).text
    coordinates = placemark.find('.//kml:coordinates', namespaces).text.strip()
    coords_list = coordinates.split()
    polygon_coords = [(float(coord.split(',')[0]), float(coord.split(',')[1])) for coord in coords_list]
    polygons.append((name, Polygon(polygon_coords)))

for placemark1 in rootFR.findall('.//kml:Placemark', namespaces):
    name1 = placemark1.find('kml:name', namespaces).text
    coordinates1 = placemark1.find('.//kml:coordinates', namespaces).text.strip()
    coords_list1 = coordinates.split()
    polygon_coords1 = [(float(coord1.split(',')[0]), float(coord1.split(',')[1])) for coord1 in coords_list1]
    polygonsFR.append((name1, Polygon(polygon_coords1)))

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

def get_regionFR(row):
    lat, lon = map(float, row['Koordinaten'].split(','))
    point = Point(lon, lat)
    for name1, polygon1 in polygonsFR:
        if polygon1.contains(point):
            row['Region'] = name1
            return row
    row['Region'] = None
    return row
