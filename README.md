# WeatherDataStorer

## Überblick
WeatherDataStorer ist eine innovative Softwarelösung, die darauf abzielt, Wetterdaten effizient zu sammeln, zu speichern und visuell darzustellen. Dieses Projekt verwendet moderne Technologien wie Python und JavaScript, um eine robuste Plattform für Wetterdatenanalyse zu bieten.

## Hauptfunktionen
- **Automatische Datenerfassung**: Sammelt in Echtzeit Wetterdaten von verschiedenen öffentlichen APIs.
- **Intuitive Datenvisualisierung**: Bietet ein interaktives Frontend, um die gespeicherten Wetterdaten ansprechend zu präsentieren.
- **Datenverwaltung**: Implementiert eine leistungsfähige MongoDB-Datenbank zur effizienten Datenverarbeitung und -speicherung.

## Verzeichnisstuktur
Backend/
├── .gitattributes
├── .gitignore
├── backend/
│ └── DataGathering/
│ ├── pycache/
│ ├── Access_Information
│ ├── AllStations_with_location_info.csv
│ ├── bin
│ ├── empty_weather_data.csv
│ ├── GeoAdmin/
│ ├── GeoAdminData.py
│ ├── getStationInformations.py
│ ├── mergeAllStations.py
│ ├── Meteostat.py
│ ├── meteostat_stations_filtered.csv
│ ├── mongodb_connection.py
│ ├── openweathermap.py
│ ├── openweathermap_stations_filtered.csv
│ ├── pwd.json
│ ├── region_mapping.py
│ ├── Regionsmapping/
│ └── rendercoordinates.json
├── Dockerfile
├── Dockerfile raspi
├── main.py
├── README.md
└── requirements.txt

## Dateien
- `.gitattributes`: Git-Konfigurationsdatei für Attribute.
- `.gitignore`: Gibt Dateien und Verzeichnisse an, die von git ignoriert werden sollen.
- `backend/`: Verzeichnis, das backend-bezogene Skripte und Dateien enthält.
    - `DataGathering/`: Ein Verzeichnis, das für das Sammeln und Verarbeiten von Daten verantwortlich ist.
        - `__pycache__/`: Verzeichnis, das von Python zum Zwischenspeichern kompilierten Bytecodes verwendet wird.
        - `Access_Information`: Enthält wahrscheinlich Zugangsdaten oder Informationen für den Datenzugriff.
        - `AllStations_with_location_info.csv`: CSV-Datei mit Standortinformationen aller Stationen.
        - `bin`: Möglicherweise ein Verzeichnis für Binärdateien oder ausführbare Dateien.
        - `empty_weather_data.csv`: Leere CSV-Datei für Wetterdaten.
        - `GeoAdmin/`: Ein Verzeichnis, das vermutlich Daten oder Skripte im Zusammenhang mit geografischen Verwaltungsdaten enthält.
        - `GeoAdminData.py`: Python-Skript zur Handhabung von GeoAdmin-Daten.
        - `getStationInformations.py`: Python-Skript zum Abrufen von Stationsinformationen.
        - `mergeAllStations.py`: Python-Skript zum Zusammenführen von Daten aller Stationen.
        - `Meteostat.py`: Python-Skript zur Interaktion mit der Meteostat-API oder -Daten.
        - `meteostat_stations_filtered.csv`: Gefilterte CSV-Datei mit Meteostat-Stationen.
        - `mongodb_connection.py`: Python-Skript zur Verbindung mit einer MongoDB-Datenbank.
        - `openweathermap.py`: Python-Skript zur Interaktion mit der OpenWeatherMap-API.
        - `openweathermap_stations_filtered.csv`: Gefilterte CSV-Datei mit OpenWeatherMap-Stationen.
        - `pwd.json`: JSON-Datei mit Passwörtern oder Zugangsdaten.
        - `region_mapping.py`: Python-Skript zur Zuordnung von Regionen.
        - `Regionsmapping/`: Ein Verzeichnis, das wahrscheinlich Daten oder Skripte im Zusammenhang mit der Zuordnung von Regionen enthält.
        - `rendercoordinates.json`: JSON-Datei mit Koordinateninformationen.
- `Dockerfile`: Docker-Konfigurationsdatei zum Erstellen des Projekts.
- `Dockerfile raspi`: Docker-Konfigurationsdatei, die speziell für Raspberry Pi angepasst ist.
- `main.py`: Das Hauptskript zum Ausführen des Backend-Servers.
- `README.md`: Dokumentationsdatei für das Projekt.
- `requirements.txt`: Listet die für das Projekt erforderlichen Abhängigkeiten auf.


## Schnellstart
1. **Repository klonen**: `git clone https://github.com/schmij03/WeatherDataStorer`
2. **Virtual Environment erstellen**: `python -m venv venv`
3. **Virtual Environment starten**: `venv\Scripts\activate`
4. **Abhängigkeiten installieren**: `pip install -r requirements.txt`
5. **Anwendung starten**: `python main.py`

## Docker Image
1. **Docker Installieren**: Falls noch nicht vorhanden Docker installieren.
2. **Repository klonen**: `docker pull schmij03/weatherdatastorer:latest`
3. **Anwendung starten**: `docker run schmij03/weatherdatastorer:latest`

## Docker Image für RaspberryPi
1. **Docker Installieren**: Falls noch nicht vorhanden Docker installieren.
2. **Repository klonen**: `docker pull schmij03/weatherdata-raspi:latest`
3. **Anwendung starten**: `docker run schmij03/weatherdata-raspi:latest`


