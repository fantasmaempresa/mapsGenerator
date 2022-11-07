from dash import Dash, html, dcc, Input, Output
import pandas as pd

app = Dash(__name__)

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
    Input('year', 'value'),
    Input('candidance_type', 'value'),
)
def getPoliticPartiesByFile(year: str, candidance_type: str):
    if candidance_type != '':
        file = originData.query(
            'year == @year and type == @candidance_type')['file'].iloc[0];
        
        path = 'mapas/' + year + '/csv/' + file
        data = pd.read_csv(path)
        
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
        
        return keys
    return []


def interactive():
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
                    value=[]
                ),
            ], style={'width': '30%', 'display': 'inline-block'}),
        ]),
        html.Div([
            dcc.Checklist(id='political_parties', inline=False)
        ])
    ])

    app.run_server(debug=True)
