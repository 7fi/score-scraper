from operator import indexOf
import functools
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import warnings
warnings.filterwarnings("ignore")

regattas = {"south regional": "s22/south-regional-nwisa",  "oak gold": "s22/island-cup",
            "oak silver": "s22/islands-cup-silver", "SSP gold": "s22/nwisa-combined-division",
            "SSP silver": "s22/nwisa-combined-division-silver", "SSP bronze": "s22/nwisa-combined-division-bronze",
            "bellingham": "s22/bellingham-fleet-race", "anacortes gold": "s22/seafarers-cup-gold",
            "anacortes silver": "s22/seafarers-cup-silver", "fleet champs gold": "s22/nwisa-doublehanded",
            "fleet champs silver": "s22/nwisa-silver-fleet-champs", "PT open": "s22/port-townsend-open"}

names = {"Elliott Chalcraft": "#e0570d", 'Carter Anderson': "#3684a3",
         "Ryan Downey": "#2de00d", "Sabrina Anderson": "#d20de0", "Barrett Lhamon": "#f00"}
# Raw Points Ratio
Type = "Points"
people = []


class person:
    def __init__(self, name, team, races):
        self.name = name
        self.team = team
        self.races = races

    def __repr__(self):
        return f"{self.name} {self.team} {self.races}"


class race:
    """
    """

    def __init__(self, number, division, score, teams, position, venue):
        self.number = number
        self.division = division
        self.score = score
        self.teams = teams
        self.position = position
        self.venue = venue

    def __repr__(self):
        return f"#: {self.number} D:{self.division} s:{self.score} t:{len(self.teams)} {self.position}"


def addPerson(name, pos, division, home, raceNums, scores, teams, venue):
    """
    Function to add person to list of people or edit a persons data if they already exist. 

    Parameters:
    --------
    name: Str
        Person's name
    pos: Str 
        Person's position (Skipper/Crew)
    division: Str
        Person's division (A/B)
    home: Str
        Person's school
    raceNums: list of lists of strings
        Numbers of start and end races participated in
    scores: list of ints
        list of all scores for person's division
    teams: list of strings
        list of all teams in regatta
    venue: 
        Name of regatta / venue
    """
    newNums = []
    if name not in [p.name for p in people]:
        people.append(person(name, home, []))
    if raceNums == [['']]:
        newNums = list(range(len(scores)))
    elif len(raceNums) > 0:
        for i, num in enumerate(raceNums):
            if len(num) > 1:
                for j in range(int(num[0]), int(num[1]) + 1):
                    newNums.append(j)
            else:
                newNums.append(int(num[0]))
    raceNums = newNums
    for i, score in enumerate(scores):
        if i + 1 in raceNums:
            for s in people:
                if s.name == name:
                    s.races.append(race(
                        i + 1, division, score, [t for t in teams], pos, venue))


def getData(type, name, fleet=None, division=None, position=None, pair=None, regatta=None):
    """
    Fetches data of specified person based on input parameters.

    Parameters:
    ------
    type: Str (required)
        Type of data (Raw / Points / Ratio)
    name: Str (required)
        Name of person
    fleet: Str (optional)
        Fleet to search by(Gold / Silver/ Bronze)
    division: Str (optional)
        Division to search by (A / B)
    position: Str (optional)
        Position to search by (Skipper / Crew)
    pair: Str (optional)
        Person to be paired with 
    regatta: Str (optional)
        Regatta to search within

    Returns:
    ------
    data: dict
        Dictionary of race names and race scores

    """
    data = {}
    for p in people:
        if p.name == name:
            for r in p.races:
                if regatta != None and r.venue == regatta:
                    if type == "Raw":
                        if isinstance(r.score, int):
                            data[f"{regatta} {r.division}{r.number}"] = r.score
                        else:
                            data[f"{regatta} {r.division}{r.number}"] = len(
                                r.teams) + 1
                    elif type == "Points":
                        if isinstance(r.score, int):
                            data[f"{regatta} {r.division}{r.number}"] = len(
                                r.teams) - r.score + 1
                        else:
                            data[f"{regatta} {r.division}{r.number}"] = len(
                                r.teams) + 1
                    elif type == "Ratio":
                        if isinstance(r.score, int):
                            data[f"{regatta} {r.division}{r.number}"] = 1 - \
                                (r.score / len(r.teams))
                        else:
                            data[f"{regatta} {r.division}{r.number}"] = len(
                                r.teams) + 1
    return data


def compare(first, second):
    if first[len(first) - 1] > second[len(second) - 1]:
        return 1
    if first[len(first) - 1] < second[len(second) - 1]:
        return - 1
    if first[len(first) - 2] > second[len(second) - 2]:
        return 1
    if first[len(first) - 2] < second[len(second) - 2]:
        return - 1
    return 0


