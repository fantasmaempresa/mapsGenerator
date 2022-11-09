import json
import plotly.express as px

politicalPartiesColors = {'PAN': '#00008B ',	'PRI': '#008000',	'PRD': '#FFD700',	'PVEM': '#00FF00',	'PT': '#B22222',
                          'MC': '#D2691E',	'MORENA': '#621132',	'PES': '#8B008B',	'RSP': '#8B0000',	'FPM': '#FF1493', 'NVA_ALIANZA': '#28BBFD'}

politicalPartiesRange = {'PAN': 'Blues',	'PRI': 'Greens',	'PRD': 'solar',	'PVEM': 'YlGN',	'PT': 'YlOrRd',
                         'MC': 'Oranges',	'MORENA': 'PuRd',	'PES': 'RdPu',	'RSP': 'amp',	'FPM': 'Burg', 'NVA_ALIANZA': 'PuBu'}


def paintMap(db, geoJsonFile, locations, keyToMap, idKey):
    municipalityGeoJson = json.load(open(geoJsonFile, encoding="utf8"))

    if keyToMap == "GANADOR":
        fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color=keyToMap,
                                locations=locations, featureidkey=idKey,
                                color_discrete_map=politicalPartiesColors,
                                mapbox_style="carto-positron", zoom=7,height=700,
                                center={
                                    'lat': 18.028157,
                                    'lon': -92.753621
                                })
    else:
        fig = px.choropleth_mapbox(db, geojson=municipalityGeoJson, color=keyToMap,
                                locations=locations, featureidkey=idKey,
                                color_continuous_scale=politicalPartiesRange[keyToMap],
                                mapbox_style="carto-positron", zoom=7, height=700,
                                center={
                                    'lat': 18.028157,
                                    'lon': -92.753621
                                })
        


    return fig
