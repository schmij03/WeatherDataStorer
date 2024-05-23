from pymongo.mongo_client import MongoClient
from pymongo import UpdateOne
import json
import pandas as pd
from shapely.geometry import Polygon, Point
from datetime import datetime

# MongoDB-Verbindungsdaten laden
with open("backend/DataGathering/pwd.json") as f:
    credentials = json.load(f)
    password = credentials["mongodb_credentials"]['password']
    username = credentials["mongodb_credentials"]['username']
    database = credentials["mongodb_credentials"]['database']

def connect_mongodb():
    # MongoDB-Verbindungs-URI
    uri = f"mongodb+srv://{username}:{password}@{database}.zebph6n.mongodb.net/?retryWrites=true&w=majority&appName=WeatherData"
    # Erstellen eines neuen Clients und Verbindung zum Server
    client = MongoClient(uri)

    # Überprüfen, ob die MongoDB-Verbindung erfolgreich ist
    try:
        client.admin.command('ping')
        print("Erfolgreich mit MongoDB verbunden!")
    except Exception as e:
        print("Fehler bei der Verbindung zu MongoDB:", e)

    # Auswählen der spezifischen Datenbanken und Sammlungen
    db = client["BA"]
    collection = db["WeatherData"]
    return db, collection

# JSON-Daten für Regionen laden und Polygone extrahieren
with open('backend/DataGathering/Regionsmapping/All_Regions.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}

def extract_polygons_from_json(json_data):
    polygons = []
    for feature in json_data:
        name = feature['name']
        coordinates = feature['coordinates']
        for coord_set in coordinates:
            polygon_coords = [(float(coord[0]), float(coord[1])) for coord in coord_set]
            if len(polygon_coords) >= 4:
                polygons.append((name, Polygon(polygon_coords)))
            else:
                print(f"Polygon {name} hat weniger als 4 Koordinaten und wird übersprungen.")
    return polygons

polygons = extract_polygons_from_json(json_data)

def get_region(document):
    lat, lon = map(float, document['Koordinaten'].split(','))
    point = Point(lon, lat)
    for name, polygon in polygons:
        if polygon.contains(point):
            return name
    return None

# MongoDB-Dokumente aktualisieren
def update_documents():
    db, collection = connect_mongodb()

    query = {"Zeit": {"$lt": datetime(2024, 5, 23, 13, 0, 0)}}
    documents = collection.find(query)

    updates = []
    for doc in documents:
        region = get_region(doc)
        print(f"Updating document ID: {doc['_id']} with region: {region}")
        updates.append(UpdateOne({'_id': doc['_id']}, {'$set': {'Region': region}}))

    if updates:
        result = collection.bulk_write(updates)
        print(f"Updated {result.modified_count} documents.")
    else:
        print("No documents to update.")

    db.client.close()

# Hauptfunktion ausführen
if __name__ == "__main__":
    update_documents()
