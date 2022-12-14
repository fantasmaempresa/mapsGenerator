import pandas as pd
import geopandas

munGeoJson = 'assets/geoJson/municipalities.geojson'
dFGeoJson = 'assets/geoJson/federalDistrict.geojson'
dLGeoJson = 'assets/geoJson/localDistrict.geojson'
seccGeoJson = 'assets/geoJson/seccion.geojson'

def createAllGeoJson(pathMun: str, pathShp: str):
    data = pd.read_csv(pathMun)
    dataShp = geopandas.read_file(pathShp)

    # MUNICIPALITIES
    nameData = []
    geoData = []
    for index, row in data.iterrows():
        nameData.append(row['municipio'])
        value = row['clave']
        query = dataShp.query(
            "entidad == 27 & municipio == @value")
        geoData.append(query['geometry'].unary_union)

    data = {'municipio': nameData,
            'geometry': geoData
            }

    saveGeoJson(data, munGeoJson)

    # FEDERAL DISTRICT
    nameData = []
    geoData = []
    for row in range(6):
        nameData.append(row + 1)
        value = row + 1
        query = dataShp.query("entidad == 27 & distrito_f == @value")
        geoData.append(query['geometry'].unary_union)

    data = {'district': nameData,
            'geometry': geoData
            }
    
    saveGeoJson(data, dFGeoJson)

    # LOCAl DISTRICT
    nameData = []
    geoData = []
    for row in range(21):
        nameData.append(row + 1)
        value = row + 1
        query = dataShp.query("entidad == 27 & distrito_l == @value")
        geoData.append(query['geometry'].unary_union)

    data = {'district': nameData,
            'geometry': geoData
            }
    
    saveGeoJson(data, dLGeoJson)
    
    # SECCIONES
    dataShp.query("entidad == 27", inplace=True)
    dataShp.to_file(seccGeoJson, driver='GeoJSON')

def saveGeoJson(data: dict, fileName: str):
    df_marques = pd.DataFrame(data)
    geoJson = geopandas.GeoDataFrame(df_marques, crs='epsg:4326')
    geoJson.to_file(fileName, driver='GeoJSON')