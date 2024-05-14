# Verwende ein offizielles Python 3.12-Image als Basis
FROM python:3.12-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /usr/src/app

# Kopiere die requirements.txt Datei in das Arbeitsverzeichnis
COPY requirements.txt ./

# Installiere die Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Inhalt des aktuellen Verzeichnisses in das Arbeitsverzeichnis im Container
COPY COPY /mnt/data/ /destination/path/
COPY /mnt/data/backend /destination/path/backend
COPY /mnt/data/backend/DataGathering /destination/path/backend/DataGathering
COPY /mnt/data/backend/scripts /destination/path/backend/scripts
COPY /mnt/data/requirements.txt /destination/path/
COPY /mnt/data/main.py /destination/path/
COPY /mnt/data/Dockerfile /destination/path/

# Führe das Hauptskript aus, wenn der Container startet
CMD ["python", "main.py"]