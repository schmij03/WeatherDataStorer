import json
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree

# Pfad zur JSON-Datei
file_path = 'backend/DataGathering/Regionsmapping/DE/Files/extracted_data_ba_bw.json'

# JSON-Datei laden
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# KML-Dokument erstellen
kml = Element('kml')
document = SubElement(kml, 'Document')

# Durch alle Features iterieren und die gewünschten Informationen extrahieren
for feature in data:
    lan_name = feature.get('lan_name')
    krs_shortname = feature.get('krs_shortname')
    coordinates = feature.get('coordinates')

    placemark = SubElement(document, 'Placemark')

    name = SubElement(placemark, 'name')
    name.text = f"{krs_shortname}"

    polygon = SubElement(placemark, 'Polygon')
    outer_boundary_is = SubElement(polygon, 'outerBoundaryIs')
    linear_ring = SubElement(outer_boundary_is, 'LinearRing')

    coord_text = ""
    for coord in coordinates[0]:
        coord_text += f"{coord[0]},{coord[1]},0 "

    coordinates_elem = SubElement(linear_ring, 'coordinates')
    coordinates_elem.text = coord_text.strip()

# KML-Dokument als Datei speichern
output_path = 'backend/DataGathering/Regionsmapping/DE/Files/extracted_data_ba_bw.jsonextracted_data.kml'
ElementTree(kml).write(output_path, encoding='utf-8', xml_declaration=True)

# Ausgabe des Pfads zur neuen KML-Datei
print(output_path)
