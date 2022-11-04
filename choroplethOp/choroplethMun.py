from dash import Dash, html, dcc

import json
import geopandas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from choropleth import *

def choroplethMun(pathData: str, keyToMap: str):
    municipalityGeoJson = json.load(open('myJson.geojson', encoding="utf8"))
    df = pd.read_csv(pathData)

    db = df.groupby(['MUNICIPIO']).sum(numeric_only=True).T.T.reset_index()
    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)

    fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color=keyToMap,
                               locations='MUNICIPIO', featureidkey="properties.municipio",
                               color_continuous_scale="PuRd", mapbox_style="carto-positron",
                               zoom=7, height=800, center={
                                   'lat': 18.028157,
                                   'lon': -92.753621
                               }
                               )
    return fig

def comparisonMap(politicalPartiesArr, pathData: str):
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

    df = pd.read_csv(pathData)

    db = df.groupby(['MUNICIPIO']).sum(
        numeric_only=True).T.T.reset_index()

    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)
    db['WINNER'] = db.apply(lambda row: getWinner(
        row, politicalPartiesArr), axis=1)

    fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color="WINNER",
                               locations="MUNICIPIO", featureidkey="properties.municipio",
                               color_continuous_scale="PuRd",
                               color_discrete_map=politicalPartiesColors,
                               mapbox_style="carto-positron", zoom=7, height=800,
                               center={
                                   'lat': 18.028157,
                                   'lon': -92.753621
                               })
    
    return fig

def pageMun(politicalParties: str, pathData: str, keyToMap: str):
    app = Dash(__name__)
    df = pd.read_csv(pathData)

    db = df.groupby(['MUNICIPIO']).sum(
        numeric_only=True).T.T.reset_index()

    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)

    db.drop('SECCION ELECTORAL', axis=1, inplace=True, errors='ignore')
    db.drop('DISTRITO L', axis=1, inplace=True, errors='ignore')
    db.drop('DISTRITO F', axis=1, inplace=True, errors='ignore')
    db.drop('% PARTICIPACION CIUDADANA', axis=1, inplace=True, errors='ignore')
    
    politicalPartiesArr = politicalParties.split(',')

    votes = []
    district = []
    parties = []

    for index, row in db.iterrows():
        for item in politicalPartiesArr:
            district.append(row['MUNICIPIO'])
            votes.append(row[item])
            parties.append(item)

    finalData = pd.DataFrame({
        "Partido": parties,
        "Municipio": district,
        "Votos": votes
    })

    fig = px.bar(finalData, x="Municipio", y="Votos",
                 color="Partido", barmode="group",
                 color_discrete_map=politicalPartiesColors, height=700)

    app.layout = html.Div(
        children=[
            html.Div(
                id="banner",
                className="banner",
                children=[
                    html.H2("Análisis por Municipios"),
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
                                            figure=comparisonMap(
                                                politicalPartiesArr, pathData),
                                        ),
                                    )
                                ],
                            ),
                            html.Div(
                                id="geo-map-loading-outer 2",
                                children=[
                                    dcc.Loading(
                                        id="loading 2",
                                        children=dcc.Graph(
                                            id="geo-map 2",
                                            figure=choroplethMun(
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
