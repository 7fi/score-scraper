from operator import indexOf
import functools
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline, BSpline

# "SSP gold": "s22/nwisa-combined-division", "SSP silver": "s22/nwisa-combined-division-silver", after oak # "bellingham": "s22/bellingham-fleet-race/", after bronze, 
# regattas = {"south regional": "s22/south-regional-nwisa",  "oak gold": "s22/island-cup", 
#             "oak silver": "s22/islands-cup-silver", "SSP bronze":"s22/nwisa-combined-division-bronze", 
#             "anacortes gold" :"s22/seafarers-cup-gold", "anacortes silver":"s22/seafarers-cup-silver", 
#             "fleet champs gold":"s22/nwisa-doublehanded", "fleet champs silver":"s22/nwisa-silver-fleet-champs", 
#             "PT open":"s22/port-townsend-open"}

regattas = {"ACCs": "f22/2022-atlantic-coast"}
# better_spring = [, , "bellingham gold", "bellingham silver", "bellingham bronze"]

# regatta_names = ["f22/nwisa-girls-qualifiers", "f22/cascadia-cup-gold", "f22/2022-issa-pcisa-all-girls-invitational",
#                  "f22/pontiac-bay-regional-south-regional", "f22/fall-champs", "f22/2022-atlantic-coast"]
# better_names = ["girls quals", "cascadia gold", "PCISA girls",
#                 "south regional", "fall champs", "ACCs"]
names = {"Elliott Chalcraft": "#e0570d"} # , 'Carter Anderson':"#3684a3", "Ryan Downey": "#2de00d", "Sabrina Anderson": "#d20de0", "Barrett Lhamon": "#f00"
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
    newNums = []
    if name not in [p.name for p in people]:
        people.append(person(name, home, []))
    if raceNums == [['']]:
        newNums = list(range(len(scores)))
        # print(raceNums)
    elif len(raceNums) != 0:
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

def getData(type, name, fleet, division, position, pair, regatta):
    data = {}
    for p in people:
        if p.name == name:
            # racenum = 0
            for r in p.races:
                # print(r.score)
                if r.venue == regatta:
                    if type == "Raw":
                        if isinstance(r.score, int):
                            data[f"{regatta} {r.division}{r.number}"] = r.score
                        else:
                            data[f"{regatta} {r.division}{r.number}"] = len(r.teams) + 1
                    if type == "Points":
                        if isinstance(r.score, int):
                            data[f"{regatta} {r.division}{r.number}"] = len(r.teams) - r.score + 1
                        else:
                            data[f"{regatta} {r.division}{r.number}"] = len(r.teams) + 1
                    if type == "Ratio":
                        if isinstance(r.score, int):
                            data[f"{regatta} {r.division}{r.number}"] = 1 - (r.score / len(r.teams))
                        else:
                            data[f"{regatta} {r.division}{r.number}"] = len(r.teams) + 1
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
    else:
        return 0

