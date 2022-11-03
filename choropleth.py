from unidecode import unidecode
from ast import parse
from email.policy import default
from dash import Dash, html, dcc

import json
import argparse
import geopandas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

mapbox_access_token = 'pk.eyJ1IjoiZXJpY2tuYXZlIiwiYSI6ImNrdDh3MnppbzE2NXIydm5ybWtkNjM5Y3UifQ.4bfoMQc-wQkbI7f2YQRhUA'
politicalPartiesColors = {'PAN': '#00008B ',	'PRI': '#008000',	'PRD': '#FFD700',	'PVEM': '#00FF00',	'PT': '#B22222',
                          'MC': '#D2691E',	'MORENA': '#621132',	'PES': '#8B008B',	'RSP': '#8B0000',	'FPM': '#FF1493'}


def createMap():
    municipalityShp = geopandas.read_file("assets/Tabasco/mun.shp")
    municipalityShp.to_file('myJson.geojson', driver='GeoJSON')

    municipalityGeoJson = json.load(open('myJson.geojson'))
    df = pd.read_csv("CM2020-2021.csv")

    fig = px.choropleth(df, geojson=municipalityGeoJson, color="PT",
                        locations="CVE", featureidkey="properties.CVEGEO",
                        color_continuous_scale="PuRd",
                        title='Información Por Municipio'
                        )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 100, "t": 100, "l": 100, "b": 100})
    fig.show()
    fig.write_html("file.html")


def printRow(row):
    return (row['TOTAL DE VOTOS'] * 100) / row['LISTA NOMINAL']


def getWinner(row, politcParties):

    dictWinners = {}
    for key in politcParties:
        dictWinners[key] = row[key]

    return max(dictWinners, key=dictWinners.get)


def getMunicipality(row, df):
    value = row['SECCION ELECTORAL']
    query = df.query("`SECCION ELECTORAL` == @value")
    return query.iloc[0]['MUNICIPIO']


def replaceContent(row):
    try:
        row = row.str.normalize('NFKD').str.encode(
            'ascii', errors='ignore').str.decode('utf-8')
    except Exception as e:
        row

    return row


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


def createSectionMap(pathGeojson: str, pathData: str, queryString: str, keyToMap: str, locations: str, featureidKey: str, additionalData: str, queryDF: str):

    if additionalData == '':
        hoverData = []
    else:
        hoverData = additionalData.split(',')

    municipalityShp = geopandas.read_file(pathGeojson)
    if queryString != "":
        municipalityShp.query(queryString, inplace=True)
    municipalityShp.to_file('myJson.geojson', driver='GeoJSON')
    municipalityGeoJson = json.load(open('myJson.geojson'))

    df = pd.read_csv(pathData)
    if queryDF != "":
        df.query(queryDF, inplace=True)

    db = df.groupby(['SECCION ELECTORAL']).sum(
        numeric_only=True).T.T.reset_index()
    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)

    fig = px.choropleth(db, geojson=municipalityGeoJson, color=['PAN', 'PRI'],
                        locations=locations, featureidkey=featureidKey,
                        color_continuous_scale="PuRd",
                        hover_data=hoverData,
                        title='Información por sección'
                        )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 100, "t": 100, "l": 100, "b": 100})
    fig.write_html("file.html")
    fig.show()


def comparisonMap():
    municipalities = pd.read_csv("assets/Tabasco/municipios.csv")
    municipalityShp = geopandas.read_file('assets/Tabasco/secc.shp')

    municiplaitiesName = []
    municiplaitiesGeometry = []

    for index, row in municipalities.iterrows():
        municiplaitiesName.append(row['municipio'])
        municipality = row['clave']
        query = municipalityShp.query(
            "entidad == 27 & municipio == @municipality")
        municiplaitiesGeometry.append(query['geometry'].unary_union)

    data = {'municipio': municiplaitiesName,
            'geometry': municiplaitiesGeometry
            }

    df_marques = pd.DataFrame(data)
    municipalityGeoJson = geopandas.GeoDataFrame(df_marques, crs='epsg:4326')
    municipalityGeoJson.to_file('myJson.geojson', driver='GeoJSON')
    municipalityGeoJson = json.load(open('myJson.geojson', encoding="utf8"))

    df = pd.read_csv("mapas/2020-2021/csv/ayu_resumen_general.csv")

    db = df.groupby(['MUNICIPIO']).sum(
        numeric_only=True).T.T.reset_index()

    # db['MUNICIPIO'] = db.apply(lambda row: getMunicipality(row, df), axis=1)
    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)
    db['WINNER'] = db.apply(lambda row: getWinner(
        row, ['PAN', 'PT', 'PRD', 'PRI', 'MORENA']), axis=1)

    # fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color='MORENA',
    #                            locations='MUNICIPIO', featureidkey='properties.municipio',
    #                            color_continuous_scale="PuRd",
    #                            title='Información por sección', mapbox_style="carto-positron", zoom=9
    #                            )

    fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color="WINNER",
                               locations="MUNICIPIO", featureidkey="properties.municipio",
                               color_continuous_scale="PuRd",
                               mapbox_style="carto-positron", zoom=9)

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 100, "t": 100, "l": 100, "b": 100})
    fig.write_html("file.html")
    fig.show()


