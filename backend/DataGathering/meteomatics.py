import requests
import base64
import pandas as pd
from io import StringIO

username = 'zhaw_schmid_jan'
password = 'T36iwL9Sik'

# Codieren von Benutzername und Passwort zu Base64
credentials = base64.b64encode(f"{username}:{password}".encode()).decode('utf-8')

# Setzen der Autorisierungs-Header
headers = {'Authorization': f'Basic {credentials}'}

# Senden der Anfrage an die API, um den Token zu erhalten
response = requests.get('https://login.meteomatics.com/api/v1/token', headers=headers)

# Überprüfen der Antwort
if response.status_code == 200:
    data = response.json()
    token = data['access_token']
    print('token:', token)

    # Abfrage der URL vom Benutzer
    url = "https://api.meteomatics.com/find_station?location=switzerland"

    # Senden der Anfrage an die angegebene URL mit dem erhaltenen Token
    response = requests.get(url, headers={'Authorization': f'Bearer {token}'})

    # Überprüfen der Antwort
    if response.status_code == 200:
        print('Daten erfolgreich abgerufen.')

        # CSV-Daten aus der Antwort extrahieren
        csv_data = response.text

        # CSV-Daten in ein Pandas DataFrame umwandeln
        df = pd.read_csv(StringIO(csv_data), delimiter=';')
        print('Pandas DataFrame:')
        print(df)
    else:
        print('Fehler beim Abrufen der Daten:', response.text)
else:
    print('Fehler beim Abrufen des Tokens:', response.text)
df=df.drop(columns=["Horizontal Distance","Vertical Distance",'Effective Distance'])
df.to_csv('backend/DataGathering/MeteomaticsStations.csv', index=False)