for i, regatta in enumerate(list(regattas.values())):
    betterVenue = list(regattas.keys())[i]
    print(f"({i + 1}/{len(list(regattas.values()))}) analyzing {betterVenue}")
    # full scores
    url = f"https://scores.hssailing.org/{regatta}/full-scores/"
    page = requests.get(url)
    fullScores = BeautifulSoup(page.content, 'html.parser')

    # sailors a
    url = f"https://scores.hssailing.org/{regatta}/sailors/"
    page = requests.get(url)
    sailors = BeautifulSoup(page.content, 'html.parser')

    # A
    url = f"https://scores.hssailing.org/{regatta}/A/"
    page = requests.get(url)
    a = BeautifulSoup(page.content, 'html.parser')

    # B
    url = f"https://scores.hssailing.org/{regatta}/B/"
    page = requests.get(url)
    b = BeautifulSoup(page.content, 'html.parser')

    scoreData = fullScores.find('table', class_="results").contents[1].contents
    aData = a.find('table', class_="results").contents[1].contents
    bData = b.find('table', class_="results").contents[1].contents
    sailorData = sailors.find('table', class_="sailors").contents[1].contents
    header = fullScores.find(
        'table', class_="results").find_all('th', class_="right")
    raceCount = int(header[len(header) - 2].text)

    teamCount = int(len(scoreData) / 3)

    teamHomes = [(scoreData[(i*3) - 3].find('a').text) for i in range(teamCount)]

    # loop through teams
    for i in range(1, teamCount):
        teamHome = scoreData[(i*3) - 3].find('a').text
        teamName = scoreData[(i*3) - 2].contents[2].text

        teamAScores = []
        for j in range(4, (4 + raceCount)):
            score = scoreData[(i*3) - 3].contents[j].text
            if score.isdigit():
                score = int(score)
            teamAScores.append(score)

        teamBScores = []
        for j in range(4, (4 + raceCount)):
            score = scoreData[(i*3) - 2].contents[j].text
            if score.isdigit():
                score = int(score)
            teamBScores.append(score)

        teamATotal = int(scoreData[(i*3) - 3].contents[5 + raceCount].text)
        teamBTotal = int(scoreData[(i*3) - 2].contents[5 + raceCount].text)

        teamASkippers = []
        teamACrews = []
        teamBSkippers = []
        teamBCrews = []

        allNames = sailors.find_all('td', class_="teamname")
        # print(allNames)
        teamNameEl = [i for i in allNames if i.text == teamName][0]
        # print(teamNameEl)


        rowClass = teamNameEl.parent['class'][1]
        # print(sailors.find_all("tr", class_=rowClass))
        # print(teamNameEl.parent.parent.find_all("tr", class_=rowClass))
        for i,row in enumerate(sailors.find_all("tr", class_=rowClass)):
            if i != 0 and row['class'][0] == "topborder":
                break
            skipper = row.contents[len(row.contents) - 4]
            print(skipper)
                


        for skipper in teamNameEl.parent.find_all('td', class_="skipper"):
            if skipper.parent.previous_sibling and skipper.parent.previous_sibling.find_all('td', class_="skipper"):
                skipper2 = skipper.parent.previous_sibling.find(
                    'td', class_="skipper")
                raceNums = skipper2.next_sibling.text.split(",")
                raceNums = [i.split("-", 1) for i in raceNums]
                addPerson(skipper2.text.split(" '")[0],"Skipper", 'A', teamHome, raceNums, teamAScores, teamHomes, betterVenue)
            # print(skipper)
            division = skipper.parent.find_all('td', class_="division-cell").text
            # print(division)
            raceNums = skipper.next_sibling.text.split(",")
            raceNums = [i.split("-", 1) for i in raceNums]
            addPerson(skipper.text.split(" '")[0],"Skipper",'A', teamHome, raceNums, teamAScores, teamHomes, betterVenue)

        for crew in teamNameEl.parent.find_all('td', class_="crew"):
            races = crew.next_sibling.text.split(",")
            races = [i.split("-", 1) for i in races]
            addPerson(crew.text.split(" '")[0],"Crew",'A', teamHome, races, teamAScores, teamHomes, betterVenue)
            if crew.parent.next_sibling and crew.parent.next_sibling.find_all('td', class_="crew"):
                crew2 = crew.parent.next_sibling.find(
                    'td', class_="crew")
                races = crew2.next_sibling.text.split(",")
                races = [i.split("-", 1) for i in races]
                addPerson(crew2.text.split(" '")[0],"Crew",'A', teamHome, races, teamAScores, teamHomes, betterVenue)
                if crew2.parent.next_sibling and crew2.parent.next_sibling.find_all('td', class_="crew"):
                    crew3 = crew2.parent.next_sibling.find(
                        'td', class_="crew")
                    races = crew3.next_sibling.text.split(",")
                    races = [i.split("-", 1) for i in races]
                    addPerson(crew3.text.split(" '")[0],"Crew",'A', teamHome, races, teamAScores, teamHomes, betterVenue)

        # allNames = b.find_all('td', class_="teamname")
        # teamNameEl = [i for i in allNames if i.text == teamName][0]

        # for skipper in teamNameEl.parent.previous_sibling.find_all('td', class_="skipper"):
        #     if skipper.parent.previous_sibling and skipper.parent.previous_sibling.find_all('td', class_="skipper"):
        #         skipper2 = skipper.parent.previous_sibling.find(
        #             'td', class_="skipper")
        #         races = skipper2.next_sibling.text.split(",")
        #         races = [i.split("-", 1) for i in races]
        #         addPerson(skipper2.text.split(" '")[0],"Skipper",'B', teamHome, races, teamBScores, teamHomes, betterVenue)
        #     races = skipper.next_sibling.text.split(",")
        #     races = [i.split("-", 1) for i in races]
        #     addPerson(skipper.text.split(" '")[0],"Skipper",'B', teamHome, races, teamBScores, teamHomes, betterVenue)

        # for crew in teamNameEl.parent.find_all('td', class_="crew"):
        #     races = crew.next_sibling.text.split(",")
        #     races = [i.split("-", 1) for i in races]
        #     addPerson(crew.text.split(" '")[0],"Crew",'B', teamHome, races, teamBScores, teamHomes, betterVenue)
        #     if crew.parent.next_sibling and crew.parent.next_sibling.find_all('td', class_="crew"):
        #         crew2 = crew.parent.next_sibling.find(
        #             'td', class_="crew")
        #         races = crew2.next_sibling.text.split(",")
        #         races = [i.split("-", 1) for i in races]
        #         addPerson(crew2.text.split(" '")[0],"Crew",'B', teamHome, races, teamBScores, teamHomes, betterVenue)

        #         if crew2.parent.next_sibling and crew2.parent.next_sibling.find_all('td', class_="crew"):
        #             crew3 = crew2.parent.next_sibling.find(
        #                 'td', class_="crew")
        #             races = crew3.next_sibling.text.split(",")
        #             races = [i.split("-", 1) for i in races]
        #             addPerson(crew3.text.split(" '")[0],"Crew",'B', teamHome, races, teamBScores, teamHomes, betterVenue)

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
            data[p] = getData(Type, p, None, None, None, None, regatta)
            races.extend(list(data[p].keys()))
            maxVals.append(max(list(data[p].values())))
        except:
            print("Couldn't find person 👀")
    races = sorted([*set(races)], key=functools.cmp_to_key(compare))

    for p in list(names.keys()):
        print(races, data[p])
        x = sorted([indexOf(races,race) + prev for race in list(data[p].keys()) if race in races])
        y = [data[p][race] for race in races if race in data[p]]
        print(p,x, y)
        # if pData
        if x != [] and y != []:
            plt.scatter(x, y, color=names[p], alpha=0.5, zorder=1) #label=f'{p.split(" ", 1)[0]} {regatta}',
            if p not in nameLabels:
                nameLabels.append(p)
            if len(x) > 3 and Type != "Ratio":
                xnew = np.linspace(min(x), max(x), 300)  
                spl = make_interp_spline(x, y, k=3)  # type: BSpline
                ynew = spl(xnew)
                plt.plot(xnew, ynew, color=names[p], alpha=0.5, zorder=0)
                nameLabels.append("_")
            plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)), color=names[p])
            nameLabels.append("_")

    prev += len(races)
    xTicks.extend(races)

plt.xlim([-1,len(xTicks)])
if Type == "Ratio":
    plt.yticks(np.arange(0,1, 0.1))
    plt.ylim([0, 1])
else:
    plt.yticks(np.arange(0, max(maxVals) + 1, 2))
    plt.ylim([0, max(maxVals) + 1])

plt.xticks(range(len(xTicks)), xTicks, rotation=90)
plt.ylabel(Type)
plt.legend(nameLabels,loc="upper right")
plt.tight_layout()
plt.grid(True)
plt.savefig("fig.png")

# plt.show() 
