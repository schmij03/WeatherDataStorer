import requests
import pandas as pd
import zipfile
import io
import os

def download_and_extract_data(url, extract_to='temp_data'):
    """
    Download the ZIP file and extract its contents.
    """
    response = requests.get(url)
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        zip_file.extractall(extract_to)
    print(f"Data extracted to {extract_to}")

def load_data_to_dataframe(extract_to='temp_data'):
    """
    Load the CSV file into a pandas DataFrame.
    Assumes there's only one CSV file in the directory.
    """
    for file_name in os.listdir(extract_to):
        if file_name.endswith('.csv'):
            file_path = os.path.join(extract_to, file_name)
            df = pd.read_csv(file_path)
            print(f"Loaded data from {file_name}")
            return df
    print("No CSV file found.")
    return None

def cleanup_temp_data(extract_to='temp_data'):
    """
    Clean up the extracted files to avoid clutter.
    """
    for file_name in os.listdir(extract_to):
        file_path = os.path.join(extract_to, file_name)
        os.remove(file_path)
    print("Temporary data cleaned up.")

def main():
    data_url = "https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/data.zip"
    extract_to = "temp_data"

    # Download and extract data
    download_and_extract_data(data_url, extract_to)
    
    # Load data into DataFrame
    df = load_data_to_dataframe(extract_to)
    
    if df is not None:
        print(df.head())  # Beispiel: Anzeigen der ersten Zeilen des DataFrame
    
    # Clean up temporary data
    cleanup_temp_data(extract_to)

if __name__ == "__main__":
    main()
