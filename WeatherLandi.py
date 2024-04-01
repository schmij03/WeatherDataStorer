from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def landi_wetter_ortschaft_eingeben(ortschaft):
    # Pfad zum ChromeDriver
    driver_path = "C:\\Users\\jansc\\Downloads\\chromedriver\\chromedriver.exe"
    
    # Erstellen einer neuen Chrome-Sitzung
    driver = webdriver.Chrome(executable_path=driver_path)
    driver.get('https://www.landi.ch/wetter/lokalprognose')
    
    # Finden des Eingabefelds für die Ortschaft
    search_box = driver.find_element_by_name('query')
    
    # Eingabe der Ortschaft und Abschicken der Suche
    search_box.send_keys(ortschaft)
    search_box.send_keys(Keys.RETURN)
    
    # Hier können Sie nun weitere Schritte programmieren, z.B. das Auslesen der Wetterdaten
    
    # Schließen des Browsers
    # driver.quit()

# Verwendung der Funktion mit einer Beispielortschaft
landi_wetter_ortschaft_eingeben('Zürich')
