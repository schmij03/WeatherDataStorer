from pymongo.mongo_client import MongoClient
import json
import pandas as pd

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

def update_wind_speed_fields():
    db, collection = connect_mongodb()

    query = {
        "$or": [
            {"Windgeschwindigkeit in km/h": {"$type": "string"}},
            {"Windgeschwindigkeit Turm in km/h": {"$type": "string"}}
        ]
    }
    documents = collection.find(query, {"Windgeschwindigkeit in km/h": 1, "Windgeschwindigkeit Turm in km/h": 1})
    count1 = collection.count_documents(query)
    count = 0

    for doc in documents:
        count += 1
        updates = {}
        
        if "Windgeschwindigkeit in km/h" in doc and isinstance(doc["Windgeschwindigkeit in km/h"], str):
            try:
                wind_speed = float(doc["Windgeschwindigkeit in km/h"])
                updates["Windgeschwindigkeit in km/h"] = wind_speed
            except ValueError:
                print(f"Warnung: Wert für 'Windgeschwindigkeit in km/h' in Dokument {doc['_id']} konnte nicht in Float umgewandelt werden.")

        if "Windgeschwindigkeit Turm in km/h" in doc and isinstance(doc["Windgeschwindigkeit Turm in km/h"], str):
            try:
                wind_speed_turm = float(doc["Windgeschwindigkeit Turm in km/h"])
                updates["Windgeschwindigkeit Turm in km/h"] = wind_speed_turm
            except ValueError:
                print(f"Warnung: Wert für 'Windgeschwindigkeit Turm in km/h' in Dokument {doc['_id']} konnte nicht in Float umgewandelt werden.")
        
        if updates:
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": updates}
            )

        print(f"Dokument {count} von {count1} aktualisiert.")

    db.client.close()

if __name__ == "__main__":
    update_wind_speed_fields()
