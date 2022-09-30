import csv
import shapefile
import plotly.graph_objects as go

mapbox_access_token = 'pk.eyJ1IjoiZXJpY2tuYXZlIiwiYSI6ImNrdDh3MnppbzE2NXIydm5ybWtkNjM5Y3UifQ.4bfoMQc-wQkbI7f2YQRhUA'


def readFile(fileName):
    data = []
    aux = {}
    with open(fileName, encoding="UTF-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            aux = {}
            key = row
            for item in range(len(key)):
                aux[key[item]] = row[item]

            data.append(aux)

    return data


def midPoint(x1, y1, x2, y2):
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def getCenterCoordinates(shape, coordinates):
    for element in shape:
        if coordinates[0] > element[0]:
            coordinates[0] = element[0]

        if coordinates[1] < element[0]:
            coordinates[1] = element[0]

        if coordinates[2] > element[1]:
            coordinates[2] = element[1]

        if coordinates[3] < element[1]:
            coordinates[3] = element[1]

    return coordinates


def addTrace(fig, lat, lon):
    fig.add_trace(go.Scattermapbox(
        mode=None,
        fillcolor="#C2BA98",
        line=dict(color="black", width=1),
        showlegend=False,
        lon=lon,
        lat=lat))

    return fig


def createMap(municipality):
    fig = go.Figure()

    # READING SHAPE FILES
    municipalityShp = "assets/" + municipality + "/mun.shp"
    municipalityShp = shapefile.Reader(municipalityShp, encoding="iso-8859-15")

    coordinates = [999, -999, 999, -999]
    for item in municipalityShp:
        coordinates = getCenterCoordinates(item.shape.points, coordinates)
        lon, lat = zip(*item.shape.points)
        
        fig = addTrace(fig, lat, lon)

    mid_point_x, mid_point_y = midPoint(
        coordinates[2], coordinates[0], coordinates[3], coordinates[1])

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox=dict(style='light',
                                  accesstoken=mapbox_access_token,
                                  zoom=8,
                                  center={'lat': mid_point_x, 'lon': mid_point_y}))
    fig.show()


def main():
    createMap("Tabasco")


if __name__ == "__main__":
    main()
