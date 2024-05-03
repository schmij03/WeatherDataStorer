from datetime import datetime
import pandas as pd
from meteostat import Stations, Hourly


stations = Stations()
stations = stations.region("DE")
stations = stations.fetch()
stations = stations.reset_index()
stations = stations["region"]
stations = stations.unique()

stations_at = Stations()
stations_at = stations_at.region("AT")
stations_at = stations_at.fetch()
stations_at = stations_at.reset_index()
stations_at = stations_at["region"]
stations_at = stations_at.unique()
print(stations_at)

stations_it = Stations()
stations_it = stations_it.region("IT")
stations_it = stations_it.fetch()
stations_it = stations_it.reset_index()
stations_it = stations_it["region"]
stations_it = stations_it.unique()
print(stations_it)

stations_fr = Stations()
stations_fr = stations_fr.region("FR")
stations_fr = stations_fr.fetch()
stations_fr = stations_fr.reset_index()
stations_fr = stations_fr["region"]
stations_fr = stations_fr.unique()
print(stations_fr)

stations = list(stations) + list(stations_at) + list(stations_it) + list(stations_fr)
print(stations)