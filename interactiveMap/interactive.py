import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import Dash, html, dcc, Input, Output, dash_table

from interactiveMap.paintMap import paintMap
from interactiveMap.createGeoJson import *
from interactiveMap.createData import createDataToMap, createDataToTable

app = Dash(external_stylesheets=[dbc.themes.SOLAR])
pathShp = 'assets/Tabasco/secc.shp'
pathMun = 'assets/Tabasco/municipios.csv'
pathData = ''
originData = pd.DataFrame({
    "year": ['2017-2018', '2017-2018', '2017-2018', '2020-2021', '2020-2021'],
    "type": ['Ayuntamiento', 'Diputados', 'Gobernatura', 'Ayuntamiento', 'Diputados'],
    "file": ['ayu_general_casillas.csv', 'dip_resumen_general.csv', 'gub_resumen_general.csv', 'ayu_resumen_general.csv', 'dip_resumen_general.csv']
})

dataBase = pd.DataFrame()


@app.callback(
    Output('candidance_type', 'options'),
    Output('candidance_type', 'value'),
    Input('year', 'value')
)
def filterByYearData(year: str):
    return originData.query('year == @year')['type'], ''


@app.callback(
    Output('political_parties', 'options'),
    Output('political_parties', 'value'),
    Output('query_type', 'value'),
    Output('political_parties_range', 'options'),
    Output('political_parties_range', 'value'),
    Input('year', 'value'),
    Input('candidance_type', 'value'),
)
def getPoliticPartiesByFile(year: str, candidance_type: str):
    global pathData
    if candidance_type != '' and candidance_type != None:
        file = originData.query(
            'year == @year and type == @candidance_type')['file'].iloc[0]

        pathData = 'mapas/' + year + '/csv/' + file

        data = pd.read_csv(pathData)

        keys = list(data.keys())
        keys.remove('SECCION ELECTORAL')
        keys.remove('MUNICIPIO')
        keys.remove('NUMERO DE VOTOS VALIDOS')
        keys.remove('NUMERO DE VOTOS NULOS')
        keys.remove('TOTAL DE VOTOS')
        keys.remove('LISTA NOMINAL')
        keys.remove('% PARTICIPACION CIUDADANA')
        keys.remove('DISTRITO F')
        keys.remove('DISTRITO L')

        try:
            keys.remove('CASILLA')
        except ValueError:
            pass

        try:
            keys.remove('NUMERO DE VOTOS CANDIDATURAS NO REGISTRADAS')
        except ValueError:
            pass

        return [{"label": i, "value": i} for i in keys], keys[0:1], '', [{"label": i, "value": i} for i in keys], keys[0]

    pathData = ''
    return [], [], '', [], ''


@app.callback(
    Output('comparision_map', 'figure'),
    Input('political_parties', 'value'),
    Input('query_type', 'value'),
)
def createComparisionMap(political_parties, query_type: str):
    fig = px.choropleth_mapbox()

    if political_parties and query_type != '' and query_type != None:
        if query_type == 'Municipio':
            db = createDataToMap(pathData, political_parties, "MUNICIPIO")
            fig = paintMap(db, munGeoJson, "MUNICIPIO",
                           "GANADOR", "properties.municipio")

        elif query_type == 'Distrito Local':
            db = createDataToMap(pathData, political_parties, "DISTRITO L")
            fig = paintMap(db, dLGeoJson, "DISTRITO L",
                           "GANADOR", "properties.district")

        elif query_type == 'Distrito Federal':
            db = createDataToMap(pathData, political_parties, "DISTRITO F")
            fig = paintMap(db, dFGeoJson, "DISTRITO F",
                           "GANADOR", "properties.district")

        elif query_type == 'Secciones':
            db = createDataToMap(
                pathData, political_parties, "SECCION ELECTORAL")
            fig = paintMap(db, seccGeoJson, "SECCION ELECTORAL",
                           "GANADOR", "properties.seccion")

    return fig


@app.callback(
    Output('range_map', 'figure'),
    Input('political_parties_range', 'value'),
    Input('query_type', 'value'),
)
def createRangeMap(politicalParty, queryType):
    fig = px.choropleth_mapbox()

    if politicalParty != '' and queryType != '' and queryType != None:
        if queryType == 'Municipio':
            db = createDataToMap(pathData, [politicalParty], "MUNICIPIO")
            fig = paintMap(db, munGeoJson, "MUNICIPIO",
                           politicalParty, "properties.municipio")

        elif queryType == 'Distrito Local':
            db = createDataToMap(pathData, [politicalParty], "DISTRITO L")
            fig = paintMap(db, dLGeoJson, "DISTRITO L",
                           politicalParty, "properties.district")

        elif queryType == 'Distrito Federal':
            db = createDataToMap(pathData, [politicalParty], "DISTRITO F")
            fig = paintMap(db, dFGeoJson, "DISTRITO F",
                           politicalParty, "properties.district")

        elif queryType == 'Secciones':
            db = createDataToMap(
                pathData, [politicalParty], "SECCION ELECTORAL")
            fig = paintMap(db, seccGeoJson, "SECCION ELECTORAL",
                           politicalParty, "properties.seccion")

    return fig


@app.callback([
    Output('table1', 'data'),
    Output('table1', 'columns'),
    Input('query_type', 'value')
])
def createTable(query_type: str):
    db = pd.DataFrame()

    if query_type != '':
        if query_type == 'Municipio':
            db = createDataToTable(pathData, "MUNICIPIO")

        elif query_type == 'Distrito Local':
            db = createDataToTable(pathData, "DISTRITO L")

        elif query_type == 'Distrito Federal':
            db = createDataToTable(pathData, "DISTRITO F")

        elif query_type == 'Secciones':
            db = createDataToTable(
                pathData,  "SECCION ELECTORAL")

    return db.to_dict('records'), [{"name": i, "id": i} for i in db.columns]


def interactive():
    createAllGeoJson(pathMun, pathShp)

    app.layout = html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.P("Año de Consulta"),
                            dcc.Dropdown(
                                originData['year'].unique(),
                                '0',
                                id='year'
                            )])
                    ]),
                    dbc.Col([
                        html.Div([
                            html.P("Tipo Candidatura"),
                            dcc.Dropdown(
                                id='candidance_type',
                                value=''
                            )
                        ])
                    ]),
                    dbc.Col([
                        html.Div([
                            html.P("Tipo Consulta"),
                            dcc.Dropdown(
                                ['Distrito Local', 'Distrito Federal',
                                 'Municipio', 'Secciones'],
                                id='query_type',
                                value=''
                            )
                        ])
                    ]),
                ], align='center')
            ]),
            style={'margin': '30px'}
        ),
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Checklist(id='political_parties', inline=True),
                    dcc.Loading(dcc.Graph(id='comparision_map'))
                ])
            ]),
            style={'margin': '30px'}
        ),
        dbc.Card(
            dbc.CardBody(
                dcc.Loading(dash_table.DataTable(
                    id='table1', page_size=21, style_table={'overflowX': 'auto'}))
            ),
            style={'margin': '30px'}
        ),
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.RadioItems(id='political_parties_range', inline=True),
                    dcc.Loading(dcc.Graph(id='range_map'))
                ])
            ]),
            style={'margin': '30px'}
        )
    ])

    app.run_server(debug=True)
