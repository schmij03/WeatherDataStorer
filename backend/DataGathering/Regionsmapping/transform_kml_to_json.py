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
        for linear_ring in placemark.findall('.//kml:LinearRing', namespace):
            coord_text = linear_ring.find('.//kml:coordinates', namespace).text.strip()
            coords = []
            for c in coord_text.split():
                lon, lat, _ = map(float, c.split(','))
                coords.append((lon, lat))
            coordinates.append(coords)
        polygons.append({'name': name, 'coordinates': coordinates})

    return polygons

def merge_json_data(json_data1, json_data2):
    merged_data = json_data1 + json_data2
    return merged_data

def save_to_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Pfad zur KML-Datei
kml_file_path = 'backend/DataGathering/Regionsmapping/Regions_not_AT.kml'
# Daten extrahieren
polygons = extract_polygons_from_kml(kml_file_path)

with open('backend/DataGathering/Regionsmapping/AT/regionsAT.json', 'r', encoding='utf-8') as file:
    json_data_AT = json.load(file)

merged_data = merge_json_data(polygons, json_data_AT)

# Pfad zur Ausgabe-JSON-Datei
output_json_path = 'backend/DataGathering/Regionsmapping/All_Regions.json'

# Daten in JSON-Datei speichern
save_to_json(merged_data, output_json_path)

# Ausgabe des Pfads zur JSON-Datei
print(f"JSON-Datei wurde erfolgreich erstellt: {output_json_path}")
