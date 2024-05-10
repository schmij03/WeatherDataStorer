import pandas as pd
from shapely.geometry import Point
import geopandas as gpd

# Lade den CSV-Datensatz
new_file_path = f'backend/DataGathering/Merged_Stations.csv'
merged_stations_df = pd.read_csv(new_file_path)

# Entferne Leerzeichen aus den Spaltennamen
merged_stations_df.columns = merged_stations_df.columns.str.replace(' ', '')

# Zeige die ersten Zeilen des Datensatzes an, um den Aufbau zu verstehen
print(merged_stations_df.head())

# Trenne Latitude und Longitude in separate Spalten
# Passe hier den Namen der Spalte an, die die Koordinaten enthält (z. B. 'LocationLatLon')
merged_stations_df[['Latitude', 'Longitude']] = merged_stations_df['LocationLat,Lon'].str.split(',', expand=True)

# Konvertiere die neuen Spalten in float (numerische Werte)
merged_stations_df['Latitude'] = merged_stations_df['Latitude'].astype(float)
merged_stations_df['Longitude'] = merged_stations_df['Longitude'].astype(float)

# Erstelle die GeoDataFrame mit den geografischen Punkten
geometry = [Point(xy) for xy in zip(merged_stations_df['Longitude'], merged_stations_df['Latitude'])]
geo_df = gpd.GeoDataFrame(merged_stations_df, geometry=geometry)

# Lade das Shapefile
shapefile_path = f'backend\DataGathering\Bezirksmapping\swissBOUNDARIES3D_1_5_TLM_BEZIRKSGEBIET.shp'  # Pfad zum Shapefile anpassen
regions_gdf = gpd.read_file(shapefile_path)

# Setze das Koordinatensystem (CRS)
geo_df = geo_df.set_crs(regions_gdf.crs, allow_override=True)

# Räumlicher Join zwischen Stationen und Regionen
geo_df = gpd.sjoin(geo_df, regions_gdf, how='left', op='within')

# Benenne die relevante Spalte um (passe 'BEZIRKSGEBIET' an)
geo_df = geo_df.rename(columns={'BEZIRKSGEBIET': 'Mapped_Region'})

# Zeige die ersten Zeilen des aktualisierten Datensatzes an
print(geo_df[['Ort', 'Kanton', 'Latitude', 'Longitude', 'Mapped_Region']])
