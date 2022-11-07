from ast import parse

from choroplethOp.choroplethMun import pageMun
from choroplethOp.choroplethSecc import pageSecc
from choroplethOp.choroplethDF import pageDF
from choroplethOp.choroplethDL import pageDL
from interactiveMap.interactive import interactive

import argparse


if __name__ == "__main__":
    interactive()
    # parser = argparse.ArgumentParser(description="Render maps of votes")
    # parser.add_argument("--politicalParties", type=str, required=True)
    # parser.add_argument("--pathData", type=str, required=True)
    # parser.add_argument("--politicalParty", type=str, required=True)
    # parser.add_argument("--municipalityKey", type=int, default=0)
    # parser.add_argument("--mapType", type=str, default='Mun')

    # arguments = parser.parse_args()

    # if arguments.mapType == 'Mun':
    #     pageMun(arguments.politicalParties,
    #             arguments.pathData, arguments.politicalParty)
    # elif arguments.mapType == 'Secc':
    #     pageSecc(arguments.politicalParties, arguments.pathData,
    #              arguments.politicalParty, arguments.municipalityKey)
    # elif arguments.mapType == 'DL':
    #     pageDL(arguments.politicalParties,
    #            arguments.pathData, arguments.politicalParty)
    # elif arguments.mapType == 'DF':
    #     pageDF(arguments.politicalParties,
    #            arguments.pathData, arguments.politicalParty)
