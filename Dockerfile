# Offizielles Python 3.12-Image als Basis
FROM python:3.12-slim

# Arbeitsverzeichnis im Container
WORKDIR /usr/src/app

# Kopiert die requirements.txt Datei in das Arbeitsverzeichnis
COPY requirements.txt ./

# Installiert die Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiert den gesamten Inhalt des aktuellen Verzeichnisses in das Arbeitsverzeichnis im Container
COPY . .

# Führt das Hauptskript aus, wenn der Container startet
CMD ["python", "main.py"]