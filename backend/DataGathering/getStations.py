import pandas as pd
from Meteostat import fetch_stations
from GeoAdminData import main

time_str, weather_geoadmin_df, rainfall_geoadmin_df,merged_geoadmin_df = main()
# Fetch the Swiss weather stations
stations = fetch_stations('CH')
stations=stations.reset_index()

combined=stations
combined=combined.drop(columns=["wmo","icao","latitude","longitude","elevation","timezone","hourly_start","hourly_end","daily_start","daily_end","monthly_start","monthly_end"])
weather_geoadmin_df=weather_geoadmin_df.drop(columns=["Lufttemperatur 2 m über Boden; Momentanwert","Niederschlag; Zehnminutensumme","Sonnenscheindauer; Zehnminutensumme","Globalstrahlung; Zehnminutenmittel","Relative Luftfeuchtigkeit 2 m über Boden; Momentanwert","Taupunkt 2 m über Boden; Momentanwert","Windrichtung; Zehnminutenmittel","Windgeschwindigkeit; Zehnminutenmittel","Böenspitze (Sekundenböe); Maximum","Luftdruck auf Stationshöhe (QFE); Momentanwert","Luftdruck reduziert auf Meeresniveau (QFF); Momentanwert","Luftdruck reduziert auf Meeresniveau mit Standardatmosphäre (QNH); Momentanwert","Geopotentielle Höhe der 850 hPa-Fläche; Momentanwert","Geopotentielle Höhe der 700 hPa-Fläche; Momentanwert","Windrichtung vektoriell; Zehnminutenmittel; Instrument 1","Windgeschwindigkeit Turm; Zehnminutenmittel","Böenspitze (Sekundenböe) Turm; Maximum","Lufttemperatur Instrument 1","Relative Luftfeuchtigkeit Turm; Momentanwert","Taupunkt Turm","Stationstyp","Datum","Föhnindex"])

#combined=combined.merge(weather_geoadmin_df[['Kürzel']], left_on='name', right_on='Ort', how='left')
print(weather_geoadmin_df)
print(combined)

# Initialize a list to collect new rows
weather_geoadmin_df['id'] = [None] * len(weather_geoadmin_df)
new_rows = []

# Iterate through combined and match `name` with `Ort` in weather_geoadmin_df
for index, row in combined.iterrows():
    matching =weather_geoadmin_df.loc[weather_geoadmin_df['Ort'] == row['name']]
    if not matching.empty:
        weather_geoadmin_df.loc[weather_geoadmin_df['Ort'] == row['name'], 'id'] = row['id']

    else:
        # If the `name` isn't found in weather_geoadmin_df's `Ort`, add a new row
        new_row = {
            'Kürzel': '',  # Leave this empty, as it's not available in combined
            'Kanton': row['region'],  # Use the `region` field from combined
            'Ort': row['name'],
            'id': row['id']  # Add the `id` field from combined
        }
        new_rows.append(new_row)

# Create a new DataFrame from the new rows
new_df = pd.DataFrame(new_rows)

# Concatenate the original and new rows
final_df = pd.concat([weather_geoadmin_df, new_df], ignore_index=True)
final_df['country']='CH'
final_df=final_df.sort_values(by='Kanton')
final_df=final_df.reset_index(drop=True)
final_df.to_csv(f"backend/DataGathering/Stations.csv", index=False)