for i, regatta in enumerate(list(regattas.values())):
    betterVenue = list(regattas.keys())[i]
    print(f"({i + 1}/{len(list(regattas.values()))}) analyzing {betterVenue}")
    # full scores
    url = f"https://scores.hssailing.org/{regatta}/full-scores/"
    page = requests.get(url)
    fullScores = BeautifulSoup(page.content, 'html.parser')

    # sailors
    url = f"https://scores.hssailing.org/{regatta}/sailors/"
    page = requests.get(url)
    sailors = BeautifulSoup(page.content, 'html.parser')

    scoreData = fullScores.find_all('table', class_="results")[
        0].contents[1].contents
    sailorData = sailors.find('table', class_="sailors").contents[1].contents
    header = fullScores.find(
        'table', class_="results").find_all('th', class_="right")
    raceCount = int(header[len(header) - 2].text)

    teamCount = int(len(scoreData) / 3)

    teamHomes = [(scoreData[(i*3) - 3].find('a').text)
                 for i in range(teamCount)]

    # loop through teams

    for i in range(1, teamCount):
        teamHome = scoreData[(i*3) - 3].find('a').text
        teamName = scoreData[(i*3) - 2].contents[2].text
        teamScores = {'A': [], 'B': []}

        teamScores["A"] = [int(scoreData[(i*3) - 3].contents[j].text) for j in range(
            4, (4 + raceCount)) if scoreData[(i*3) - 3].contents[j].text.isdigit()]
        teamScores["B"] = [int(scoreData[(i*3) - 2].contents[j].text) for j in range(
            4, (4 + raceCount)) if scoreData[(i*3) - 2].contents[j].text.isdigit()]

        teamNameEl = [i for i in sailors.find_all(
            'td', class_="teamname") if i.text == teamName][0]

        rowClass = teamNameEl.parent['class'][1]

        index = 0
        row = teamNameEl.parent
        while row.next_sibling is not None and row['class'][0] != "topborder" and row['class'][0] != "reserves-row" or index == 0:
            curRow = row
            while curRow.find_all('td', class_="division-cell") == []:
                curRow = curRow.previous_sibling
            division = curRow.find_all('td', class_="division-cell")[0].text

            # Get Skipper
            skipper = row.contents[len(row.contents) - 4]
            skipperName = skipper.text.split(" '", 1)[0]
            if skipperName != "":
                raceNums = skipper.next_sibling.text.split(",")
                raceNums = [i.split("-", 1) for i in raceNums]
                addPerson(skipper.text.split(" '")[
                          0], "Skipper", division, teamHome, raceNums, teamScores[division], teamHomes, betterVenue)

            # Get Crew
            crew = row.contents[len(row.contents) - 2]
            crewName = crew.text.split(" '", 1)[0]
            if crewName != "":
                raceNums = crew.next_sibling.text.split(",")
                raceNums = [i.split("-", 1) for i in raceNums]
                addPerson(crew.text.split(" '")[
                          0], "Crew", division, teamHome, raceNums, teamScores[division], teamHomes, betterVenue)

            row = row.next_sibling
            index += 1

plt.figure(figsize=(20, 5))
print("Analyzing done, Graphing...")

prev = 0
xTicks = []
nameLabels = []
maxVals = []

for regatta in list(regattas.keys()):
    data = {}
    races = []
    for p in list(names.keys()):
        try:
            data[p] = getData(Type, p, regatta=regatta)
            races.extend(list(data[p].keys()))
            maxVals.append(max(list(data[p].values())))
        except:
            print("Couldn't find person 👀")
    races = sorted([*set(races)], key=functools.cmp_to_key(compare))

    for p in list(names.keys()):
        # print(races, data[p])
        x = sorted([indexOf(races, race) +
                   prev for race in list(data[p].keys()) if race in races])
        y = [data[p][race] for race in races if race in data[p]]
        # print(p,x, y)
        # if pData
        if x != [] and y != []:
            plt.scatter(x, y, color=names[p], alpha=0.5, zorder=1)
            if p not in nameLabels:
                nameLabels.append(p)
            if len(x) > 3 and Type != "Ratio":
                xnew = np.linspace(min(x), max(x), 300)
                spl = make_interp_spline(x, y, k=3)
                ynew = spl(xnew)
                plt.plot(xnew, ynew, color=names[p], alpha=0.5, zorder=0)
                nameLabels.append("_")
            plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))
                     (np.unique(x)), color=names[p])
            nameLabels.append("_")

    prev += len(races)
    xTicks.extend(races)

plt.xlim([-1, len(xTicks)])
if Type == "Ratio":
    plt.yticks(np.arange(0, 1, 0.1))
    plt.ylim([0, 1])
else:
    plt.yticks(np.arange(0, max(maxVals) + 1, 2))
    plt.ylim([0, max(maxVals) + 1])

plt.xticks(range(len(xTicks)), xTicks, rotation=90)
plt.ylabel(Type)
plt.legend(nameLabels, loc="upper right")
plt.tight_layout()
plt.grid(True)
plt.savefig("fig.png")

plt.show()
