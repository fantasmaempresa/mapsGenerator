import csv
import json
import geopandas
import shapefile
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

mapbox_access_token = 'pk.eyJ1IjoiZXJpY2tuYXZlIiwiYSI6ImNrdDh3MnppbzE2NXIydm5ybWtkNjM5Y3UifQ.4bfoMQc-wQkbI7f2YQRhUA'


def readFile(fileName):
    data = []
    aux = {}
    with open(fileName, encoding="UTF-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            aux = {}
            key = row
            for item in range(len(key)):
                aux[key[item]] = row[item]

            data.append(aux)

    return data


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
    # fig = go.Figure()

    # READING SHAPE FILES
    # municipalityShp = "assets/Tabasco/mun.shp"
    # municipalityShp = shapefile.Reader(municipalityShp, encoding="iso-8859-15")

    municipalityShp = geopandas.read_file("assets/Tabasco/mun.shp")
    municipalityShp.to_file('myJson.geojson', driver='GeoJSON')

    municipalityGeoJson = json.load(open('myJson.geojson'))
    df = pd.read_csv("Ejemplo.csv")

    fig = px.choropleth(df, geojson=municipalityGeoJson, color="cant",
                        locations="mun", featureidkey="properties.CVEGEO",
                        projection="mercator"
                        )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":100,"t":100,"l":100,"b":100})
    fig.show()


def main():
    createMap()


if __name__ == "__main__":
    main()
