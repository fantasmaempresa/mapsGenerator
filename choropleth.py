import csv
import json
import geopandas
import shapefile
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

mapbox_access_token = 'pk.eyJ1IjoiZXJpY2tuYXZlIiwiYSI6ImNrdDh3MnppbzE2NXIydm5ybWtkNjM5Y3UifQ.4bfoMQc-wQkbI7f2YQRhUA'


def midPoint(x1, y1, x2, y2):
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def getCenterCoordinates(shape, coordinates):
    for element in shape:
        if coordinates[0] > element[0]:
            coordinates[0] = element[0]

        if coordinates[1] < element[0]:
            coordinates[1] = element[0]

        if coordinates[2] > element[1]:
            coordinates[2] = element[1]

        if coordinates[3] < element[1]:
            coordinates[3] = element[1]

    return coordinates


def addTrace(fig, lat, lon):
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        fillcolor="#C2BA98",
        line=dict(color="black", width=1),
        showlegend=False,
        lon=lon,
        lat=lat))

    return fig


def createMap():
    municipalityShp = geopandas.read_file("assets/Tabasco/mun.shp")
    municipalityShp.to_file('myJson.geojson', driver='GeoJSON')

    municipalityGeoJson = json.load(open('myJson.geojson'))
    df = pd.read_csv("CM2020-2021.csv")

    fig = px.choropleth(df, geojson=municipalityGeoJson, color="PT",
                        locations="CVE", featureidkey="properties.CVEGEO",
                        color_continuous_scale="PuRd",
                        title='D:'
                        )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 100, "t": 100, "l": 100, "b": 100})
    fig.show()
    fig.write_html("file.html")
    
    
def createSectionMap():
    municipalityShp = geopandas.read_file("assets/Tabasco/secc.shp")
    municipalityShp[(municipalityShp.entidad == 28) & (municipalityShp.distrito_f==6)].to_file('myJson.geojson', driver='GeoJSON')
    municipalityGeoJson = json.load(open('myJson.geojson'))
    df = pd.read_csv("section2020-2021.csv")

    fig = px.choropleth(df, geojson=municipalityGeoJson, color="PT",
                        locations="SECCION", featureidkey="properties.seccion",
                        color_continuous_scale="PuRd",
                        title='D:'
                        )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 100, "t": 100, "l": 100, "b": 100})
    fig.show()

def main():
    createSectionMap()


if __name__ == "__main__":
    main()
