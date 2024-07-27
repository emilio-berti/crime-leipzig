import pandas as pd 
import geopandas as gpd
from geocrime import map

d = pd.read_csv("data/crimes.csv")
d = map.geolocate(d)
# geo = shape(geo)

geo = gpd.read_file("data/crimes.shp")
map.map(geo)
