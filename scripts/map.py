import sys
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry import Polygon
from geopy.geocoders import Nominatim
import plotly.express as px
import plotly.io as pio

if len(sys.argv) == 1:
    clean = True
else:
    clean = sys.argv[1]

if clean:
    # read crime csv --------
    d = pd.read_csv("data/crimes.csv")
    streets = d.street
    places = d.district
    places = [x.replace(' (', ', ').replace(')', '') for x in places]
    places = ['Leipzig, ' + x if 'Leipzig' not in x else x for x in places]

    # locate addresses ----------
    geolocator = Nominatim(user_agent = "GetLoc")
    lat = [None for x in places]
    lon = [None for x in places]
    for i in range(len(places)):
        print("  -", i + 1, "of", len(places))
        try:
            if streets[i] != streets[i]:
                coords = geolocator.geocode(places[i])
            else:
                coords = geolocator.geocode(places[i] + ', ' + streets[i])
            if coords is None:
                coords = geolocator.geocode(places[i])
            if coords is None:
                lat[i] = None
                lon[i] = None
            else:
                lat[i] = coords[1][0]
                lon[i] = coords[1][1]
        except Exception as e:
            lat[i] = None
            lon[i] = None

    d.loc[:, 'latitude'] = pd.to_numeric(lat)
    d.loc[:, 'longitude'] = pd.to_numeric(lon)
    d = d.dropna(subset = 'latitude')
    d.loc[:, 'geometry'] = [Point(d['longitude'][i], d['latitude'][i]) for i in d.index]
    d = gpd.GeoDataFrame(d, crs = "EPSG:4326")
    d.to_file("data/crimes.shp")

geo = gpd.read_file("data/crimes.shp")
geo['size'] = 2
px.set_mapbox_access_token(open(".mapbox_token").read())
fig = px.scatter_mapbox(
    geo,
    lat = geo.geometry.y,
    lon = geo.geometry.x,
    opacity = 0.75,
    size = "size",
    hover_name = "crime",
    hover_data = ["crime", "district", "street", "date"],
    zoom = 10,
    color = "crime",
    mapbox_style = "satellite-streets"
)
pio.write_image(fig, "figures/map", format = "pdf")
fig.show()