def choroplethDF(pathData: str, keyToMap: str):
    municipalityGeoJson = json.load(open('myJson.geojson', encoding="utf8"))
    df = pd.read_csv(pathData)

    db = df.groupby(['DISTRITO F']).sum(numeric_only=True).T.T.reset_index()
    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)

    fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color=keyToMap,
                               locations='DISTRITO F', featureidkey="properties.distrito_f",
                               color_continuous_scale="PuRd", mapbox_style="carto-positron",
                               zoom=7, height=800, center={
                                   'lat': 18.028157,
                                   'lon': -92.753621
                               }
                               )
    return fig


def comparisonDistF(politicalPartiesArr, pathData: str):
    municipalityShp = geopandas.read_file('assets/Tabasco/secc.shp')

    municiplaitiesName = []
    municiplaitiesGeometry = []

    for row in range(6):
        municiplaitiesName.append(row + 1)
        municipality = row + 1
        query = municipalityShp.query(
            "entidad == 27 & distrito_f == @municipality")
        municiplaitiesGeometry.append(query['geometry'].unary_union)

    data = {'distrito_f': municiplaitiesName,
            'geometry': municiplaitiesGeometry
            }

    df_marques = pd.DataFrame(data)
    municipalityGeoJson = geopandas.GeoDataFrame(df_marques, crs='epsg:4326')
    municipalityGeoJson.to_file('myJson.geojson', driver='GeoJSON')
    municipalityGeoJson = json.load(open('myJson.geojson', encoding="utf8"))

    df = pd.read_csv(pathData)

    db = df.groupby(['DISTRITO F']).sum(
        numeric_only=True).T.T.reset_index()

    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)
    db['WINNER'] = db.apply(lambda row: getWinner(
        row, politicalPartiesArr), axis=1)

    fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color="WINNER",
                               locations="DISTRITO F", featureidkey="properties.distrito_f",
                               color_discrete_map=politicalPartiesColors,
                               mapbox_style="carto-positron", zoom=7, height=800, center={
                                   'lat': 18.028157,
                                   'lon': -92.753621
                               })

    # fig.update_geos(fitbounds="locations", visible=False)
    # fig.update_layout(margin={"r": 100, "t": 100, "l": 100, "b": 100})
    # fig.write_html("file.html")
    # fig.show()

    return fig


def pageDF(politicalParties: str, pathData: str, keyToMap: str):
    app = Dash(__name__)
    df = pd.read_csv(pathData)

    db = df.groupby(['DISTRITO F']).sum(
        numeric_only=True).T.T.reset_index()

    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)

    db.drop('SECCION ELECTORAL', axis=1, inplace=True)
    db.drop('DISTRITO L', axis=1, inplace=True)

    politicalPartiesArr = politicalParties.split(',')

    votes = []
    district = []
    parties = []

    for index, row in db.iterrows():
        for item in politicalPartiesArr:
            district.append(row['DISTRITO F'])
            votes.append(row[item])
            parties.append(item)

    finalData = pd.DataFrame({
        "Partido": parties,
        "Distrito Federal": district,
        "Votos": votes
    })

    fig = px.bar(finalData, x="Distrito Federal", y="Votos",
                 color="Partido", barmode="group",
                 color_discrete_map=politicalPartiesColors, height=700)

    app.layout = html.Div(
        children=[
            html.Div(
                id="banner",
                className="banner",
                children=[
                    html.H2("Análisis por Distritos Federales"),
                ],
            ),
            html.Div(
                id="upper-container",
                className="row",
                children=[
                    html.Div(
                        id="geo-map-outer",
                        children=[
                            html.Div(
                                id="geo-map-loading-outer",
                                children=[
                                    dcc.Loading(
                                        id="loading",
                                        children=dcc.Graph(
                                            id="geo-map",
                                            figure=comparisonDistF(
                                                politicalPartiesArr, pathData),
                                        ),
                                    )
                                ],
                            ),
                            html.Div(
                                id="geo-map-loading-outer",
                                children=[
                                    dcc.Loading(
                                        id="loading",
                                        children=dcc.Graph(
                                            id="geo-map",
                                            figure=choroplethDF(
                                                pathData, keyToMap),
                                        ),
                                    )
                                ],
                            ),
                            dcc.Graph(
                                id='example-graph',
                                figure=fig
                            ),
                            generate_table(db, len(db.index))
                        ],
                    ),
                ],
            ),
        ],
    )

    app.run_server(debug=True)


def choroplethDL(pathData: str, keyToMap: str):
    municipalityGeoJson = json.load(open('myJson.geojson', encoding="utf8"))
    df = pd.read_csv(pathData)

    db = df.groupby(['DISTRITO L']).sum(numeric_only=True).T.T.reset_index()
    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)

    fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color=keyToMap,
                               locations='DISTRITO L', featureidkey="properties.distrito_l",
                               color_continuous_scale="PuRd", mapbox_style="carto-positron",
                               zoom=7, height=800, center={
                                   'lat': 18.028157,
                                   'lon': -92.753621
                               }
                               )
    return fig


