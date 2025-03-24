import sys
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry import Polygon
from geopy.geocoders import Nominatim
import plotly.express as px
import plotly.io as pio
import json

if len(sys.argv) == 1:
    clean = True
else:
    clean = sys.argv[1]

if clean:
    # read crime csv --------
    d = pd.read_csv("data/crimes.csv").drop_duplicates()
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
geo['color'] = 'gold'
geo['size'] = 1
px.set_mapbox_access_token(open(".mapbox_token").read())
fig = px.scatter_mapbox(
    geo,
    lat = geo.geometry.y,
    lon = geo.geometry.x,
    opacity = 0.75,
    color_discrete_sequence = ['#FFC300'],
    size = "size",
    size_max = 10,
    hover_name = "crime",
    hover_data = ["district", "street", "date"],
    zoom = 10,
    mapbox_style = "satellite-streets",
    title = "Crimes in Leipzig"
)
fig.write_html("figures/points.html")

districts = gpd.read_file("data/ot.shp")
districts = districts.to_crs(geo.crs)
total_crimes = pd.DataFrame({
    'n': gpd.sjoin(districts, geo).groupby("OT").Name.count()
})
missing_OT = [x for x in districts.OT if x not in total_crimes.index]
total_crimes = pd.concat([
    total_crimes,
    pd.DataFrame(
        {'n': [0 for x in missing_OT], 'OT': missing_OT},
        index = missing_OT
    ).set_index('OT')
])
m = districts.merge(total_crimes, on = "OT")

""" figure """
fig = px.choropleth_mapbox(
    data_frame = m[["Name", "n", "OT"]],
    geojson = json.loads(m.to_json()),
    featureidkey = "properties.OT",
    locations = "OT",
    color = "n",
    opacity = 0.75,
    hover_name = "Name",
    hover_data = ["Name", "n"],
    zoom = 10,
    center = dict(lat = 51.34, lon = 12.38),
    mapbox_style = "satellite-streets",
    color_continuous_scale = ["#584B9F", "#22C4B3", "#FEFDBE", "#F39B29", "#A71B4B"]
)
scatter_trace = px.scatter_mapbox(
    geo,
    lat = geo.geometry.y,
    lon = geo.geometry.x,
    opacity = 0.75,
    color_discrete_sequence = ['#FFC300'],
    size = "size",
    size_max = 10,
    hover_name = "crime",
    hover_data = ["district", "street", "date"],
    zoom = 10,
    mapbox_style = "satellite-streets",
    title = "Crimes in Leipzig"
).data[0]
scatter_trace.visible = False
fig.add_trace(scatter_trace)
fig.update_layout(
    title = {
        'text': "Crime in Leipzig",
        'y': 1,  # Position from top (0-1)
        'x': 0.45,   # Center horizontally
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {
            'size': 24,
            'family': "Arial, sans-serif"
        }
    },
    width = 600,
    height = 600,
    autosize = True,
    legend = dict(
        orientation = "h",
        yanchor = "bottom",
        y = -0.3,
        xanchor = "center",
        x = 0.5
    ),
    updatemenus = [
        dict(
            type = "buttons",
            direction = "right",
            x = 0.05,
            y = 0.95,
            xanchor = "left",
            yanchor = "top",
            buttons = list([
                dict(
                    args = [{"visible": [True, False]}],
                    label = "Show districts",
                    method = "update"
                ),
                dict(
                    args = [{"visible": [False, True]}],
                    label = "Show crimes",
                    method = "update"
                )
            ])
        )
    ],
    margin = dict(r = 0, t = 40, l = 0, b = 40)
)
fig.write_html("figures/map.html", include_plotlyjs='cdn')
