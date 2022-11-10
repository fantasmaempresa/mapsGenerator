import pandas as pd

pathSecc = 'assets/Tabasco/secciones.csv'

def getWinner(row, politcParties):
    
    dictWinners = {}
    for key in politcParties:
        dictWinners[key] = row[key]

    return max(dictWinners, key=dictWinners.get)

def calculateParticipation(row):
    return (row['TOTAL DE VOTOS'] * 100) / row['LISTA NOMINAL']

def searchType(row, dbSecc):
    value = row['SECCION ELECTORAL']
    filter = dbSecc.query('SECCION == @value')
    
    if filter.iloc[0]['TIPO'] == 'MIXTO':
        return 10
    elif filter.iloc[0]['TIPO'] == 'URBANO':
        return 10
    elif filter.iloc[0]['TIPO'] == 'RURAL':
        return 5

def searchMunicipality(row, dbSecc):
    value = value = row['SECCION ELECTORAL']
    filter = dbSecc.query('SECCION == @value')
    
    return filter.iloc[0]['MUNICIPIO']

def createDataToMap(pathData: str, politicParties, key):
    df = pd.read_csv(pathData)

    db = df.groupby([key]).sum(
        numeric_only=True).T.T.reset_index()
    
    db['GANADOR'] = db.apply(lambda row: getWinner(
        row, politicParties), axis=1)

    return db

def createDataToTable(pathData: str, key):
    df = pd.read_csv(pathData)

    db = df.groupby([key]).sum(
        numeric_only=True).T.T.reset_index()

    db['% PARTICIPACION'] = db.apply(lambda row: calculateParticipation(row), axis=1)

    db.drop('% PARTICIPACION CIUDADANA', axis=1, inplace=True, errors='ignore')
    
    if key == "DISTRITO F":
        db.drop('SECCION ELECTORAL', axis=1, inplace=True, errors='ignore')
        db.drop('DISTRITO L', axis=1, inplace=True, errors='ignore')
    elif key == "DISTRITO L":
        db.drop('SECCION ELECTORAL', axis=1, inplace=True, errors='ignore')
        db.drop('DISTRITO F', axis=1, inplace=True, errors='ignore')
    elif key == "MUNICIPIO":
        db.drop('SECCION ELECTORAL', axis=1, inplace=True, errors='ignore')
        db.drop('DISTRITO L', axis=1, inplace=True, errors='ignore')
        db.drop('DISTRITO F', axis=1, inplace=True, errors='ignore')
    else:
        db.drop('DISTRITO L', axis=1, inplace=True, errors='ignore')
        db.drop('DISTRITO F', axis=1, inplace=True, errors='ignore')
    
    return db

def createDataTableRG(pathData, key):
    df = pd.read_csv(pathData)
    dbSecc = pd.read_csv(pathSecc)
    
    df['No Propietarios'] = df.apply(lambda row: 1, axis=1)
    df['No Suplentes'] = df.apply(lambda row: 1, axis=1)
    
    db = df.groupby(['SECCION ELECTORAL']).sum(
        numeric_only=True).T.T.reset_index()
    
    db['MUNICIPIO'] = db.apply(lambda row: searchMunicipality(row, dbSecc), axis=1)
    db['No RGS'] = db.apply(lambda row: searchType(row, dbSecc), axis=1)
    db['DISTRITO L'] = db.apply(lambda row: row['DISTRITO L']/row['No Suplentes'], axis=1)
    db['DISTRITO F'] = db.apply(lambda row: row['DISTRITO F']/row['No Suplentes'], axis=1)
    
    db = db.groupby([key]).sum(
        numeric_only=True).T.T.reset_index()
    
    return db[[key,'No Propietarios', 'No Suplentes', 'No RGS']]