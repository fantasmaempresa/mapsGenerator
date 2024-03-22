import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import Dash, html, dcc, Input, Output, dash_table
from dash.dash_table.Format import Format, Scheme, Sign

from interactiveMap.paintMap import *
from interactiveMap.createGeoJson import *
from interactiveMap.createData import *

app = Dash(external_stylesheets=[dbc.themes.SOLAR])
pathShp = 'assets/Puebla/SHP/SECCION.shp'

pathData = ''
type = ''

originData = pd.DataFrame({
    "year": ['2011','2011','2011','2013','2013','2019','2021','2021'],
    "type": ['Gobernatura','Diputados','Ayuntamiento','Diputados','Ayuntamiento','Gobernatura','Diputados','Presidencia'],
    "file": ['gobernatura.csv','diputados.csv','ayuntamiento.csv','diputados.csv','ayuntamiento.csv','gub_ext_2019.csv','dip_2021.csv', 'presi_2021.csv']
})

dataBase = pd.DataFrame()


@app.callback(
    Output('candidance_type', 'options'),
    Output('candidance_type', 'value'),
    Input('year', 'value')
)
def filterByYearData(year: str):
    return [{"label": i, "value": i} for i in originData.query('year == @year')['type']], ''


@app.callback(
    Output('political_parties', 'options'),
    Output('political_parties', 'value'),
    Output('query_type', 'value'),
    Output('political_parties_range', 'options'),
    Output('political_parties_range', 'value'),
    Output('political_parties_bar', 'options'),
    Output('political_parties_bar', 'value'),
    Output('political_parties_g1', 'options'),
    Output('political_parties_g1', 'value'),
    Output('political_parties_g2', 'options'),
    Output('political_parties_g2', 'value'),
    Input('year', 'value'),
    Input('candidance_type', 'value'),
)
def getPoliticPartiesByFile(year: str, candidance_type: str):
    global pathData
    if candidance_type != '' and candidance_type != None:
        file = originData.query(
            'year == @year and type == @candidance_type')['file'].iloc[0]

        pathDB = 'mapas/' + year + '/csv/' + file

        data = pd.read_csv(pathDB)
        if type != 'GENERAL':
            data.query('MUNICIPIO == @type', inplace=True)
        
        pathData = 'mapas/DB.csv'
        data.to_csv(pathData, index=False)

        keys = list(data.keys())
        keys.remove('SECCION ELECTORAL')
        keys.remove('MUNICIPIO')
        keys.remove('TOTAL DE VOTOS')
        keys.remove('LISTA NOMINAL')
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

        if not keys:
            keys.append('A')

        ppDict = [{"label": i, "value": i} for i in keys]

        return ppDict, keys[0:1], '', ppDict, keys[0], ppDict, keys[0:1], keys, keys[0:1], keys, keys[0:1]

    pathData = ''
    return [], [], '', [], '', [], '', [], '', [], ''


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
                           "GANADOR", "properties.SECCION")

    fig.update_layout(mapbox_style="carto-positron")
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
                           politicalParty, "properties.SECCION")

    fig.update_layout(mapbox_style="carto-positron")
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

    return db.to_dict('records'), [{"name": i, "id": i, "type": 'numeric', 'format': Format().group(True)} for i in db.columns]


@app.callback([
    Output('table2', 'data'),
    Output('table2', 'columns'),
    Input('query_type', 'value')
])
def createTable2(query_type: str):
    db = pd.DataFrame()

    if query_type != '':
        if query_type == 'Municipio':
            db = createDataTableRG(pathData, "MUNICIPIO")

        elif query_type == 'Distrito Local':
            db = createDataTableRG(pathData, "DISTRITO L")

        elif query_type == 'Distrito Federal':
            db = createDataTableRG(pathData, "DISTRITO F")

        elif query_type == 'Secciones':
            db = createDataTableRG(
                pathData,  "SECCION ELECTORAL")

    return db.to_dict('records'), [{"name": i, "id": i, "type": 'numeric', 'format': Format().group(True)} for i in db.columns]


@app.callback(
    Output('bar', 'figure'),
    Input('political_parties_bar', 'value'),
    Input('query_type', 'value'),
)
def createGrafic(politicalParties, queryType: str):
    fig = px.bar()

    if politicalParties and queryType != '' and queryType != None:
        if queryType == 'Municipio':
            db = createDataToMap(pathData, politicalParties, "MUNICIPIO")
            fig = createGraphicBar(db, politicalParties, "MUNICIPIO")

        elif queryType == 'Distrito Local':
            db = createDataToMap(pathData, politicalParties, "DISTRITO L")
            fig = createGraphicBar(db, politicalParties, "DISTRITO L")

        elif queryType == 'Distrito Federal':
            db = createDataToMap(pathData, politicalParties, "DISTRITO F")
            fig = createGraphicBar(db, politicalParties, "DISTRITO F")

        elif queryType == 'Secciones':
            db = createDataToMap(
                pathData, politicalParties, "SECCION ELECTORAL")
            fig = createGraphicBar(db, politicalParties, "SECCION ELECTORAL")

    return fig


