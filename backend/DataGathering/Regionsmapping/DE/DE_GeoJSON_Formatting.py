import json

def extract_data_from_geojson(file_path):
    # Load GeoJSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Function to decode Unicode escape sequences
    def decode_unicode_escape(s):
        if isinstance(s, str):
            return s.encode('latin1').decode('unicode_escape')
        return s

    # List to store extracted information
    extracted_data = []

    # Iterate through all features and extract the desired information
    for feature in data['features']:
        lan_name = decode_unicode_escape(feature['properties'].get('lan_name'))
        krs_shortname = decode_unicode_escape(feature['properties'].get('krs_name_short'))
        coordinates = feature['geometry'].get('coordinates')

        extracted_data.append({
            'lan_name': lan_name,
            'krs_shortname': krs_shortname,
            'coordinates': coordinates
        })

    # Return the extracted data as JSON
    return extracted_data


def filter_data(data):
    # List to store extracted information
    extracted_data = []

    # Iterate through all features and extract the desired information
    for feature in data:
        lan_name = feature.get('lan_name')[0]
        krs_shortname = feature.get('krs_shortname')[0]
        coordinates = feature.get('coordinates')

        if lan_name in ['Baden-Württemberg', 'Bayern'] and krs_shortname in [
            'Oberallgäu', 'Lindau (Bodensee)', 'Breisgau-Hochschwarzwald',
            'Landkreis Bodenseekreis', 'Ravensburg', 'Waldshut', 'Lörrach',
            'Landkreis Schwarzwald-Baar-Kreis', 'Tuttlingen', 'Sigmaringen']:
            extracted_data.append({
                'lan_name': lan_name,
                'krs_shortname': krs_shortname,
                'coordinates': coordinates
            })

    # Return the filtered data
    return extracted_data


# Call the function and output the result
file_path = 'backend/DataGathering/Regionsmapping/DE/Files/georef-germany-kreis@public.geojson'
formatted = extract_data_from_geojson(file_path)
filtered = filter_data(formatted)

# Write the filtered data to a file
output_path = 'backend/DataGathering/Regionsmapping/DE/Files/extracted_data_ba_bw.json'
with open(output_path, 'w', encoding='utf-8') as outfile:
    json.dump(filtered, outfile, indent=4, ensure_ascii=False)

# Return the filtered data as a JSON string
filtered_json = json.dumps(filtered, indent=4, ensure_ascii=False)
