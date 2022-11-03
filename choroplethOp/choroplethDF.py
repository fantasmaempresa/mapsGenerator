from dash import Dash, html, dcc

import json
import geopandas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from choropleth import *


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
