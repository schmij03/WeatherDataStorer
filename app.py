from flask import Flask, jsonify, render_template
from pymongo import MongoClient
from backend.DataGathering.mongodb_connection import connect_mongodb

app = Flask(__name__)

# Verbindung zur MongoDB-Datenbank
db, collection = connect_mongodb()


@app.route('/api/stations')
def get_stations():
    db, stations_collection = connect_mongodb()  # Verwendet die Verbindungsfunktion, um die Datenbank und Kollektion zu erhalten
    stations = list(stations_collection.find({}, {'_id': 0}))  # Exclude the _id field
    return jsonify(stations)

@app.route('/api/regions')
def get_regions():
    db, regions_collection = connect_mongodb()  # Verwendet die Verbindungsfunktion, um die Datenbank und Kollektion zu erhalten
    regions = list(regions_collection.find({}, {'_id': 0}))  # Exclude the _id field
    return jsonify(regions)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
