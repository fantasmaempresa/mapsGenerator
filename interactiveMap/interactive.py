import pandas as pd
import plotly.express as px

from interactiveMap.createGeoJson import createAllGeoJson
from interactiveMap.createData import createDataMunicipalities
from interactiveMap.paintMap import paintMap
from dash import Dash, html, dcc, Input, Output

app = Dash(__name__)
pathShp = 'assets/Tabasco/secc.shp'
pathMun = 'assets/Tabasco/municipios.csv'
pathData = ''
originData = pd.DataFrame({
    "year": ['2017-2018', '2017-2018', '2017-2018', '2020-2021', '2020-2021'],
    "type": ['Ayuntamiento', 'Diputados', 'Gobernatura', 'Ayuntamiento', 'Diputados'],
    "file": ['ayu_general_casillas.csv', 'dip_resumen_general.csv', 'gub_resumen_general.csv', 'ayu_resumen_general.csv', 'dip_resumen_general.csv']
})


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
    Input('year', 'value'),
    Input('candidance_type', 'value'),
)
def getPoliticPartiesByFile(year: str, candidance_type: str):
    if candidance_type != '':
        file = originData.query(
            'year == @year and type == @candidance_type')['file'].iloc[0]

        global pathData
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

        return keys, keys[0:1]
    
    pathData = ''
    return [], []


@app.callback(
    Output('comparision_map', 'figure'),
    Input('political_parties', 'value'),
    Input('query_type', 'value'),
)
def createComparisionMap(political_parties: str, query_type: str):
    if query_type == 'Municipio':
        db = createDataMunicipalities(
            pathData=pathData, politicParties=political_parties)

        return paintMap(db)
    elif query_type == 'Distrito Local':
        print('Distrito Local')
    elif query_type == 'Distrito Federal':
        print('Distrito Federal')

    return px.choropleth_mapbox()


def interactive():
    createAllGeoJson(pathMun, pathShp)

    app.layout = html.Div([
        html.Div([
            html.Div([
                html.P("Año de Consulta"),
                dcc.Dropdown(
                    originData['year'].unique(),
                    '0',
                    id='year'
                )
            ], style={'width': '30%', 'display': 'inline-block'}),
            html.Div([
                html.P("Tipo Candidatura"),
                dcc.Dropdown(
                    id='candidance_type',
                    value=''
                ),
            ], style={'width': '30%', 'display': 'inline-block'}),
            html.Div([
                html.P("Tipo Consulta"),
                dcc.Dropdown(
                    ['Distrito Local', 'Distrito Federal', 'Municipio', 'Secciones'],
                    id='query_type',
                    value=''
                ),
            ], style={'width': '30%', 'display': 'inline-block'}),
        ]),
        html.Div([
            dcc.Checklist(id='political_parties', inline=False)
        ]),
        html.Div([
            dcc.Loading(dcc.Graph(id='comparision_map'))
        ])
    ])

    app.run_server(debug=True)
