import pandas as pd
import geopandas


def createGeoJsonMunicipalities(pathMun: str, pathShp: str):
    data = pd.read_csv(pathMun)
    dataShp = geopandas.read_file(pathShp)

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

    df_marques = pd.DataFrame(data)
    municipalityGeoJson = geopandas.GeoDataFrame(df_marques, crs='epsg:4326')
    municipalityGeoJson.to_file('myJson.geojson', driver='GeoJSON')


def createGeoJsonDistricts(pathShp: str, districtType: int):
    rangeD = range(6) if districtType == 1 else range(21)

    dataShp = geopandas.read_file(pathShp)
    nameData = []
    geoData = []

    for row in rangeD:
        nameData.append(row + 1)
        value = row + 1
        query = dataShp.query(
            "entidad == 27 & distrito_f == @value") if districtType == 1 else dataShp.query(
            "entidad == 27 & distrito_l == @value")
        geoData.append(query['geometry'].unary_union)

    data = {'district': nameData,
            'geometry': geoData
            }

    df_marques = pd.DataFrame(data)
    municipalityGeoJson = geopandas.GeoDataFrame(df_marques, crs='epsg:4326')
    municipalityGeoJson.to_file('myJson.geojson', driver='GeoJSON')
