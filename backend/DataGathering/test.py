from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime
import logging

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levellevelname)s - %(message)s')

def get_pollen_data(ort, country):
    # WebDriver einrichten (hier Firefox als Beispiel)
    driver = webdriver.Firefox()  # Pfad zum FirefoxDriver anpassen, falls nötig

    # Seite öffnen
    driver.get("https://www.wetter.com/gesundheit/pollenflug/")

    # Land umwandeln
    if country == 'DE':
        country = 'Deutschland'
    elif country == 'AT':
        country = 'Österreich'
    elif country == 'CH':
        country = 'Schweiz'

    try:
        # Button "Akzeptieren und weiter" anklicken
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "cmp-btn-accept"))
            ).click()
        except Exception as e:
            logging.warning(f"Fehler beim Akzeptieren der Cookies in {ort}, {country}: {e}")

        # <div> mit Suchfeld finden
        suchfeld_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="layout__item one-third lap-one-whole palm-one-whole float--left desk-pr lap-pr palm-mb"]'))
        )

        # Ortseingabefeld innerhalb des <div> finden
        ort_eingabe = WebDriverWait(suchfeld_div, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        ort_eingabe.clear()
        ort_eingabe.send_keys(f"{ort} {country}")

        # Suche auslösen durch Drücken der Enter-Taste im Eingabefeld
        ort_eingabe.send_keys(Keys.ENTER)

        # Pollentabelle abwarten
        pollen_tabelle = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".js-tab.is-active[data-tab-target='pollen-active']"))
        )

        # Pollen-Elemente finden
        pollen_elemente = pollen_tabelle.find_elements(By.CSS_SELECTOR, "tr[data-snippet]")

        # Daten extrahieren und in ein Dictionary sammeln
        pollen_data = {}
        for element in pollen_elemente:
            pollenart = element.find_element(By.CSS_SELECTOR, "td:first-child").text

            # Belastungswert ermitteln
            belastungs_element = element.find_element(By.CSS_SELECTOR, "td[class^='pollen-index']")
            belastung_heute = belastungs_element.find_element(By.CSS_SELECTOR, "div").text
            
            # Daten ins Dictionary einfügen
            pollen_data[pollenart] = belastung_heute

        return pollen_data

    except Exception as e:
        logging.error(f"Fehler bei der Verarbeitung der Ortschaft {ort}, {country}: {e}")
        return None

    finally:
        driver.quit()

# CSV-Datei einlesen
csv_file_path = 'backend/DataGathering/AllStations_with_location_info.csv'
data = pd.read_csv(csv_file_path)

# Filtern der Daten
data = data[~data['country'].isin(['FR', 'IT','LI'])]
data=data[data['city']!="Unknown"]
# Liste zum Sammeln der Daten
all_data = []

# Aktuelles Datum
current_date = datetime.now().strftime('%Y-%m-%d')

# Über die Städte im CSV file loopen
for index, row in data.iterrows():
    city = row['city']
    coordinates = row['Koordinaten']
    country = row['country']
    
    try:
        # Pollen-Daten für die Stadt holen
        pollen_data = get_pollen_data(city, country)
        
        if pollen_data:
            # Datum und Koordinaten hinzufügen
            pollen_data['date'] = current_date
            pollen_data['Koordinaten'] = coordinates
            
            # Daten zur Liste hinzufügen
            all_data.append(pollen_data)
        else:
            logging.warning(f"Keine Daten für {city}, {country} erhalten.")
    except Exception as e:
        logging.error(f"Fehler bei der Verarbeitung der Ortschaft {city}, {country}: {e}")

# finalen DataFrame erstellen
final_df = pd.DataFrame(all_data)

# finalen DataFrame ausgeben und speichern
print(final_df)
final_df.to_csv('backend/DataGathering/PollenData.csv', index=False)
