import pandas as pd
import requests
from datetime import datetime
from io import StringIO
import time
from pymongo.mongo_client import MongoClient
import numpy as np

from mongodb_connection import connect_mongodb

# Function to load CSV data from file path
def load_csv_data(filepath):
    try:
        return pd.read_csv(filepath, sep=',')
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Function to fetch CSV data from URL
def fetch_csv_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text), sep=';')
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

# Function to convert date format
def convert_date(date_str):
    date_str = str(date_str)
    return datetime.strptime(date_str, '%Y%m%d%H%M').strftime('%Y-%m-%d %H:%M')

# Function to replace column names
def replace_column_names(df, mapping):
    df.columns = [mapping.get(col, col) for col in df.columns]
    return df

# Function to add canton information
def add_canton(df, stations_df):
    df = df.merge(stations_df[['Abk.', 'Kanton']], left_on='Station/Location', right_on='Abk.', how='left')
    df.drop(columns=['Abk.'], inplace=True)
    return df

def main():
    # URLs for CSV files
    weather_data_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv'
    stations_desc = 'Stationsbeschreibungen.csv' 
    rain_data_url = 'https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA98.csv'

    # Fetch data
    rain_df = fetch_csv_data(rain_data_url)
    weather_df = fetch_csv_data(weather_data_url)
    stations_df = load_csv_data(stations_desc)

    if weather_df is not None and stations_df is not None:
        stations_df.set_index('Abk.', inplace=True)

        # Merge to add station name and canton
        weather_df = weather_df.merge(stations_df[['Kanton', 'Stationstyp']],  left_on='Station/Location', right_index=True, how='left')
        rain_df = rain_df.merge(stations_df[['Kanton', 'Stationstyp']],  left_on='Station/Location', right_index=True, how='left')

        # Add a 'W' if the station type is 'Wetterstation', otherwise 'N'
        weather_df['Stationstyp'] = weather_df['Stationstyp'].apply(lambda x: 'W' if x == 'Wetterstation' else 'N')
        rain_df['Stationstyp'] = rain_df['Stationstyp'].apply(lambda x: 'W' if x == 'Wetterstation' else 'N')

        # Convert date format
        weather_df['Date'] = weather_df['Date'].apply(convert_date)
        rain_df['Date'] = rain_df['Date'].apply(convert_date)
       
        # Check if canton has been included
        print(rain_df.head())
        print(weather_df.head())

        # Replace '-' with NaN
        rain_df.replace('-', np.nan, inplace=True)
        weather_df.replace('-', np.nan, inplace=True)

        merged_df = pd.merge(weather_df, rain_df, left_on=['Station/Location', 'Date', 'Kanton', 'rre150z0', 'Stationstyp'], right_on=['Station/Location', 'Date', 'Kanton', 'rre150z0', 'Stationstyp'], how='outer')
        merged_df.rename(columns={'Station/Location': 'Station'}, inplace=True)
        print(merged_df.head())

        records = merged_df.to_dict(orient='records')
        db, collection = connect_mongodb()
        if db is not None and collection is not None:
            # Konvertierung des DataFrame zu Dictionary und Speicherung in MongoDB
            collection.insert_many(records)
            print("Wetterdaten erfolgreich in MongoDB gespeichert.")
        
        current_time = datetime.now()
        formatted_time = current_time.strftime("%H:%M:%S")
        print("Current time is:", formatted_time)

# Infinite loop to run the code every 30 Minutes
while True:
    main()
    time.sleep(1800)
