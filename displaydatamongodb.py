from backend.DataGathering.mongodb_connection import connect_mongodb
import pandas as pd

db, collection = connect_mongodb()

region_name = input("Enter the region name: ")

# Aggregations-Pipeline
pipeline = [
    {"$match": {"Region": region_name}},  # Filters documents by the specified region
    {"$project": {"_id": 0}}  # Excludes the _id field from the output
]

region_data = list(collection.aggregate(pipeline))

region_df = pd.DataFrame(region_data)
print(region_df)