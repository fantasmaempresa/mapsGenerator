import json
import pandas as pd
import plotly.express as px

politicalPartiesColors = {'PAN': '#00008B ',	'PRI': '#008000',	'PRD': '#FFD700',	'PVEM': '#00FF00',	'PT': '#B22222',
                          'MC': '#D2691E',	'MORENA': '#621132',	'PES': '#8B008B',	'RSP': '#8B0000',	'FPM': '#FF1493', 'NVA_ALIANZA': '#28BBFD'}

politicalPartiesRange = {'PAN': 'Blues',	'PRI': 'Greens',	'PRD': 'solar',	'PVEM': 'YlGN',	'PT': 'YlOrRd',
                         'MC': 'Oranges',	'MORENA': 'PuRd',	'PES': 'RdPu',	'RSP': 'amp',	'FPM': 'Burg', 'NVA_ALIANZA': 'PuBu',
                         'PAN_PRD_MC':'aggrnyl', 'PAN_MC':'agsunset', 'PAN_MC': 'bluered', 'PRD_MC':'blugrn',
                         'PT_MORENA': 'brwnyl',
                         'PAN,PRD Y MC':'gnbu', 'PAN Y PRD': 'greys', 'PAN Y MC': 'magenta', 'PRD Y MC': 'magma',
                         'PT,MORENA Y ES': 'pubu', 'PT Y MORENA': 'pubugn', 'PT Y ES': 'purd', 'MORENA Y ES': 'purp'}


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

def createGraphicBar(db, politicalParties, type):
    votes = []
    district = []
    parties = []

    for index, row in db.iterrows():
        for item in politicalParties:
            district.append(row[type])
            votes.append(row[item])
            parties.append(item)

        finalData = pd.DataFrame({
            "Partido": parties,
            type: district,
            "Votos": votes
        })

    fig = px.bar(finalData, x=type, y="Votos",
                 color="Partido", barmode="group",
                 color_discrete_map=politicalPartiesColors, height=700)
    return fig