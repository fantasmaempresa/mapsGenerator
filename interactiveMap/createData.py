import pandas as pd

def getWinner(row, politcParties):
    
    dictWinners = {}
    for key in politcParties:
        dictWinners[key] = row[key]

    return max(dictWinners, key=dictWinners.get)

def createDataMunicipalities(pathData: str, politicParties):
    df = pd.read_csv(pathData)

    db = df.groupby(['MUNICIPIO']).sum(
        numeric_only=True).T.T.reset_index()
    
    db['WINNER'] = db.apply(lambda row: getWinner(
        row, politicParties), axis=1)
    
    return db