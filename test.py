import requests
from bs4 import BeautifulSoup


def printGrid(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    if table is None:
        return

    rows = table.find_all("tr")

    points = []

    maxX = 0
    maxY = 0

    for i in range(1, len(rows)):
        cols = rows[i].find_all("td")

        if len(cols) != 3:
            continue

        x = int(cols[0].get_text(strip=True))
        ch = cols[1].get_text(strip=True)
        y = int(cols[2].get_text(strip=True))

        points.append((x, y, ch))

        if x > maxX:
            maxX = x
        if y > maxY:
            maxY = y

    grid = []

    for i in range(maxY + 1):
        row = []
        for j in range(maxX + 1):
            row.append(" ")
        grid.append(row)

    for x, y, ch in points:
        grid[y][x] = ch

    for i in range(maxY, -1, -1):
        print("".join(grid[i]))


url = input()
printGrid(url)
