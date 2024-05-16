import pandas as pd
import requests
import json

def get_api_key():
    with open('backend/DataGathering/pwd.json') as f:
      credentials = json.load(f)
      API_KEY = credentials['google_api_key']
    return API_KEY

def get_pollen_forecast(latitude, longitude):
    API_KEY=get_api_key()
    DAYS = 1
    # URL der API-Anfrage
    url = f"https://pollen.googleapis.com/v1/forecast:lookup?key={API_KEY}&location.latitude={latitude}&location.longitude={longitude}&days={DAYS}&languageCode=de"

    # Senden Sie die GET-Anfrage und speichern Sie die Antwort
    response = requests.get(url)

    results = []

    # Prüfen Sie, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        try:
            # Decodieren Sie die JSON-Antwort
            data = response.json()

            # Überprüfen Sie, ob "dailyInfo" vorhanden ist
            if "dailyInfo" in data:
                # Durchlaufen Sie die täglichen Informationen
                for day in data["dailyInfo"]:
                    date = f"{day['date']['year']}-{day['date']['month']}-{day['date']['day']}"

                    # Initialisiere Ergebnis-Dictionary
                    result = {
                        'Datum': date,
                        'Latitude': latitude,
                        'Longitude': longitude
                    }

                    # Informationen aus pollenTypeInfo extrahieren
                    if "pollenTypeInfo" in day:
                        for pollen_type in day["pollenTypeInfo"]:
                            display_name = pollen_type.get('displayName', 'N/A')
                            index_value = pollen_type.get('indexInfo', {}).get('value', 'N/A')
                            result[display_name] = index_value

                    # Informationen aus plantInfo extrahieren
                    if "plantInfo" in day:
                        for plant in day["plantInfo"]:
                            display_name = plant.get('displayName', 'N/A')
                            index_value = plant.get('indexInfo', {}).get('value', 'N/A')
                            result[display_name] = index_value

                    results.append(result)
            else:
                print("Keine Polleninformationen in der Antwort gefunden.")
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Antwort: {e}")
    else:
        print(f"Fehler beim Abrufen der Pollenvorhersage: {response.status_code}")

    return results

def collect_pollen_forecasts(dataframe):
    all_results = []
    
    # Durch das DataFrame loopen und die Pollenvorhersage für jeden Eintrag abrufen
    for index, row in dataframe.iterrows():
        latitude, longitude = map(float, row['Koordinaten'].split(','))        
        try:
            results = get_pollen_forecast(latitude, longitude)
            if results:
                all_results.extend(results)
        except Exception as e:
            print(f"Fehler bei der Verarbeitung des Standorts {row['Koordinaten']}: {e}")
    
    # Ergebnisse in DataFrame umwandeln
    result_df = pd.DataFrame(all_results)

    if not result_df.empty:
        # LatLng in eine Spalte zusammenführen und Latitude und Longitude entfernen
        result_df['Koordinaten'] = result_df['Latitude'].astype(str) + ',' + result_df['Longitude'].astype(str)
        result_df = result_df.drop(columns=['Latitude', 'Longitude'])
    
    return result_df

allstations = pd.read_csv('backend/DataGathering/AllStations_with_location_info2.csv')
pollen_info=allstations[['Koordinaten']]
pollen_data = collect_pollen_forecasts(pollen_info)
pollen_data.to_csv('backend/DataGathering/pollen_data.csv', index=False)