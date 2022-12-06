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


def searchTypeName(row, dbSecc, type):
    value = row['SECCION ELECTORAL']
    filter = dbSecc.query('SECCION == @value')

    if filter.iloc[0]['TIPO'] == type:
        return 1
    else:
        return 0


def searchMunicipality(row, dbSecc):
    value = value = row['SECCION ELECTORAL']
    filter = dbSecc.query('SECCION == @value')

    return filter.iloc[0]['MUNICIPIO']


def sumPoliticParties(row, politicalParties):
    sum = 0
    for item in politicalParties:
        sum = sum + row[item]

    return sum


def putClassification(row, highPriority, mediumPriority):
    value = row['TOTAL DE VOTOS']

    if value >= highPriority:
        return 'ALTA (AAA)'
    elif value >= mediumPriority and value < highPriority:
        return 'MEDIA (AA)'
    else:
        return 'BAJA (A)'


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
    
    for columnHeader in db.columns:
        db.at['Total', columnHeader] = db[columnHeader].sum()

    db['% PARTICIPACION'] = db.apply(
        lambda row: calculateParticipation(row), axis=1)

    db[key].iloc[-1] = 'TOTAL'
    
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

    db['MUNICIPIO'] = db.apply(
        lambda row: searchMunicipality(row, dbSecc), axis=1)
    db['No RGS'] = db.apply(lambda row: searchType(row, dbSecc), axis=1)
    db['DISTRITO L'] = db.apply(
        lambda row: row['DISTRITO L']/row['No Suplentes'], axis=1)
    db['DISTRITO F'] = db.apply(
        lambda row: row['DISTRITO F']/row['No Suplentes'], axis=1)

    db['MIXTO'] = db.apply(lambda row: searchTypeName(
        row, dbSecc, 'MIXTO'), axis=1)
    db['URBANO'] = db.apply(lambda row: searchTypeName(
        row, dbSecc, 'URBANO'), axis=1)
    db['RURAL'] = db.apply(lambda row: searchTypeName(
        row, dbSecc, 'RURAL'), axis=1)
    db['TOTAL CASILLAS'] = db.apply(lambda row: 1, axis=1)

    db = db.groupby([key]).sum(
        numeric_only=True).T.T.reset_index()

    return db[[key, 'No Propietarios', 'No Suplentes', 'No RGS', 'MIXTO', 'URBANO', 'RURAL', 'TOTAL CASILLAS']]


def createDataToVS(pathData, politicalPartiesG1, politicalPartiesG2, key):
    df = pd.read_csv(pathData)

    db = df.groupby([key]).sum(
        numeric_only=True).T.T.reset_index()

    db['_'.join(politicalPartiesG1)] = db.apply(
        lambda x: sumPoliticParties(x, politicalPartiesG1), axis=1)
    db['_'.join(politicalPartiesG2)] = db.apply(
        lambda x: sumPoliticParties(x, politicalPartiesG2), axis=1)

    db['GANADOR'] = db.apply(lambda row: getWinner(
        row, ['_'.join(politicalPartiesG1), '_'.join(politicalPartiesG2)]), axis=1)

    return db[[key, '_'.join(politicalPartiesG1), '_'.join(politicalPartiesG2), 'GANADOR']]


def createDataClassification(pathData, key):
    df = pd.read_csv(pathData)

    db = df.groupby([key]).sum(
        numeric_only=True).T.T.reset_index()

    db.drop('NUMERO DE VOTOS VALIDOS', inplace=True, axis=1, errors='ignore')
    db.drop('% PARTICIPACION CIUDADANA', inplace=True, axis=1, errors='ignore')
    db.drop('CASILLA', inplace=True, axis=1, errors='ignore')

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

    highPriority = (db['TOTAL DE VOTOS'].max() + db['TOTAL DE VOTOS'].min())/2
    mediumPriority = (db['TOTAL DE VOTOS'].min() + highPriority) / 2
    
    db['PRIORIDAD'] = db.apply(lambda row : putClassification(row, highPriority, mediumPriority), axis=1)

    return db.sort_values(by=['TOTAL DE VOTOS'], ascending=False)
