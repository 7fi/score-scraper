from bs4 import BeautifulSoup
import requests
from csv import writer

regatta_names = ["pontiac-bay-regional-south-regional",
                 "nwisa-girls-qualifiers"]

printFormat = False


class team:
    def __init__(self, home, name, aScores, bScores, aTotal, bTotal):
        self.home = home
        self.name = name
        self.aScores = aScores
        self.bScores = bScores
        self.aTotal = aTotal
        self.bTotal = bTotal

    def __repr__(self):
        return f"{self.home} {self.name} {self.aScores} {self.bScores} {self.aTotal} {self.bTotal}"


for regatta in regatta_names:

    # full scores
    url = f"https://scores.hssailing.org/f22/{regatta}/full-scores/"
    page = requests.get(url)
    fullScores = BeautifulSoup(page.content, 'html.parser')

    # sailors
    url = f"https://scores.hssailing.org/f22/{regatta}/sailors/"
    page = requests.get(url)
    sailors = BeautifulSoup(page.content, 'html.parser')

    scoreData = fullScores.find('table', class_="results").contents[1].contents
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
                      "Team B Scores", "Team A Total", "Team B Total"]
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

            teamAskippers = []
            # for teamName in sailors.find('table', class_="sailors").find_all('td', class_="teamname"):
            #     print(f"{teamName}found")

            for sibling in sailors.find('table', class_="sailors").find('td', class_="teamname").next_siblings:
                if not sibling.has_attr('class'):
                    print(repr(sibling.text.split(" '")[0]))
                elif sibling['class'] == "races":
                    print(repr(sibling.text.split("-")))
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
                    [teamHome, teamName, ', '.join(map(str, teamAScores)), ', '.join(map(str, teamBScores)), teamATotal, teamBTotal])
            teams.append(team(teamHome, teamName, teamAScores,
                              teamBScores, teamATotal, teamBTotal))

        if printFormat:
            thewriter.writerow(["Race Count: ", raceCount])
            thewriter.writerow(["Team Count: ", teamCount])

    # print(teams)
