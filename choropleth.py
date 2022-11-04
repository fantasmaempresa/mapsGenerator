from unidecode import unidecode
from ast import parse
from email.policy import default
from dash import Dash, html, dcc

import sys
import json
import argparse
import geopandas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

mapbox_access_token = 'pk.eyJ1IjoiZXJpY2tuYXZlIiwiYSI6ImNrdDh3MnppbzE2NXIydm5ybWtkNjM5Y3UifQ.4bfoMQc-wQkbI7f2YQRhUA'
politicalPartiesColors = {'PAN': '#00008B ',	'PRI': '#008000',	'PRD': '#FFD700',	'PVEM': '#00FF00',	'PT': '#B22222',
                          'MC': '#D2691E',	'MORENA': '#621132',	'PES': '#8B008B',	'RSP': '#8B0000',	'FPM': '#FF1493', 'NVA_ALIANZA': '#28BBFD'}


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