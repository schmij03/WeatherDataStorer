import json

import xml.etree.ElementTree as ET

def extract_polygons_from_kml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Namespace verwenden, um die KML-Elemente zu finden
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}

    polygons = []

    for placemark in root.findall('.//kml:Placemark', namespace):
        name = placemark.find('kml:name', namespace).text
        coordinates = []
        for polygon in placemark.findall('.//kml:Polygon', namespace):
            for linear_ring in polygon.findall('.//kml:LinearRing', namespace):
                coord_text = linear_ring.find('.//kml:coordinates', namespace).text.strip()
                coords = []
                for c in coord_text.split():
                    lon, lat = map(float, c.split(','))
                    coords.append((lon, lat))
                coordinates.append(coords)
        polygons.append({'name': name, 'coordinates': coordinates})

    return polygons

def save_to_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Pfad zur KML-Datei
kml_file_path = 'backend/DataGathering/Regionsmapping/AT/vogis-bezirke_aut.kml'

# Daten extrahieren
polygons = extract_polygons_from_kml(kml_file_path)

# Pfad zur Ausgabe-JSON-Datei
output_json_path = 'backend/DataGathering/Regionsmapping/AT/regionsAT.json'

# Daten in JSON-Datei speichern
save_to_json(polygons, output_json_path)

# Ausgabe des Pfads zur JSON-Datei
print(f"JSON-Datei wurde erfolgreich erstellt: {output_json_path}")
