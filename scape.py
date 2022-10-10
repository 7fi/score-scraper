from itertools import tee
from bs4 import BeautifulSoup
import requests
from csv import writer

# "nwisa-girls-qualifiers"
regatta_names = ["pontiac-bay-regional-south-regional"]

printFormat = False


class team:
    def __init__(self, home, name, aScores, bScores, aSailors, bSailors, aTotal, bTotal):
        self.home = home
        self.name = name
        self.aScores = aScores
        self.bScores = bScores
        self.aSailors = aSailors
        self.bSailors = bSailors
        self.aTotal = aTotal
        self.bTotal = bTotal

    def __repr__(self):
        return f"{self.home} {self.name} {self.aScores} {self.bScores} {self.aSailors} {self.bSailors} {self.aTotal} {self.bTotal}"


class person:
    def __init__(self, name, position, races):
        self.name = name
        self.pos = position
        self.races = []

        if len(races) != 0:
            for i in range(len(races)):
                if len(races[i]) > 1:
                    for j in range(int(races[i][0]), int(races[i][1]) + 1):
                        self.races.append(j)
                else:
                    self.races.append(int(races[i][0]))
        # print(self.races)

    def __repr__(self):
        return f"{self.name} {self.races}"


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
    print(teamCount)

    teams = []

    with open(f'{regatta}-scores.csv', 'w', encoding='utf8', newline='') as f:
        # CSV Stuff
        thewriter = writer(f)
        if printFormat:
            header = ["Team", "Div", "Scores", "Total"]
        else:
            header = ["Team Home", "Team Name", "Team A Scores",
                      "Team B Scores", "Team A Sailors", "Team B Sailors", "Team A Total", "Team B Total"]
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

            teamASailors = []
            teamBSailors = []
            # for teamName in sailors.find('table', class_="sailors").find_all('td', class_="teamname"):
            #     print(f"{teamName}found")

            bruh = sailors.find_all('td', class_="teamname")
            nameEl = [i for i in bruh if i.text == teamName][0]
            # print(nameEl)

            bStartPoint = None
            for sibling in nameEl.next_sibling.next_elements:
                # print(str(type(sibling)) == "<class 'bs4.element.Tag'>")
                if str(type(sibling)) == "<class 'bs4.element.Tag'>" and sibling.has_attr('class') and sibling['class'] == ["division-cell"]:
                    bStartPoint = sibling
                    break
                if str(type(sibling)) == "<class 'bs4.element.Tag'>" and sibling.has_attr('class') and sibling['class'] == ["races"]:
                    name = repr(sibling.previous_sibling.text.split(" '")[0])
                    if sibling.parent.contents[4] == sibling:
                        pos = "Skipper"

                    races = sibling.text.split(",")
                    races = [i.split("-", 1) for i in races]
                    teamASailors.append(person(name, pos, races))

            # print(teamASailors)

            for sibling in bStartPoint.next_elements:
                # print(str(type(sibling)) == "<class 'bs4.element.Tag'>")
                if str(type(sibling)) == "<class 'bs4.element.Tag'>" and sibling.has_attr('class') and sibling['class'] == ["schoolname"]:
                    break
                if str(type(sibling)) == "<class 'bs4.element.Tag'>" and sibling.has_attr('class') and sibling['class'] == ["races"]:
                    name = repr(sibling.previous_sibling.text.split(" '")[0])
                    races = sibling.text.split(",")
                    races = [i.split("-", 1) for i in races]
                    teamBSailors.append(person(name, races))

            # print(teamBSailors)

            # print(sailors.find(
            #     'td', class_="races").previous_sibling.text.split(" '")[0],
            #     sailors.find(
            #     'td', class_="races").text.split(",")
            # )

            # print(sailors.find('table', class_="sailors").find('td', class_="teamname").next_sibling.next_sibling.next_sibling.text.split(" '")[0])

            # print(teamHome, teamName, teamAScores, teamBScores, teamATotal, teamBTotal)

            if printFormat:
                thewriter.writerow([teamHome, "A", ', '.join(
                    map(str, teamAScores)), teamATotal])
                thewriter.writerow([teamName, "B", ', '.join(
                    map(str, teamBScores)), teamBTotal])
                thewriter.writerow([])
            else:
                thewriter.writerow(
                    [teamHome, teamName, ', '.join(map(str, teamAScores)), ', '.join(map(str, teamBScores)), ', '.join(map(str, teamASailors)), ', '.join(map(str, teamBSailors)), teamATotal, teamBTotal])
            teams.append(team(teamHome, teamName, teamAScores,
                              teamBScores, teamASailors, teamBSailors, teamATotal, teamBTotal))

        if printFormat:
            thewriter.writerow(["Race Count: ", raceCount])
            thewriter.writerow(["Team Count: ", teamCount])

    print(teams)
