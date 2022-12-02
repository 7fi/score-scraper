from operator import indexOf
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import functools

regatta_names = ["nwisa-girls-qualifiers", "cascadia-cup-gold", "2022-issa-pcisa-all-girls-invitational",
                 "pontiac-bay-regional-south-regional", "fall-champs", "2022-atlantic-coast"]
better_names = ["girls quals", "cascadia gold", "PCISA girls",
                "south regional", "fall champs", "ACCs"]
# regatta_names = ["nwisa-girls-qualifiers"]
# better_names = ["girls quals"]


class person:
    def __init__(self, name, team, races):
        self.name = name
        self.team = team
        self.races = races
        # self.raceNums = []
            # print(self.races)

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

people = []

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
    if type == "raw":
        return next([race.score for race in p.races]
                    for p in people if p.name == name)
    if type == "points":
        data = {}
        for p in people:
            if p.name == name:
                # racenum = 0
                for r in p.races:
                    # print(r.score)
                    if r.venue == regatta:
                        data[f"{regatta} {r.division}{r.number}"] = r.score
                    # data[f"{regatta} race {r.number}"] = len(
                    #     r.teams) - r.score + 1
                    # racenum++
        return data

        return next([(len(race.teams) - race.score + 1) for race in p.races]
                    for p in people if p.name == name)


def getVenues(name):
    return next([race.venue for race in p.races]for p in people if p.name == name)


def getDataByVenue(name, rregatta):
    return next([(len(race.teams) - race.score + 1) for race in p.races if race.venue == rregatta]
                for p in people if p.name == name)

for i, regatta in enumerate(regatta_names):
    betterVenue = better_names[i]
    print(f"({i + 1}/{len(regatta_names)})analyzing {betterVenue}")
    # full scores
    url = f"https://scores.hssailing.org/f22/{regatta}/full-scores/"
    page = requests.get(url)
    fullScores = BeautifulSoup(page.content, 'html.parser')

    # sailors a
    url = f"https://scores.hssailing.org/f22/{regatta}/sailors/"
    page = requests.get(url)
    sailors = BeautifulSoup(page.content, 'html.parser')

    # A
    url = f"https://scores.hssailing.org/f22/{regatta}/A/"
    page = requests.get(url)
    a = BeautifulSoup(page.content, 'html.parser')

    # B
    url = f"https://scores.hssailing.org/f22/{regatta}/B/"
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

    teams = []

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

        allNames = a.find_all('td', class_="teamname")
        teamNameEl = [i for i in allNames if i.text == teamName][0]

        for skipper in teamNameEl.parent.previous_sibling.find_all('td', class_="skipper"):
            if skipper.parent.previous_sibling and skipper.parent.previous_sibling.find_all('td', class_="skipper"):
                skipper2 = skipper.parent.previous_sibling.find(
                    'td', class_="skipper")
                raceNums = skipper2.next_sibling.text.split(",")
                raceNums = [i.split("-", 1) for i in raceNums]
                addPerson(skipper2.text.split(" '")[0],"Skipper", 'A', teamHome, raceNums, teamAScores, teamHomes, betterVenue)
            raceNums = skipper.next_sibling.text.split(",")
            raceNums = [i.split("-", 1) for i in raceNums]
            addPerson(skipper.text.split(" '")[0],"Skipper",'A', teamHome, raceNums, teamAScores, teamHomes, betterVenue)
            # teamASkippers.append(
            #     person(skipper.text.split(" '")[0], "skipper", raceNums, races))

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

        allNames = b.find_all('td', class_="teamname")
        teamNameEl = [i for i in allNames if i.text == teamName][0]

        for skipper in teamNameEl.parent.previous_sibling.find_all('td', class_="skipper"):
            if skipper.parent.previous_sibling and skipper.parent.previous_sibling.find_all('td', class_="skipper"):
                skipper2 = skipper.parent.previous_sibling.find(
                    'td', class_="skipper")
                races = skipper2.next_sibling.text.split(",")
                races = [i.split("-", 1) for i in races]
                addPerson(skipper2.text.split(" '")[0],"Skipper",'B', teamHome, races, teamBScores, teamHomes, betterVenue)
            races = skipper.next_sibling.text.split(",")
            races = [i.split("-", 1) for i in races]
            addPerson(skipper.text.split(" '")[0],"Skipper",'B', teamHome, races, teamBScores, teamHomes, betterVenue)

        for crew in teamNameEl.parent.find_all('td', class_="crew"):
            races = crew.next_sibling.text.split(",")
            races = [i.split("-", 1) for i in races]
            addPerson(crew.text.split(" '")[0],"Crew",'B', teamHome, races, teamAScores, teamHomes, betterVenue)
            if crew.parent.next_sibling and crew.parent.next_sibling.find_all('td', class_="crew"):
                crew2 = crew.parent.next_sibling.find(
                    'td', class_="crew")
                races = crew2.next_sibling.text.split(",")
                races = [i.split("-", 1) for i in races]
                addPerson(crew2.text.split(" '")[0],"Crew",'B', teamHome, races, teamBScores, teamHomes, betterVenue)

                if crew2.parent.next_sibling and crew2.parent.next_sibling.find_all('td', class_="crew"):
                    crew3 = crew2.parent.next_sibling.find(
                        'td', class_="crew")
                    races = crew3.next_sibling.text.split(",")
                    races = [i.split("-", 1) for i in races]
                    addPerson(crew3.text.split(" '")[0],"Crew",'B', teamHome, races, teamBScores, teamHomes, betterVenue)

