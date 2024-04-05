import csv

# Dateinamen
input_file = r'C:\Users\jansc\Downloads\ch.meteoschweiz.messnetz-automatisch_de.csv'
output_file = 'Stationsbeschreibungen.csv'

# Öffnen der Datei mit einer anderen Zeichenkodierung und Entfernen der Anführungszeichen
with open(input_file, 'r', encoding='latin-1') as file:
    reader = csv.reader((line.replace('"', '') for line in file), delimiter=';')
    lines = list(reader)

# Schreiben der Daten in eine neue CSV-Datei
with open(output_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(lines)

print("CSV-Datei wurde erfolgreich erstellt.")
