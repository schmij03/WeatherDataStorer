from flask import Flask, jsonify, request
from mongodb_connection import connect_mongodb  # Dies importiert Ihre Verbindungsfunktion

app = Flask(__name__)

@app.route('/api/stations')
def get_stations():
    db, collection = connect_mongodb()  # Verwendet die Verbindungsfunktion, um die Datenbank und Kollektion zu erhalten
    stations = list(collection.find({}, {'_id': 0}))  # Exclude the _id field
    return jsonify(stations)

@app.route('/api/region_data')
def get_data_by_region():
    region_name = request.args.get('region')  # Nimmt den Region-Parameter aus der Query-URL
    if not region_name:
        return jsonify({"error": "No region specified"}), 400  # Fehlermeldung, wenn keine Region angegeben ist

    db, collection = connect_mongodb()

    # Aggregations-Pipeline
    pipeline = [
        {"$match": {"region": region_name}}  # Filtert Dokumente nach der spezifizierten Region
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