@app.callback(
    Output('versus_map', 'figure'),
    Output('table3', 'data'),
    Output('table3', 'columns'),
    Input('political_parties_g1', 'value'),
    Input('political_parties_g2', 'value'),
    Input('query_type', 'value'),
)
def createMapVs(politicalPartiesG1, politicalPartiesG2, queryType):
    fig = px.choropleth_mapbox()
    db = pd.DataFrame()

    if politicalPartiesG1 and politicalPartiesG2 and queryType != '' and queryType != None:

        if queryType == 'Municipio':
            db = createDataToVS(
                pathData, politicalPartiesG1, politicalPartiesG2, "MUNICIPIO")
            fig = paintMap(db, munGeoJson, "MUNICIPIO",
                           "GANADOR", "properties.municipio")

        elif queryType == 'Distrito Local':
            db = createDataToVS(pathData, politicalPartiesG1,
                                politicalPartiesG2, "DISTRITO L")
            fig = paintMap(db, dLGeoJson, "DISTRITO L",
                           "GANADOR", "properties.district")

        elif queryType == 'Distrito Federal':
            db = createDataToVS(pathData, politicalPartiesG1,
                                politicalPartiesG2, "DISTRITO F")
            fig = paintMap(db, dFGeoJson, "DISTRITO F",
                           "GANADOR", "properties.district")

        elif queryType == 'Secciones':
            db = createDataToVS(pathData, politicalPartiesG1,
                                politicalPartiesG2, "SECCION ELECTORAL")
            fig = paintMap(db, seccGeoJson, "SECCION ELECTORAL",
                           "GANADOR", "properties.SECCION")

    fig.update_layout(mapbox_style="carto-positron")
    return fig, db.to_dict('records'), [{"name": i, "id": i, "type": 'numeric', 'format': Format().group(True)} for i in db.columns]


@app.callback([
    Output('table4', 'data'),
    Output('table4', 'columns'),
    Output('priority_map', 'figure'),
    Input('query_type', 'value')
])
def createTable4(query_type: str):
    db = pd.DataFrame()
    fig = px.choropleth_mapbox()

    if query_type != '':
        if query_type == 'Municipio':
            db = createDataClassification(pathData, "MUNICIPIO")
            fig = priorityMap(db, munGeoJson, "MUNICIPIO",
                              "PRIORIDAD", "properties.municipio")

        elif query_type == 'Distrito Local':
            db = createDataClassification(pathData, "DISTRITO L")
            fig = priorityMap(db, dLGeoJson, "DISTRITO L",
                              "PRIORIDAD", "properties.district")

        elif query_type == 'Distrito Federal':
            db = createDataClassification(pathData, "DISTRITO F")
            fig = priorityMap(db, dFGeoJson, "DISTRITO F",
                              "PRIORIDAD", "properties.district")

        elif query_type == 'Secciones':
            db = createDataClassification(pathData,  "SECCION ELECTORAL")
            fig = priorityMap(db, seccGeoJson, "SECCION ELECTORAL",
                              "PRIORIDAD", "properties.SECCION")
        elif query_type == 'Junta Auxiliar':
            db = createDataClassification(pathData,  "JA")
            fig = priorityMap(db, jaGeoJson, "JA",
                              "PRIORIDAD", "properties.junta_auxiliar")

    fig.update_layout(mapbox_style="carto-positron")
    return db.to_dict('records'), [{"name": i, "id": i, "type": 'numeric', 'format': Format().group(True)} for i in db.columns], fig


@app.callback([
    Output('div-principal', 'style'),
    Output('div-consulta', 'style'),
    Output('div-special-map', 'style'),
    Input('year', 'value'),
    Input('candidance_type', 'value'),
])
def showHideElements(year: str, candidance_type: str):
    if candidance_type != '' and candidance_type != None:
        file = originData.query(
            'year == @year and type == @candidance_type')['file'].iloc[0]

        pathData = 'mapas/' + year + '/csv/' + file

        data = pd.read_csv(pathData)

        keys = list(data.keys())

        index = keys.index('EXTRA DATA') if 'EXTRA DATA' in keys else -1

        if index == -1:
            return {'display': 'block'}, {'display': 'block'}, {'display': 'none'}
        else:
            return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'block'}, {'display': 'block'}, {'display': 'none'}


@app.callback(
    Output('map_special', 'figure'),
    Input('candidance_type', 'value'),
)
def mapSpecialCase(candidance_type: str):
    fig = px.choropleth_mapbox()

    if pathData != '':
        db = pd.read_csv(pathData)
        keys = list(db.keys())

        index = keys.index('EXTRA DATA') if 'EXTRA DATA' in keys else -1

        if index != -1:
            fig = paintMap(db, seccGeoJson, "SECCION ELECTORAL",
                           "EXTRA DATA", "properties.SECCION")

    fig.update_layout(mapbox_style="carto-positron")
    return fig


