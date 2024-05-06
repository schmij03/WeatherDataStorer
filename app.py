from flask import Flask, jsonify, request, render_template
from backend.DataGathering.mongodb_connection import connect_mongodb  # Dies importiert Ihre Verbindungsfunktion

app = Flask(__name__)

@app.route('/api/stations')
def get_stations():
    station_name = request.args.get('station')  # Nimmt den station-Parameter aus der Query-URL
    if not station_name:
        return jsonify({"error": "No station specified"}), 400  # Fehlermeldung, wenn keine station angegeben ist
    db, collection = connect_mongodb()  # Verwendet die Verbindungsfunktion, um die Datenbank und Kollektion zu erhalten
    # Aggregations-Pipeline
    pipeline = [
    {
        '$match': {
            'Ort': station_name
        }
    }
    ]

    stations = list(collection.aggregate(pipeline))
    return jsonify(stations)

@app.route('/api/region_data')
def get_data_by_region():
    region_name = request.args.get('region')  # Nimmt den Region-Parameter aus der Query-URL
    if not region_name:
        return jsonify({"error": "No region specified"}), 400  # Fehlermeldung, wenn keine Region angegeben ist

    db, collection = connect_mongodb()

    # Aggregations-Pipeline
    pipeline = [
    {"$match": {"Region": region_name}},  # Filtert Dokumente nach der spezifizierten Region
    {"$project": {
        "_id": 0}},  # Projektion der relevanten Felder
    {"$group": {
        "_id": "$Zeit",  # Gruppierung nach Zeit
        "average_temperature": {"$avg": "$Temperatur"},  # Durchschnittstemperatur
        "average_dew_point": {"$avg": "$Taupunkt"},  # Durchschnittstaupunkt
        "average_weather_condition": {"$first": "$Wetterbedingung"},  # Wetterbedingung
        "average_wind_direction": {"$avg": "$Windrichtung"},  # Durchschnittswindrichtung
        "average_humidity": {"$avg": "$Luftfeuchtigkeit"},  # Durchschnittsluftfeuchtigkeit
        "average_precipitation": {"$avg": "$Niederschlagsmenge (letzte Stunde)"},  # Durchschnittsniederschlagsmenge
        "average_snowfall": {"$avg": "$Schneefallmenge (letzte Stunde)"},  # Durchschnittsschneefallmenge
        "average_wind_speed": {"$avg": "$Windgeschwindigkeit"},  # Durchschnittswindgeschwindigkeit
        "average_wind_gust": {"$avg": "$Windböen"},  # Durchschnittswindböen
        "average_pressure": {"$avg": "$Luftdruck"},  # Durchschnittsluftdruck
        "average_solar_radiation": {"$avg": "$Sonneneinstrahlungsdauer"}  # Durchschnittssonneneinstrahlungsdauer
    }},{"$sort": {"_id": 1}}
    
    ]

    region_data = list(collection.aggregate(pipeline))

    if not region_data:
        return jsonify({"error": "Region not found"}), 404  # Fehlermeldung, wenn keine Daten gefunden werden

    return jsonify(region_data)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
