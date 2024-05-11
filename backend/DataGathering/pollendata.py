import requests

# Ersetzen Sie "YOUR_API_KEY" mit Ihrer API-Schlüssel
API_KEY = "AIzaSyBPPQk2MCl9gqa18jjUtg-1fj5pmb2ABhc"

# Breitengrad und Längengrad des Standorts
LATITUDE = 46.7499
LONGITUDE = 7.58522

# Anzahl der Tage, für die Vorhersagen abgerufen werden sollen
DAYS = 1

# URL der API-Anfrage
url = f"https://pollen.googleapis.com/v1/forecast:lookup?key={API_KEY}&location.latitude={LATITUDE}&location.longitude={LONGITUDE}&days={DAYS}"

# Senden Sie die GET-Anfrage und speichern Sie die Antwort
response = requests.get(url)

# Prüfen Sie, ob die Anfrage erfolgreich war
if response.status_code == 200:
  # Decodieren Sie die JSON-Antwort
  data = response.json()

  # Überprüfen Sie, ob "dailyInfo" vorhanden ist
  if "dailyInfo" in data:
    # Durchlaufen Sie die täglichen Informationen
    for day in data["dailyInfo"]:
      # Drucken Sie das Datum
      print(f"Datum: {day['date']['year']}-{day['date']['month']}-{day['date']['day']}")

      # Überprüfen Sie, ob "pollenTypeInfo" vorhanden ist
      if "pollenTypeInfo" in day:
        # Durchlaufen Sie die Pollentypen
        for pollen_type in day["pollenTypeInfo"]:
          # Drucken Sie den Pollentyp
          print(f"{pollen_type['displayName']}: ", end='')

          # Überprüfen Sie, ob "indexInfo" vorhanden ist, bevor Sie darauf zugreifen
          if "indexInfo" in pollen_type:
            print(f"{pollen_type['indexInfo']['value']} ({pollen_type['indexInfo']['category']})")
          else:
            print("Keine Indexinformationen verfügbar")
      else:
        print("Keine Polleninformationen für diesen Tag verfügbar.")
  else:
    print("Keine Polleninformationen in der Antwort gefunden.")
else:
  print(f"Fehler beim Abrufen der Pollenvorhersage: {response.status_code}")
