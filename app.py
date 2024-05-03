from flask import Flask, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "deine_mongodb_uri"
mongo = PyMongo(app)

@app.route('/stationen')
def get_stationen():
    stationen = mongo.db.stationen.find()  
    return jsonify(list(stationen))

@app.route('/regionen')
def get_regionen():
    regionen = mongo.db.regionen.find()  
    return jsonify(list(regionen))

if __name__ == '__main__':
    app.run(debug=True)