def compare(first, second):
    # print("First", first, "Second", second)
    #B > A
    if first[len(first) - 1] > second[len(second) - 1]:
        # print("putting ahead #")
        return 1
    if first[len(first) - 1] < second[len(second) - 1]:
        # print("putting behind #")
        return - 1
    if first[len(first) - 2] > second[len(second) - 2]:
        # print("putting ahead L")
        return 1
    if first[len(first) - 2] < second[len(second) - 2]:
        # print("putting behind L")
        return - 1
    else:
        return 0

names = {"Elliott Chalcraft": "#e0570d", 'Carter Anderson':"#3684a3"}
Type = "points"

prev = 0
xTicks = []
pData = {}
for regatta in better_names:
    data = {}
    races = []
    for p in list(names.keys()):
        try:
            data[p] = getData(Type, p, None, None, None, None, regatta)
        except:
            print("Couldn't find person 👀")
        races.extend(list(data[p].keys()))
    races = sorted([*set(races)], key=functools.cmp_to_key(compare))

    # list out x values tied with race names
    # attach same x value to next person if same name
    # graph each person with new x values

    for p in list(names.keys()):
        print(races)
        x = [indexOf(races,race) + prev for race in list(data[p].keys()) if race in races]
        y = [data[p][race] for race in races if race in data[p]]
        print(x, y)
        # if pData.get(p) == None:
        #     pData[p] = []
        # pData[p].extend(y)
        plt.scatter(x, y, label=f'{p.split(" ", 1)[0]} {regatta}', color=names[p])

    # prev += int(max([len(x) for x in data]) / 2)
    prev += len(races)
    xTicks.extend(races)

# for p in names:
#     plt.scatter(range(len(pData[p])), pData[p], label=f'{p.split(" ", 1)[0]} {regatta}')

# plt.xticks 
plt.xticks(range(len(xTicks)), xTicks, rotation=90)
# plt.ylabel("Points (Higher is better)")
# plt.figure(figsize=(20, 5))
plt.legend(list(names.keys()),loc="upper right")
plt.tight_layout()
plt.grid(True)
plt.subplots_adjust(bottom=0.25)
plt.savefig("fig.png")

plt.show()