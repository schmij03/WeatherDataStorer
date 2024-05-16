import json
import pandas as pd
from meteostat import Stations
from shapely.geometry import Polygon, Point
import base64
import requests
from io import StringIO
import gzip

with open('backend/DataGathering/pwd.json') as f:
    credentials = json.load(f)
    username = credentials['meteomatics_credentials']['username']
    password = credentials['meteomatics_credentials']['password']

# Encode credentials to Base64 and set up the authorization header
credentials = base64.b64encode(f"{username}:{password}".encode()).decode('utf-8')
headers = {'Authorization': f'Basic {credentials}'}

# Requesting the token
response = requests.get('https://login.meteomatics.com/api/v1/token', headers=headers)
if response.status_code == 200:
    token = response.json()['access_token']
    print('Token successfully obtained:', token)
else:
    print('Error obtaining token:', response.text)

# Load and prepare polygon coordinates
with open('backend/DataGathering/rendercoordinates.json', 'r') as file:
    coords = json.load(file)['rendercoordinates']
    polygon = Polygon([(coord['lat'], coord['lng']) for coord in coords])

# Helper function to check if a station is within the polygon
def is_in_polygon(station):
    point = Point(station['latitude'], station['longitude'])
    return polygon.contains(point)

def fetch_and_prepare_stations(countries):
    data_frames = []
    for country in countries:
        try:
            # Fetch stations and ensure they are fetched correctly
            stations = Stations().region(country).fetch()
            if stations.empty:
                continue  # Skip if no data is available
            data_frames.append(stations)
        except Exception as e:
            # Optionally log the error to a file or logging system
            pass

    if not data_frames:
        return pd.DataFrame()  # Return an empty DataFrame if no data was fetched

    # Concatenate all DataFrames, reset index, and reformat columns
    result = pd.concat(data_frames)
    result['Location Lat,Lon'] = result['latitude'].astype(str) + ',' + result['longitude'].astype(str)
    return result

# URL for weather stations in different countries
countries = ["switzerland", "italy", "austria", "germany", "france"]

# List of country_codes
country_codes = ['CH', 'DE', 'AT', 'IT', 'FR']
stations = fetch_and_prepare_stations(country_codes)

stations = stations.reset_index()

# Filter stations inside the polygon
stations['In Polygon'] = stations.apply(is_in_polygon, axis=1)

filtered_stations = stations[stations['In Polygon']].drop(columns='In Polygon')
filtered_stations = filtered_stations.rename(columns={'name': 'Ort', 'id': 'id_meteostat', 'Location Lat,Lon': 'Koordinaten'})

meteostat_filtered = filtered_stations.drop(columns=['latitude', 'longitude', 'region', 'hourly_start', 'hourly_end', 'daily_start', 'daily_end', 'monthly_start', 'monthly_end'])
# Save to CSV
meteostat_filtered.to_csv('backend/DataGathering/meteostat_stations_filtered.csv')
# Collecting data for each country
dataframes = []
for country in countries:
    url = f"https://api.meteomatics.com/find_station?location={country}"
    response = requests.get(url, headers={'Authorization': f'Bearer {token}'})
    if response.status_code == 200:
        # Converting CSV data to DataFrame
        df = pd.read_csv(StringIO(response.text), delimiter=';')
        dataframes.append(df)
    else:
        print(f'Error retrieving data for {country}:', response.text)


# Combining all DataFrames into one and cleaning up columns
if dataframes:
    combined_df = pd.concat(dataframes).drop(columns=["Horizontal Distance", "Vertical Distance", 'Effective Distance'])


def is_in_polygon1(station, lat_lon_col='Location Lat,Lon'):
    try:
        # Split the 'lat_lon' column on the comma
        lat, lon = map(float, station[lat_lon_col].split(','))
        # Create a Point object
        point = Point(lat, lon)
        # Return whether the point is within the polygon
        return polygon.contains(point)
    except ValueError:
        # Handle cases where the data cannot be converted to float or split correctly
        return False

# Assuming `polygon` is correctly defined
if 'combined_df' in locals():
    # Apply the function and check if each station is within the polygon
    combined_df['in_polygon'] = combined_df.apply(is_in_polygon1, axis=1)
    # Filter DataFrame to only include rows where 'in_polygon' is True
    filtered_df = combined_df[combined_df['in_polygon']].copy()
    filtered_df['elevation'] = filtered_df['Elevation'].str.replace('m', '').astype(float)
    meteomatics_filtered=filtered_df.drop(columns={'in_polygon', 'Start Date', 'End Date','Elevation'}).rename(columns={'Name': 'Ort'})
    meteomatics_filtered['id_meteomatics']=meteomatics_filtered['Location Lat,Lon']
    # Save the filtered DataFrame to CSV
    meteomatics_filtered.to_csv('backend/DataGathering/meteomatics_stations_filtered.csv', index=False)



def download_and_create_dataframe(url, country_codes):
    # Download file from the URL
    response = requests.get(url)
    if response.status_code == 200:
        # Hold GZIP file content in a temporary storage
        compressed_file = response.content
        
        # Decompress GZIP file
        decompressed_file = gzip.decompress(compressed_file)
        
        # Load JSON data
        json_data = json.loads(decompressed_file)
        
        # Filter data by specific country codes
        filtered_data = [city for city in json_data if city['country'] in country_codes]
        
        # Convert to a Pandas DataFrame
        df = pd.DataFrame(filtered_data)
        
        # Split 'coord' column into 'lon' and 'lat'
        df['longitude'] = df['coord'].apply(lambda x: x['lon'])
        df['latitude'] = df['coord'].apply(lambda x: x['lat'])
        
        # Remove 'coord' column as it is no longer needed
        df.drop('coord', axis=1, inplace=True)
        
        # Return the DataFrame
        return df
    else:
        print("Error downloading file:", response.status_code)
        return None

# URL of the GZIP file
url_openweathermap = "https://bulk.openweathermap.org/sample/city.list.json.gz"

# Create DataFrame
openweathermap_df = download_and_create_dataframe(url_openweathermap, country_codes)

openweathermap_df['in_polygon'] = openweathermap_df.apply(is_in_polygon, axis=1)
openweathermap_filtered = openweathermap_df[openweathermap_df['in_polygon']].drop(columns='in_polygon')
openweathermap_filtered = openweathermap_filtered.drop(columns={'state'})
openweathermap_filtered['Koordinaten'] = openweathermap_filtered['latitude'].astype(str) + ',' + openweathermap_filtered['longitude'].astype(str)
openweathermap_filtered = openweathermap_filtered.drop(columns=['latitude', 'longitude'])
openweathermap_filtered = openweathermap_filtered.reset_index(drop=True).rename(columns={'id': 'id_openweathermap', 'name': 'Ort'})

openweathermap_filtered.to_csv('backend/DataGathering/openweathermap_stations_filtered.csv', index=False)

print("All stations have been filtered and saved to CSV files.")
