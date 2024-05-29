# WeatherDataStorer

## Überblick
WeatherDataStorer ist eine innovative Lösung die darauf abzielt, Wetterdaten effizient zu sammeln und zu speichern. Dieses Projekt wurde im Rahmen der Bachelorarbeit mit der Thematik der Aggregation historischer Wetterdatern der Schweiz und deren Nachbarsregionen erstellt.

## Hauptfunktionen
- **Automatische Datenerfassung**: Sammelt in Echtzeit Wetterdaten von verschiedenen öffentlichen APIs.
- **Intuitive Datenvisualisierung**: Bietet ein [interaktives Frontend](https://github.com/schmij03/HistoricWeatherDataFrontend), um die gespeicherten Wetterdaten ansprechend zu präsentieren.
- **Datenverwaltung**: Implementiert eine leistungsfähige MongoDB-Datenbank zur effizienten Datenverarbeitung und -speicherung.

## Verzeichnisstuktur
```
Backend/
├── .gitattributes
├── .gitignore
├── backend/
│ └── DataGathering/
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
```

## Dateien
- `.gitattributes`: Git-Konfigurationsdatei für Attribute.
- `.gitignore`: Gibt Dateien und Verzeichnisse an, die von git ignoriert werden sollen.
- `backend/`: Verzeichnis, das backend-bezogene Skripte und Dateien enthält.
    - `DataGathering/`: Verzeichnis, das für das Sammeln und Verarbeiten von Daten verantwortlich ist.
        - `Access_Information`: Enthält das leere pwd.json File.
        - `AllStations_with_location_info.csv`: CSV-Datei mit Standortinformationen aller Stationen.
        - `bin`: Nicht benötigte Files.
        - `empty_weather_data.csv`: Leere CSV-Datei für Wetterdaten.
        - `GeoAdmin/`: Verzeichnis mit Stationsbeschreibungen und Informationen zum GeoAdminData.py File.
        - `GeoAdminData.py`: Python-Skript zur Handhabung von GeoAdmin-Daten.
        - `getStationInformations.py`: Python-Skript zum Abrufen von Stationsinformationen.
        - `mergeAllStations.py`: Python-Skript zum Zusammenführen von Daten aller Stationen.
        - `Meteostat.py`: Python-Skript zur Interaktion mit der Meteostat-API oder -Daten.
        - `meteostat_stations_filtered.csv`: Gefilterte CSV-Datei mit Meteostat-Stationen.
        - `mongodb_connection.py`: Python-Skript zur Verbindung mit einer MongoDB-Datenbank.
        - `openweathermap.py`: Python-Skript zur Interaktion mit der OpenWeatherMap-API.
        - `openweathermap_stations_filtered.csv`: Gefilterte CSV-Datei mit OpenWeatherMap-Stationen.
        - `pwd.json`: JSON-Datei mit Passwörtern und API Keys.
        - `region_mapping.py`: Python-Skript zur Zuordnung von Regionen.
        - `Regionsmapping/`: Verzeichnis, das Daten und Skripte im Zusammenhang mit der Zuordnung von Regionen enthält.
        - `rendercoordinates.json`: JSON-Datei mit Koordinateninformationen.
- `Dockerfile`: Docker-Konfigurationsdatei zum Erstellen des Projekts.
- `Dockerfile raspi`: Docker-Konfigurationsdatei, die speziell für Raspberry Pi angepasst ist.
- `main.py`: Das Hauptskript zum Ausführen des Backends.
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


