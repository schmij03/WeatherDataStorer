import requests

def get_stations_in_switzerland(api_key):
    # URL für den Zugriff auf die Daten der Wetterstationen
    url = "http://api.openweathermap.org/data/3.0/stations"
    
    complete_url = f"{url}&appid={api_key}&units=metric&lang=de"
    response = requests.get(complete_url)
    # API-Anfrage ausführen
    response = requests.get(complete_url)
    
    # Überprüfen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        # JSON-Daten aus der Antwort extrahieren
        stations = response.json()
        # Durchlaufen der Stationen und Filtern nach Landeskennung für die Schweiz (z.B. 'CH')
        swiss_stations = [station for station in stations if station['country'] == 'CH']
        return swiss_stations
    else:
        # Fehlermeldung ausgeben, wenn die Anfrage fehlschlägt
        return f"Error: {response.status_code} - {response.text}"

# Ersetzen Sie 'Ihr_API_Schlüssel' mit Ihrem tatsächlichen OpenWeather API-Schlüssel
api_key = '06f4684f04692eef55eaca387497e196'
swiss_stations = get_stations_in_switzerland(api_key)
print(swiss_stations)
