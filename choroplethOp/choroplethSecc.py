from dash import Dash, html, dcc

import json
import geopandas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from choropleth import *


def choroplethSecc(pathData: str, keyToMap: str, municipality: int):
    municipalityGeoJson = json.load(open('myJson.geojson', encoding="utf8"))
    municipalities = pd.read_csv("assets/Tabasco/municipios.csv")
    df = pd.read_csv(pathData)

    if municipality != 0:
        municipalities.query('clave == @municipality', inplace=True)
        value = municipalities.iloc[0]['municipio']
        df.query('MUNICIPIO == @value', inplace=True)

    db = df.groupby(['SECCION ELECTORAL']).sum(numeric_only=True).T.T.reset_index()
    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)

    fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color=keyToMap,
                               locations='SECCION ELECTORAL', featureidkey="properties.seccion",
                               color_continuous_scale="PuRd", mapbox_style="carto-positron",
                               zoom=7, height=800, center={
                                   'lat': 18.028157,
                                   'lon': -92.753621
                               }
                               )
    return fig


def comparisonSecc(politicalPartiesArr, pathData: str, municipality: int):
    df = pd.read_csv(pathData)
    municipalities = pd.read_csv("assets/Tabasco/municipios.csv")
    municipalityGeoJson = geopandas.read_file('assets/Tabasco/secc.shp')
    
    municipalityGeoJson.query("entidad == 27", inplace=True)
    
    if municipality != 0:
        municipalityGeoJson.query('municipio == @municipality', inplace=True)
        municipalities.query('clave == @municipality', inplace=True)
        value = municipalities.iloc[0]['municipio']
        df.query('MUNICIPIO == @value', inplace=True)
    
    municipalityGeoJson.to_file('myJson.geojson', driver='GeoJSON')
    municipalityGeoJson = json.load(open('myJson.geojson', encoding="utf8"))

    
    db = df.groupby(['SECCION ELECTORAL']).sum(
        numeric_only=True).T.T.reset_index()

    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)
    db['WINNER'] = db.apply(lambda row: getWinner(
        row, politicalPartiesArr), axis=1)

    fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color="WINNER",
                               locations="SECCION ELECTORAL", featureidkey="properties.seccion",
                               color_continuous_scale="PuRd",
                               color_discrete_map=politicalPartiesColors,
                               mapbox_style="carto-positron", zoom=7, height=800,
                               center={
                                   'lat': 18.028157,
                                   'lon': -92.753621
                               })

    return fig


def pageSecc(politicalParties: str, pathData: str, keyToMap: str, municipality: str):
    app = Dash(__name__)
    df = pd.read_csv(pathData)
    municipalities = pd.read_csv("assets/Tabasco/municipios.csv")
    title = "Análisis por Secciones"

    if municipality != 0:
        municipalities.query('clave == @municipality', inplace=True)
        value = municipalities.iloc[0]['municipio']
        title = title + " " + " Municipio: " + municipalities.iloc[0]['municipio']
        df.query('MUNICIPIO == @value', inplace=True)

    db = df.groupby(['SECCION ELECTORAL']).sum(
        numeric_only=True).T.T.reset_index()

    db['% PARTICIPACION'] = db.apply(lambda row: printRow(row), axis=1)

    db.drop('DISTRITO L', axis=1, inplace=True, errors='ignore')
    db.drop('DISTRITO F', axis=1, inplace=True, errors='ignore')
    db.drop('% PARTICIPACION CIUDADANA', axis=1, inplace=True, errors='ignore')

    politicalPartiesArr = politicalParties.split(',')

    app.layout = html.Div(
        children=[
            html.Div(
                id="banner",
                className="banner",
                children=[
                    html.H2(title),
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
                                            figure=comparisonSecc(
                                                politicalPartiesArr, pathData, municipality),
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
                                            figure=choroplethSecc(
                                                pathData, keyToMap, municipality),
                                        ),
                                    )
                                ],
                            ),
                            generate_table(db, len(db.index))
                        ],
                    ),
                ],
            ),
        ],
    )

    app.run_server(debug=True)
