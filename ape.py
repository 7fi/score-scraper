from csv import writer
import csv
# from itertools import tee
from bs4 import BeautifulSoup
import requests
import numpy as np
import matplotlib.pyplot as plt

regatta_names = ["cascadia-cup-gold", "cascadia-cup-silver", "2022-issa-pcisa-all-girls-invitational", "nwisa-girls-qualifiers",
                 "pontiac-bay-regional-south-regional", "north-regionals"]
# regatta_names = ["2022-atlantic-coast"]

printFormat = False


class team:
    def __init__(self, home, name, aScores, bScores, aSkippers, bSkippers, aCrews, bCrews, aTotal, bTotal):
        self.home = home
        self.name = name
        self.aScores = aScores
        self.bScores = bScores
        self.aSkippers = aSkippers
        self.bSkippers = bSkippers
        self.aCrews = aCrews
        self.bCrews = bCrews
        self.aTotal = aTotal
        self.bTotal = bTotal

    def __repr__(self):
        return f"{self.home} {self.name} {self.aScores} {self.bScores} {self.aSkippers} {self.bSkippers} {self.aCrews} {self.bCrews} {self.aTotal} {self.bTotal}"


class person:
    def __init__(self, name, position, races):
        self.name = name
        self.pos = position
        self.races = []

        if races != [['']] and len(races) != 0:
            for i in range(len(races)):
                if len(races[i]) > 1:
                    for j in range(int(races[i][0]), int(races[i][1]) + 1):
                        self.races.append(j)
                else:
                    self.races.append(int(races[i][0]))
            # print(self.races)

    def __repr__(self):
        return f"{self.name}{self.races}"


for regatta in regatta_names:

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
    # print(teamCount)

    teams = []

    with open(f'{regatta}-scores.csv', 'w', encoding='utf8', newline='') as f:
        # CSV Stuff
        thewriter = writer(f)
        if printFormat:
            header = ["Team", "Div", "Scores", "Skippers", "Crews", "Total"]
        else:
            header = ["Team Home", "Team Name", "Team A Scores",
                      "Team B Scores", "Team A Skippers", "Team A Crews", "Team B Skippers", "Team B Crews", "Team A Total", "Team B Total"]
        thewriter.writerow(header)

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
                    races = skipper2.next_sibling.text.split(",")
                    races = [i.split("-", 1) for i in races]
                    teamASkippers.append(
                        person(skipper2.text.split(" '")[0], "skipper", races))
                races = skipper.next_sibling.text.split(",")
                races = [i.split("-", 1) for i in races]
                teamASkippers.append(
                    person(skipper.text.split(" '")[0], "skipper", races))

            for crew in teamNameEl.parent.find_all('td', class_="crew"):
                races = crew.next_sibling.text.split(",")
                races = [i.split("-", 1) for i in races]
                teamACrews.append(
                    person(crew.text.split(" '")[0], "crew", races))
                if crew.parent.next_sibling and crew.parent.next_sibling.find_all('td', class_="crew"):
                    crew2 = crew.parent.next_sibling.find(
                        'td', class_="crew")
                    races = crew2.next_sibling.text.split(",")
                    races = [i.split("-", 1) for i in races]
                    teamACrews.append(
                        person(crew2.text.split(" '")[0], "crew", races))
                    if crew2.parent.next_sibling and crew2.parent.next_sibling.find_all('td', class_="crew"):
                        crew3 = crew2.parent.next_sibling.find(
                            'td', class_="crew")
                        races = crew3.next_sibling.text.split(",")
                        races = [i.split("-", 1) for i in races]
                        teamACrews.append(
                            person(crew3.text.split(" '")[0], "crew", races))

            allNames = b.find_all('td', class_="teamname")
            teamNameEl = [i for i in allNames if i.text == teamName][0]

            for skipper in teamNameEl.parent.previous_sibling.find_all('td', class_="skipper"):
                if skipper.parent.previous_sibling and skipper.parent.previous_sibling.find_all('td', class_="skipper"):
                    skipper2 = skipper.parent.previous_sibling.find(
                        'td', class_="skipper")
                    races = skipper2.next_sibling.text.split(",")
                    races = [i.split("-", 1) for i in races]
                    teamBSkippers.append(
                        person(skipper2.text.split(" '")[0], "skipper", races))
                races = skipper.next_sibling.text.split(",")
                races = [i.split("-", 1) for i in races]
                teamBSkippers.append(
                    person(skipper.text.split(" '")[0], "skipper", races))

            for crew in teamNameEl.parent.find_all('td', class_="crew"):
                races = crew.next_sibling.text.split(",")
                races = [i.split("-", 1) for i in races]
                teamBCrews.append(
                    person(crew.text.split(" '")[0], "crew", races))
                if crew.parent.next_sibling and crew.parent.next_sibling.find_all('td', class_="crew"):
                    crew2 = crew.parent.next_sibling.find(
                        'td', class_="crew")
                    races = crew2.next_sibling.text.split(",")
                    races = [i.split("-", 1) for i in races]
                    teamBCrews.append(
                        person(crew2.text.split(" '")[0], "crew", races))
                    if crew2.parent.next_sibling and crew2.parent.next_sibling.find_all('td', class_="crew"):
                        crew3 = crew2.parent.next_sibling.find(
                            'td', class_="crew")
                        races = crew3.next_sibling.text.split(",")
                        races = [i.split("-", 1) for i in races]
                        teamBCrews.append(
                            person(crew3.text.split(" '")[0], "crew", races))

            if printFormat:
                thewriter.writerow([teamHome, "A", ', '.join(
                    map(str, teamAScores)), ', '.join(
                    map(str, teamASkippers)), ', '.join(
                    map(str, teamACrews)), teamATotal])
                thewriter.writerow([teamName, "B", ', '.join(
                    map(str, teamBScores)), ', '.join(
                    map(str, teamBSkippers)), ', '.join(
                    map(str, teamBCrews)), teamBTotal])
                thewriter.writerow([None])
            else:
                thewriter.writerow(
                    [teamHome, teamName, ', '.join(map(str, teamAScores)), ', '.join(map(str, teamBScores)), ', '.join(map(str, teamASkippers)), ', '.join(map(str, teamACrews)), ', '.join(map(str, teamBSkippers)), ', '.join(map(str, teamBCrews)), teamATotal, teamBTotal])
            teams.append(team(teamHome, teamName, teamAScores,
                              teamBScores, teamASkippers, teamBSkippers, teamACrews, teamBCrews, teamATotal, teamBTotal))

        if printFormat:
            thewriter.writerow(["Race Count: ", raceCount])
            thewriter.writerow(["Team Count: ", teamCount])
