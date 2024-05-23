import pandas as pd
from getStationInformations import meteostat_filtered, openweathermap_filtered
from GeoAdminData import main

# Daten laden
data2 = meteostat_filtered
data3 = openweathermap_filtered
time_str, weather_geoadmin_df, geoadmin_stations = main()
data = geoadmin_stations

# Zusammenführen der DataFrames
df_combined_filtered = pd.merge(data, data2, on='Koordinaten', how='outer', suffixes=('_geoadmin', '_meteos'))
df_combined_filtered = pd.merge(df_combined_filtered, data3, on='Koordinaten', how='outer', suffixes=('', '_openweather'))

# Generieren einer Liste der Spalten, die mit den angegebenen Suffixen enden
suffixes = ('_meteos', '_openweather', '_geoadmin')
to_consolidate = [col.split(suffix)[0] for col in df_combined_filtered.columns for suffix in suffixes if col.endswith(suffix)]

# Entfernen der Duplikate aus der Liste
to_consolidate = list(set(to_consolidate))

# Zusammenführen der Spalten mit den Suffixen
for col in to_consolidate:
    main_col = df_combined_filtered[col] if col in df_combined_filtered.columns else pd.Series()
    for suffix in suffixes:
        suffix_col = col + suffix
        if suffix_col in df_combined_filtered.columns:
            main_col = main_col.fillna(df_combined_filtered[suffix_col])
    df_combined_filtered[col] = main_col
    df_combined_filtered.drop([col + suffix for suffix in suffixes if (col + suffix) in df_combined_filtered.columns], axis=1, inplace=True)

df_combined_filtered = df_combined_filtered.drop_duplicates(subset=['Koordinaten'])

# Speichern des aktualisierten DataFrames in eine CSV-Datei
output_path = 'backend/DataGathering/AllStations_with_location_info.csv'
df_combined_filtered.to_csv(output_path, index=False)
