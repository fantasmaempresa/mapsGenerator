import pandas as pd

def getWinner(row, politcParties):
    
    dictWinners = {}
    for key in politcParties:
        dictWinners[key] = row[key]

    return max(dictWinners, key=dictWinners.get)

def calculateParticipation(row):
    return (row['TOTAL DE VOTOS'] * 100) / row['LISTA NOMINAL']

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