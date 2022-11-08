import json
import plotly.express as px

politicalPartiesColors = {'PAN': '#00008B ',	'PRI': '#008000',	'PRD': '#FFD700',	'PVEM': '#00FF00',	'PT': '#B22222',
                          'MC': '#D2691E',	'MORENA': '#621132',	'PES': '#8B008B',	'RSP': '#8B0000',	'FPM': '#FF1493', 'NVA_ALIANZA': '#28BBFD'}


def paintMap(db):
    municipalityGeoJson = json.load(open('myJson.geojson', encoding="utf8"))

    fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color="Ganador",
                               locations="MUNICIPIO", featureidkey="properties.municipio",
                               color_continuous_scale="PuRd",
                               color_discrete_map=politicalPartiesColors,
                               mapbox_style="carto-positron", zoom=7, height=800,
                               center={
                                   'lat': 18.028157,
                                   'lon': -92.753621
                               })

    return fig
