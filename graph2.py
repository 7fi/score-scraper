import numpy as np
import matplotlib.pyplot as plt
import csv

regattaName = 'cascadia-cup-gold-scores'


def getFleetNum(regatta, fleet):
    if regatta == "OLY":
        return 13
    elif regatta == "OAK" and fleet == "g":
        return 15
    elif regatta == "OAK" and fleet == "s":
        return 18
    elif regatta == "SSP" and fleet == "g" or fleet == "s":
        return 30
    elif regatta == "SSP" and fleet == "z":
        return 10
    elif regatta == "BEL":
        return 10
    elif regatta == "ANA" and fleet == "g":
        return 17
    elif regatta == "ANA" and fleet == "s":
        return 24
    elif regatta == "FLE" and fleet == "g":
        return 17
    elif regatta == "FLE" and fleet == "s":
        return 24
    elif regatta == "PTO":
        return 16


class race:
    def __init__(self, regatta, score, fleet, fleetNum, division, position, pair):
        self.regatta = regatta
        self.score = score
        self.fleet = fleet
        self.fleetNum = fleetNum
        self.division = division
        self.position = position
        self.pair = pair


class person:
    def __init__(self, name, team, races):
        self.races = []
        # self.name = str(values[0]).translate({ord(c): None for c in "[]'"})
        self.name = name

        for i in range(1, len(values)):
            if len(values[i]) > 1:
                self.races.append(race(
                    venues[i],
                    int((str(values[i]).translate(
                        {ord(c): None for c in "['"}).split(","))[0]),
                    (str(values[i]).split(","))[1],
                    getFleetNum(venues[i], (str(values[i]).split(","))[1]),
                    (str(values[i]).split(","))[2],
                    (str(values[i]).split(","))[3],
                    (str(values[i]).translate(
                        {ord(c): None for c in "[]'"}).split(","))[4]
                )
                )
            else:
                self.races.append(None)


values = []
with open(f'{regattaName}.csv') as file:
    reader = csv.reader(file)
    for row in reader:
        values.append(row)

print(values)