def comparisonDistL(politicalPartiesArr, pathData: str):
    municipalityShp = geopandas.read_file('assets/Tabasco/secc.shp')

    municiplaitiesName = []
    municiplaitiesGeometry = []

    for row in range(21):
        municiplaitiesName.append(row + 1)
        municipality = row + 1
        query = municipalityShp.query(
            "entidad == 27 & distrito_l == @municipality")
        municiplaitiesGeometry.append(query['geometry'].unary_union)

    data = {'distrito_l': municiplaitiesName,
            'geometry': municiplaitiesGeometry
            }

    df_marques = pd.DataFrame(data)
    municipalityGeoJson = geopandas.GeoDataFrame(df_marques, crs='epsg:4326')
    municipalityGeoJson.to_file('myJson.geojson', driver='GeoJSON')
    municipalityGeoJson = json.load(open('myJson.geojson', encoding="utf8"))

    df = pd.read_csv(pathData)

    db = df.groupby(['DISTRITO L']).sum(
        numeric_only=True).T.T.reset_index()

    # db['MUNICIPIO'] = db.apply(lambda row: getMunicipality(row, df), axis=1)
    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)
    db['WINNER'] = db.apply(lambda row: getWinner(
        row, politicalPartiesArr), axis=1)

    fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color="WINNER",
                               locations="DISTRITO L", featureidkey="properties.distrito_l",
                               color_discrete_map=politicalPartiesColors,
                               mapbox_style="carto-positron", zoom=7, height=800, center={
                                   'lat': 18.028157,
                                   'lon': -92.753621
                               })

    # fig.update_geos(fitbounds="locations", visible=False)
    # fig.write_html("file.html")
    # fig.show()

    return fig


def pageDL(politicalParties: str, pathData: str, keyToMap: str):
    app = Dash(__name__)
    df = pd.read_csv(pathData)

    db = df.groupby(['DISTRITO L']).sum(
        numeric_only=True).T.T.reset_index()

    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)

    db.drop('SECCION ELECTORAL', axis=1, inplace=True)
    db.drop('DISTRITO F', axis=1, inplace=True)

    politicalPartiesArr = politicalParties.split(',')

    votes = []
    district = []
    parties = []

    for index, row in db.iterrows():
        for item in politicalPartiesArr:
            district.append(row['DISTRITO L'])
            votes.append(row[item])
            parties.append(item)

    finalData = pd.DataFrame({
        "Partido": parties,
        "Distrito Local": district,
        "Votos": votes
    })

    fig = px.bar(finalData, x="Distrito Local", y="Votos",
                 color="Partido", barmode="group",
                 color_discrete_map=politicalPartiesColors, height=700)

    app.layout = html.Div(
        children=[
            html.Div(
                id="banner",
                className="banner",
                children=[
                    html.H2("Análisis por Distritos Locales"),
                ],
            ),
            html.Div(
                id="upper-container",
                className="row",
                children=[
                    html.Div(
                        id="geo-map-outer",
                        children=[
                            html.Div(
                                id="geo-map-loading-outer",
                                children=[
                                    dcc.Loading(
                                        id="loading",
                                        children=dcc.Graph(
                                            id="geo-map",
                                            figure=comparisonDistL(
                                                politicalPartiesArr, pathData),
                                        ),
                                    )
                                ],
                            ),
                            html.Div(
                                id="geo-map-loading-outer",
                                children=[
                                    dcc.Loading(
                                        id="loading",
                                        children=dcc.Graph(
                                            id="geo-map",
                                            figure=choroplethDL(
                                                pathData, keyToMap),
                                        ),
                                    )
                                ],
                            ),
                            dcc.Graph(
                                id='example-graph',
                                figure=fig
                            ),
                            generate_table(db, len(db.index))
                        ],
                    ),
                ],
            ),
        ],
    )

    app.run_server(debug=True)


def main():
    parser = argparse.ArgumentParser(description="Render maps of votes")
    parser.add_argument("--pathGeojson", type=str,
                        default="assets/Tabasco/mun.shp")
    parser.add_argument("--pathData", type=str, default='CM2020-2021.csv')
    parser.add_argument("--keyToMap", type=str, required=True)
    parser.add_argument("--locations", type=str, default="CVE")
    parser.add_argument("--featureidKey", type=str,
                        default="properties.CVEGEO")
    parser.add_argument("--query", type=str, default="")
    parser.add_argument("--queryDF", type=str, default="")
    parser.add_argument("--additionalData", type=str, default="")

    arguments = parser.parse_args()
    createSectionMap(arguments.pathGeojson, arguments.pathData, arguments.query,
                     arguments.keyToMap, arguments.locations, arguments.featureidKey, arguments.additionalData, arguments.queryDF)


if __name__ == "__main__":
    # pageDL("PAN,PRI,PRD", "mapas/2020-2021/csv/ayu_resumen_general.csv", "MORENA")
    pageDF("PAN,PRI,PRD,MORENA", "mapas/2020-2021/csv/ayu_resumen_general.csv", "MORENA")
