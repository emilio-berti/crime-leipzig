import plotly.express as px
import plotly.io as pio
from geopy.geocoders import Nominatim
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import json

def geolocate(d):
    place = d.place
    street = d.street
    geolocator = Nominatim(user_agent = "GetLoc")
    lat = [None for x in place]
    lon = [None for x in place]
    print(" - Geolocating...")
    for i in range(len(place)):
        print("   -", i + 1, "of", len(place))
        if (street[i] != street[i]): #street is nan
            coords = geolocator.geocode('Leipzig,' + place[i])  # use only place
        else:
            coords = geolocator.geocode('Leipzig, ' + street[i])  # only street is more accurate
        if coords is None:
            coords = geolocator.geocode('Leipzig,' + place[i])  # try only place
        if coords is None:
            lat[i] = None
            lon[i] = None
        else:
            lat[i] = coords[1][0]
            lon[i] = coords[1][1]

    # remove rows without location -----------
    empty = [i for i, x in enumerate(lat) if x is None]
    empty.reverse()
    print(" - Cannot find " +  str(len(empty)) + ":")
    for e in empty:        
        print("   - " + d['place'][e] + ', ' + str(d['street'][e]))
        lat.pop(e)
        lon.pop(e)
        d = d.drop(e)

    # add geo columns -----------
    d['lat'] = lat
    d['lon'] = lon
    return d

def shape(d, file = "data/crimes.shp", write = True):
    # create geodataframe --------
    geom = [Point(d.lon[i], d.lat[i]) for i in d.index]
    d['geometry'] = geom
    d = gpd.GeoDataFrame(d, crs = "EPSG:4326")
    s = [1 if x != x else 2 for x in d.street]
    d['size'] = s
    if write: d.to_file(file)
    return d

def map(geo):
    districts = gpd.read_file("data/ot.shp")
    districts = districts.to_crs(geo.crs)
    total_crimes = pd.DataFrame({
      'n': gpd.sjoin(districts, geo).groupby("OT").title.count()
    })
    m = districts.merge(total_crimes, on = "OT")

    px.set_mapbox_access_token(open(".mapbox_token").read())
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
        mapbox_style = "streets",
        color_continuous_scale = ["#584B9F", "#22C4B3", "#FEFDBE", "#F39B29", "#A71B4B"]
    )
    # fig = px.scatter_mapbox(
    #     geo,
    #     lat = geo.geometry.y,
    #     lon = geo.geometry.x,
    #     size = "size",
    #     opacity = 0.75,
    #     hover_name = "title",
    #     hover_data = ["title", "place", "street", "date"],
    #     zoom = 10,
    #     color = "title",
    #     mapbox_style = "streets"
    # )
    fig.write_html("figures/map.html")
    # pio.write_image(fig, "figures/map.pdf", format = "pdf")
    #fig.show()
