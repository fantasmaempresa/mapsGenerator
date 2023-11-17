from interactiveMap.interactive import interactive

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tipo de Mapa a mostrar")
    parser.add_argument("--mapType", type=int, default=0)

    arguments = parser.parse_args()
    
    interactive(arguments.mapType)