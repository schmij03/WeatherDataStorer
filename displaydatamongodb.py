from backend.DataGathering.mongodb_connection import connect_mongodb
import pandas as pd

db, collection = connect_mongodb()

region_name = input("Enter the region name: ")
# Aggregations-Pipeline
pipeline = [
    {"$match": {"Region": region_name}},  # Filtert Dokumente nach der spezifizierten Region
    {"$project": {
        "_id": 0}},  # Projektion der relevanten Felder
    {"$group": {
        "_id": "$Zeit",  # Gruppierung nach Zeit
        "average_temperature": {"$avg": "$Temperatur"},  # Durchschnittstemperatur
        "average_dew_point": {"$avg": "$Taupunkt"},  # Durchschnittstaupunkt
        "average_weather_condition": {"$first": "$Wetterbedingung"},  # Wetterbedingung
        "average_wind_direction": {"$avg": "$Windrichtung"},  # Durchschnittswindrichtung
        "average_humidity": {"$avg": "$Luftfeuchtigkeit"},  # Durchschnittsluftfeuchtigkeit
        "average_precipitation": {"$avg": "$Niederschlagsmenge (letzte Stunde)"},  # Durchschnittsniederschlagsmenge
        "average_snowfall": {"$avg": "$Schneefallmenge (letzte Stunde)"},  # Durchschnittsschneefallmenge
        "average_wind_speed": {"$avg": "$Windgeschwindigkeit"},  # Durchschnittswindgeschwindigkeit
        "average_wind_gust": {"$avg": "$Windböen"},  # Durchschnittswindböen
        "average_pressure": {"$avg": "$Luftdruck"},  # Durchschnittsluftdruck
        "average_solar_radiation": {"$avg": "$Sonneneinstrahlungsdauer"}  # Durchschnittssonneneinstrahlungsdauer
    }},{"$sort": {"_id": 1}}
    
]
region_data = list(collection.aggregate(pipeline))
region_df = pd.DataFrame(region_data)

# Funktion zur Konvertierung der Windrichtung von Grad zu Kardinalrichtungen
def get_wind_direction(degrees):
    directions = [
        "N", "NNO", "NO", "ONO", "O", "OSO", "SO", "SSO",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]

# Anwendung der Funktion zur Umrechnung der Windrichtung
region_df['average_wind_direction'] = region_df['average_wind_direction'].apply(get_wind_direction)

# Mapping der Wetterbedingungen
def load_weather_conditions(path):
    df = pd.read_csv(path)
    return dict(zip(df['Code'], df['Wetterbedingung']))

condition_dict = load_weather_conditions("backend\DataGathering\ConditionCodesMeteoStat.csv")
region_df['average_weather_condition'] = region_df['average_weather_condition'].map(condition_dict)
print(region_df)