def interactive(mapType):
    global type
    type = createAllGeoJson(pathShp, mapType)
    # type = "PUEBLA"
    app.layout = html.Div([
        html.H2(children=type),
        dbc.Card(
            dbc.CardBody([
                html.H2(children='Filtros'),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dbc.Label("Año de Consulta"),
                            dbc.Select(
                                id='year',
                                options=[{"label": i, "value": i}
                                         for i in originData['year'].unique()],
                            )])
                    ]),
                    dbc.Col([
                        html.Div([
                            dbc.Label("Tipo Candidatura"),
                            dbc.Select(
                                id='candidance_type',
                                value=''
                            )
                        ])
                    ]),
                    dbc.Col([
                        html.Div([
                            dbc.Label("Tipo Consulta"),
                            dbc.Select(
                                id='query_type',
                                options=[
                                    {"label": "Distrito Local", "value": "Distrito Local"},
                                    {"label": "Distrito Federal", "value": "Distrito Federal"},
                                    {"label": "Junta Auxiliar", "value": "Junta Auxiliar"},
                                    {"label": "Municipio", "value": "Municipio"},
                                    {"label": "Secciones", "value": "Secciones"}]
                            )
                        ], id="div-consulta")
                    ]),
                ], align='center')
            ]),
            style={'margin': '30px'}
        ),
        html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.H2(children='Comparación por Partido Político'),
                    dbc.Row([
                        dbc.Checklist(id='political_parties', inline=True),
                        dcc.Loading(dcc.Graph(id='comparision_map'))
                    ])
                ]),
                style={'margin': '30px'}
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H2(children='Tabla General'),
                        dcc.Loading(dash_table.DataTable(
                            id='table1', page_size=22, style_table={'overflowX': 'auto'}, style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(220, 220, 220)',
                                }
                            ], style_data={
                                'color': 'black',
                                'fontWeight': 'bold'
                            }, style_header={
                                'color': 'black',
                                'fontWeight': 'bold'
                            }))
                    ]
                ),
                style={'margin': '30px'}
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H2(children='Densidad de Votación por Partido Político'),
                    dbc.Row([
                        dbc.RadioItems(
                            id='political_parties_range', inline=True),
                        dcc.Loading(dcc.Graph(id='range_map'))
                    ])
                ]),
                style={'margin': '30px'}
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H2(children='Gráfica de Votación por Partido Político'),
                    dbc.Row([
                        dbc.Checklist(id='political_parties_bar', inline=True),
                        dcc.Loading(dcc.Graph(id='bar'))
                    ])
                ]),
                style={'margin': '30px'}
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H2(children='Casillas'),
                    dcc.Loading(dash_table.DataTable(
                        id='table2', page_size=22, style_table={'overflowX': 'auto'}, style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(220, 220, 220)',
                            }
                        ], style_data={
                            'color': 'black',
                            'fontWeight': 'bold'
                        }, style_header={
                            'color': 'black',
                            'fontWeight': 'bold'}
                    ))
                ]),
                style={'margin': '30px'}
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H2(children='Escenario Político'),
                    dbc.Row([
                        dbc.Col(html.Div([
                            dbc.Label("Grupo 1"),
                            dcc.Dropdown(id='political_parties_g1', multi=True)
                        ])),
                        dbc.Col(html.Div([
                            dbc.Label("Grupo 2"),
                            dcc.Dropdown(id='political_parties_g2', multi=True)
                        ])),
                        dcc.Loading(dcc.Graph(id='versus_map',
                                              style={'margin': '20px'})),
                        dcc.Loading(dash_table.DataTable(
                            id='table3', page_size=22, style_table={'overflowX': 'auto'}, style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(220, 220, 220)',
                                }
                            ], style_data={
                                'color': 'black',
                                'fontWeight': 'bold'
                            }, style_header={
                                'color': 'black',
                                'fontWeight': 'bold'}))
                    ], align='center')
                ]),
                style={'margin': '30px'}
            ),
            dbc.Card(
                dbc.CardBody([html.H2(children='Prioridad'),
                              dbc.Row([
                                  dcc.Loading(dash_table.DataTable(
                                      id='table4', page_size=22, style_table={'overflowX': 'auto'}, style_data_conditional=[
                                          {
                                              'if': {'row_index': 'odd'},
                                              'backgroundColor': 'rgb(220, 220, 220)',
                                          }
                                      ], style_data={
                                          'color': 'black',
                                          'fontWeight': 'bold'
                                      }, style_header={
                                          'color': 'black',
                                          'fontWeight': 'bold'})),
                                  dcc.Loading(dcc.Graph(id='priority_map',
                                                        style={'margin': '20px'})),

                              ])]),
                style={'margin': '30px'}
            ),
        ], id='div-principal'),
        html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.H2(children='Prioridad'),
                    dbc.Row([
                        dcc.Loading(dcc.Graph(id='map_special'))
                    ])
                ]),
                style={'margin': '30px'}
            )
        ], id='div-special-map'),
    ])

    app.run_server(debug=True)
