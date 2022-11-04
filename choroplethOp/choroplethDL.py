from dash import Dash, html, dcc

import json
import geopandas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from choropleth import printRow, getWinner, politicalPartiesColors, generate_table


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

    db.drop('SECCION ELECTORAL', axis=1, inplace=True, errors='ignore')
    db.drop('DISTRITO F', axis=1, inplace=True, errors='ignore')
    db.drop('% PARTICIPACION CIUDADANA', axis=1, inplace=True, errors='ignore')

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
                                id="geo-map-loading-outer2",
                                children=[
                                    dcc.Loading(
                                        id="loading2",
                                        children=dcc.Graph(
                                            id="geo-map2",
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
