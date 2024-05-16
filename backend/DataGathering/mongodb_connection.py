from pymongo.mongo_client import MongoClient
import json

# Load the MongoDB connection credentials from a JSON file
with open("backend/DataGathering/pwd.json") as f:
    credentials = json.load(f)
    password = credentials["mongodb_credentials"]['password']
    username = credentials["mongodb_credentials"]['username']
    database = credentials["mongodb_credentials"]['database']


def connect_mongodb():
    # MongoDB connection URI
    uri = f"mongodb+srv://{username}:{password}@{database}.zebph6n.mongodb.net/?retryWrites=true&w=majority&appName=WeatherData"
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

def save_to_mongodb(df):
    # Connect to the MongoDB server
    db, collection = connect_mongodb()

    # Convert the DataFrame to a dictionary
    data = df.to_dict(orient='records')

    # Insert the data into the MongoDB collection
    collection.insert_many(data)

    # Close the connection
    db.client.close()
    print("Data saved to MongoDB!")


def clear_mongodb():
    # Connect to the MongoDB server
    db, collection = connect_mongodb()

    # Delete all documents in the collection
    result = collection.delete_many({})

    # Check if the deletion was successful
    if result.deleted_count > 0:
        print("Collection cleared.")
    else:
        print("No documents found to delete.")

    # Close the connection
    db.client.close()