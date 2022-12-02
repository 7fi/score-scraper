import numpy as np
import matplotlib.pyplot as plt

# from __future__ import division, print_function
# from re import M
# from googleapiclient.discovery import build
# from google.oauth2 import service_account

ID = '1B56mAoBHFct_xcUB9ZWt-GHA1s2Kmbmc_LiiyABxlpY'
# service = build('sheets', 'v4')
# sheet = service.spreadsheets()
venues = []
people = []


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
    def __init__(self, values):
        self.races = []
        self.name = str(values[0]).translate({ord(c): None for c in "[]'"})

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


values = sheet.values().get(spreadsheetId=ID, range='scores!A1:AG52',
                            majorDimension="COLUMNS").execute().get('values', [])
venues = values[0]

for i in range(1, len(values)):
    people.append(person(values[i]))


def getData(type, name, fleet, division, position, pair, regatta):
    for x in people:
        if x.name == name:
            tempRaces = x.races
            for race in reversed(range(len(x.races))):
                if fleet is not None:
                    if x.races[race].fleet != fleet:
                        tempRaces[race] = None
                if division is not None:
                    if x.races[race].division != division:
                        tempRaces[race] = None
                if position is not None:
                    if x.races[race].position != position:
                        tempRaces[race] = None
                if pair is not None:
                    if x.races[race].pair != pair:
                        tempRaces[race] = None
                if regatta is not None:
                    if x.races[race].regatta != regatta:
                        tempRaces[race] = None
            res = []
            if type == "raw":
                for i in tempRaces:
                    if i is not None:
                        res.append(i.score)
                    else:
                        res.append(0)
                return res
            elif type == "points":
                for i in tempRaces:
                    if i is not None:
                        res.append(i.fleetNum - i.score)
                    else:
                        res.append(0)
                return res
            elif type == "ratio":
                for i in tempRaces:
                    if i is not None:
                        res.append(i.fleetNum / i.score)
                    else:
                        res.append(0)
                return res

#print(getData("raw", "Barrett",None,None,None,None,None))


name1 = "Carter"
name2 = "Elliott"
Type = "points"
# Type("raw"/"points"/"ratio") Name Fleet("g"/"s"/"z") Division("a"/"b") Position("k"/"s") Pair("xxx") Regatta("XXX") | (None = any)
person1 = getData(Type, name1, None, None, None, None, None)
person2 = getData(Type, name2, None, None, None, None, None)

print(person1)
print(person2)

ind = np.arange(len(person1))
ind2 = np.arange(len(person2))
width = 0.4

plt.figure(figsize=(25, 5))
plt.bar(ind, person1, width, label=name1)
plt.bar(ind2 + width, person2, width, label=name2)

plt.xticks(ind + width / 2, [venues[i+1] for i in range(len(venues)-1)])
plt.ylabel("Points (Higher is better)")
plt.legend([name1, name2])
plt.show()
