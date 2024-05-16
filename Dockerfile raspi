# Verwende ein offizielles Python 3.12-Image für ARM als Basis
FROM --platform=linux/arm64 python:3.12-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /usr/src/app

# Installiere Systemabhängigkeiten
RUN apt-get update && \
    apt-get install -y \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Setze die Umgebungsvariable für GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Kopiere die requirements.txt Datei in das Arbeitsverzeichnis
COPY requirements.txt ./

# Installiere die Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den gesamten Inhalt des aktuellen Verzeichnisses in das Arbeitsverzeichnis im Container
COPY . .

# Führe das Hauptskript aus, wenn der Container startet
CMD ["python", "main.py"]
