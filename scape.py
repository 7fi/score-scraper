from bs4 import BeautifulSoup
import requests
from csv import writer

url = "https://scores.hssailing.org/f22/pontiac-bay-regional-south-regional/full-scores/"

page = requests.get(url)
print(page)

soup = BeautifulSoup(page.content, 'html.parser')
header = soup.find('table', class_="results").find_all('th', class_="right")
raceCount = int(header[len(header) - 2].text)

scoreData = soup.find('table', class_="results").contents[1].contents

teamCount = int(len(scoreData) / 3)
print(teamCount)

teams = []


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


with open('scores.csv', 'w', encoding='utf8', newline='') as f:
    thewriter = writer(f)

    header = ["Team Home", "Team Name", "Team A Scores",
              "Team B Scores", "Team A Total", "Team B Total"]
    thewriter.writerow(header)
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
        # teamHome = teamAScores.find('', class_="")
        # print(teamHome, teamName, teamAScores, teamBScores, teamATotal, teamBTotal)
        thewriter.writerow([teamHome, teamName, teamAScores,
                           teamBScores, teamATotal, teamBTotal])
        teams.append(team(teamHome, teamName, teamAScores,
                          teamBScores, teamATotal, teamBTotal))

    thewriter.writerow(["Race Count: ", raceCount])
    thewriter.writerow(["Team Count: ", teamCount])

print(teams)
