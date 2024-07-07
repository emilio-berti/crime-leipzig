import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
import plotly.express as px

# # mapbox token ---------
# token = pd.read_csv("tokens.csv")
# token = token[token.app == 'mapbox'].token[0]

# read crime csv --------
d = pd.read_csv("data/crimes.csv")
places = d.place

# locate addresses ----------
geolocator = Nominatim(user_agent = "GetLoc")
lat = [None for x in places]
lon = [None for x in places]
for i in range(len(places)):
    coords = geolocator.geocode(places[i])
    lat[i] = coords[1][0]
    lon[i] = coords[1][1]

geom = [Point(lon[i], lat[i]) for i in range(len(lat))]
d['geometry'] = geom
d = gpd.GeoDataFrame(d, crs = "EPSG:4326")
d['size'] = 3

px.set_mapbox_access_token(open(".mapbox_token").read())
fig = px.scatter_mapbox(
    d,
    lat = d.geometry.y,
    lon = d.geometry.x,
    size = "size",
    hover_name = "title",
    hover_data = ["title", "street", "date", "people"],
    zoom = 10,
    color = "title"
)
fig.show()
