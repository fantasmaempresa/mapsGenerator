import pandas as pd
import geopandas

munGeoJson = 'assets/geoJson/municipalities.geojson'
dFGeoJson = 'assets/geoJson/federalDistrict.geojson'
dLGeoJson = 'assets/geoJson/localDistrict.geojson'
seccGeoJson = 'assets/geoJson/seccion.geojson'

pathDBMun = 'assets/Puebla/DB/municipios.csv'
pathDBSecc = 'assets/Puebla/DB/secciones.csv'

pathMun = 'assets/Puebla/municipios.csv'
pathSecc = 'assets/Puebla/secciones.csv'

def createAllGeoJson(pathShp: str, mapType: str):
    filterData(mapType)
    type = 'GENERAL'

    munData = pd.read_csv(pathMun)
    dataShp = geopandas.read_file(pathShp)

    # MUNICIPALITIES
    nameData = []
    geoData = []
    for index, row in munData.iterrows():
        nameData.append(row['municipio'])
        value = row['clave']
        query = dataShp.query("MUNICIPIO == @value")
        geoData.append(query['geometry'].unary_union)

    data = {'municipio': nameData,
            'geometry': geoData
            }

    saveGeoJson(data, munGeoJson)
    
    # SECCIONES
    if mapType != 0:
        type = munData.iloc[0]['municipio']
        value = munData.iloc[0]['clave']
        dataShp.query("MUNICIPIO == @value", inplace=True)

    dataShp.to_file(seccGeoJson, driver='GeoJSON')
    return type

def districts(dataShp):
    # FEDERAL DISTRICT
    nameData = []
    geoData = []
    for row in range(15):
        nameData.append(row + 1)
        value = row + 1
        query = dataShp.query("entidad == 21 & distrito_f == @value")
        geoData.append(query['geometry'].unary_union)

    data = {'district': nameData,
            'geometry': geoData
            }
    
    saveGeoJson(data, dFGeoJson)

    # LOCAl DISTRICT
    nameData = []
    geoData = []
    for row in range(26):
        nameData.append(row + 1)
        value = row + 1
        query = dataShp.query("entidad == 21 & distrito_l == @value")
        geoData.append(query['geometry'].unary_union)

    data = {'district': nameData,
            'geometry': geoData
            }
    
    saveGeoJson(data, dLGeoJson)

def filterData(munType):
    munData = pd.read_csv(pathDBMun)
    seccData = pd.read_csv(pathDBSecc)

    if munType != 0:
        munData = munData.query('clave == @munType')
        value = munData.iloc[0]['municipio']
        seccData = seccData.query('MUNICIPIO == @value')

    munData.to_csv(pathMun,index=False)
    seccData.to_csv(pathSecc, index=False)
 
def saveGeoJson(data: dict, fileName: str):
    df_marques = pd.DataFrame(data)
    geoJson = geopandas.GeoDataFrame(df_marques, crs='epsg:4326')
    geoJson.to_file(fileName, driver='GeoJSON')