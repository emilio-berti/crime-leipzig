import sys
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry import Polygon
from geopy.geocoders import Nominatim
import plotly.express as px

if len(sys.argv) == 1:
    clean = False
else:
    clean = sys.argv[1]

if clean:
    # read crime csv --------
    d = pd.read_csv("data/crimes.csv")
    places = d.place
    streets = d.street

    # locate addresses ----------
    geolocator = Nominatim(user_agent = "GetLoc")
    lat = [None for x in places]
    lon = [None for x in places]
    for i in range(len(places)):
        print("  -", i + 1, "of", len(places))
        if (streets[i] != streets[i]): #street is nan
            coords = geolocator.geocode(places[i]) #use only place
        else:
            coords = geolocator.geocode(streets[i] + ', ' + places[i]) #use also street
        if coords is None:
            lat[i] = None
            lon[i] = None
        else:
            lat[i] = coords[1][0]
            lon[i] = coords[1][1]

    # remove locations that were not found ----------
    while None in lat:
        empty = lat.index(None)
        lat.pop(empty)
        lon.pop(empty)
        d = d.drop(empty)

    # create geodataframe --------
    geom = [Point(lon[i], lat[i]) for i in range(len(lat))]
    d['geometry'] = geom
    d = gpd.GeoDataFrame(d, crs = "EPSG:4326")
    s = [1 if x != x else 3 for x in d.street]
    d['size'] = s
    d.to_file("data/crimes.shp")

geo = gpd.read_file("data/crimes.shp")
px.set_mapbox_access_token(open(".mapbox_token").read())
fig = px.scatter_mapbox(
    geo,
    lat = geo.geometry.y,
    lon = geo.geometry.x,
    size = "size",
    opacity = 0.75,
    hover_name = "title",
    hover_data = ["title", "place", "street", "date", "people"],
    zoom = 10,
    color = "title"
)
fig.show()
