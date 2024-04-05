from pymongo.mongo_client import MongoClient


def connect_mongodb():
    # MongoDB connection URI
    uri = "mongodb+srv://weather:erhwLLotcHI8PTxj@weatherdata.zebph6n.mongodb.net/?retryWrites=true&w=majority&appName=WeatherData"
# Create a new client and connect to the server
    client = MongoClient(uri)

# Check if MongoDB connections are successful
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print("Failed to connect to MongoDB:", e)

# Select the specific databases and collections
    db = client["BA"]
    collection = db["WeatherData"]
    return db, collection