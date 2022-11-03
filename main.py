from choroplethOp.choroplethMun import pageMun


if __name__ == "__main__":
    # pageDL("PAN,PRI,PRD", "mapas/2020-2021/csv/ayu_resumen_general.csv", "MORENA")
    # pageDF("PAN,PRI,PRD,MORENA",
    #        "mapas/2020-2021/csv/ayu_resumen_general.csv", "MORENA")
    pageMun("PAN,PRI,PRD,MORENA", "mapas/2020-2021/csv/ayu_resumen_general.csv", "MORENA")
