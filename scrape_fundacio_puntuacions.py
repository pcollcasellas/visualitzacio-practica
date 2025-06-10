import pandas as pd
from bs4 import BeautifulSoup
import re
import requests


def scrape_colles_actuals():
    url = "https://ca.wikipedia.org/wiki/Llista_de_colles_castelleres#Colles_castelleres_actuals"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    h2 = soup.find("h2", id="Colles_castelleres_actuals")
    if not h2:
        h2 = soup.find(lambda tag: tag.name == "h2" and "Colles castelleres actuals" in tag.text)
    if not h2:
        print("Section not found")
        return

    table = h2.find_next("table", class_="wikitable")
    if not table:
        print("Table not found")
        return

    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    try:
        nom_idx = headers.index("Nom")
        fundacio_idx = headers.index("Fundació")
    except ValueError:
        print("Required columns not found")
        return

    data = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all(["td", "th"])
        if len(cells) < max(nom_idx, fundacio_idx) + 1:
            continue
        nom = cells[nom_idx].get_text(strip=True)
        fundacio_cell = cells[fundacio_idx].get_text(strip=True)
        fundacio_cell = re.sub(r"\[.*?\]", "", fundacio_cell).strip()
        years = [int(x) for x in re.findall(r"\d{4}", fundacio_cell)]
        fundacio = max(years) if years else fundacio_cell
        # Map specific 'Nom' values to match another dataframe
        nom_map = {
            "Colla Castellera de Sant Pere i Sant Pau": "Colla Castellera Sant Pere i Sant Pau",
            "Colla de Castellers d'Esplugues": "Castellers d'Esplugues",
            "Encantats de Begues": "Colla Castellera Els Encantats de Begues",
            "Carallots de Sant Vicenç dels Horts": "Castellers de Sant Vicenç dels Horts",
            "Minyons de Santa Cristina": "Minyons de Santa Cristina d'Aro",
            "Castellers de l'Alt Maresme": "Colla Castellera de l'Alt Maresme i la Selva Marítima",
        }
        nom = nom_map.get(nom, nom)
        data.append({"Nom": nom, "Fundació": fundacio})

    df = pd.DataFrame(data)
    df.sort_values("Nom").to_csv("colles_actuals.csv", index=False, encoding="utf-8")
    print("Saved to colles_actuals.csv")


def scrape_puntuacions():
    url = "http://www.portalcasteller.cat/v2/taula-de-puntuacions/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table")
    if len(tables) < 2:
        print("No s'han trobat dues taules")
        return

    all_rows = []
    for table in tables[:2]:
        for row in table.find_all("tr")[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 3:
                continue
            castell = cells[0].get_text(strip=True)
            if castell == "Castell":
                continue
            descarregat = cells[1].get_text(strip=True)
            carregat = cells[2].get_text(strip=True)
            all_rows.append({"Castell": castell, "Descarregat": descarregat, "Carregat": carregat})

    df = pd.DataFrame(all_rows)
    df["Castell"] = df["Castell"].str.replace("d", "de", regex=False)
    df["Castell"] = df["Castell"].str.replace("af", "fp", regex=False)
    df["Castell"] = df["Castell"].str.replace(r"(?<=\d)a$", "p", regex=True)
    df["Castell"] = df["Castell"].str.replace(r"ps$", "s", regex=True)

    df.to_csv("puntuacions.csv", index=False, encoding="utf-8")
    print("Desat a puntuacions.csv")


def main():
    scrape_colles_actuals()
    scrape_puntuacions()


if __name__ == "__main__":
    main()
