from pymongo.mongo_client import MongoClient
import json

# Laden der MongoDB-Verbindungsdaten aus einer JSON-Datei
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

def save_to_mongodb(df):
    # Verbindung zum MongoDB-Server herstellen
    db, collection = connect_mongodb()

    # Konvertieren des DataFrames in ein Dictionary
    data = df.to_dict(orient='records')

    # Einfügen der Daten in die MongoDB-Sammlung
    collection.insert_many(data)

    # Schliessen der Verbindung
    db.client.close()
    print("Daten in MongoDB gespeichert!")

def clear_mongodb():
    # Verbindung zum MongoDB-Server herstellen
    db, collection = connect_mongodb()

    # Löschen aller Dokumente in der Sammlung
    result = collection.delete_many({})

    # Überprüfen, ob das Löschen erfolgreich war
    if result.deleted_count > 0:
        print("Sammlung geleert.")
    else:
        print("Keine Dokumente zum Löschen gefunden.")

    # Schliessen der Verbindung
    db.client.close()