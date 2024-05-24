from pymongo.mongo_client import MongoClient
import json
import pandas as pd
import numpy as np

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

def replace_no_data_with_nan():
    db, collection = connect_mongodb()

    fields_to_check = [
        "Niederschlagsmenge (letzte Stunde)",
        "Schneefallmenge (letzte Stunde)",
        "Windböen"
    ]

    query = {"$or": [{field: "Keine Daten"} for field in fields_to_check]}
    documents = collection.find(query, {field: 1 for field in fields_to_check})
    count1 = collection.count_documents(query)
    count = 0

    for doc in documents:
        count += 1
        updates = {}
        
        for field in fields_to_check:
            if field in doc and doc[field] == "Keine Daten":
                updates[field] = np.nan  # Using np.nan to represent NaN

        if updates:
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": updates}
            )

        print(f"Dokument {count} von {count1} aktualisiert.")

    db.client.close()

if __name__ == "__main__":
    replace_no_data_with_nan()
