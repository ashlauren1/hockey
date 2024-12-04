from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os

# Define rate limit parameters
REQUESTS_PER_MINUTE = 20
ONE_MINUTE = 60

@sleep_and_retry
@limits(calls=REQUESTS_PER_MINUTE, period=ONE_MINUTE)
def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def convert_toi_to_decimal(toi_str):
    """Convert TOI from 'mm:ss' to decimal minutes."""
    try:
        if isinstance(toi_str, str):
            minutes, seconds = map(int, toi_str.split(':'))
            return minutes + seconds / 60
        return None  # Return None for non-string values
    except ValueError:
        return None

# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\hockey\data"
leaders_columns = [
    'Player', 'PlayerID', 'Age', 'TeamID', 'Pos', 'GP', 'G', 'A', 'PTS', 'SOG', 'SPCT', 'HIT', 'BLK', 'TOI', 'PIM', 'EVG', 'PPG', 'SHG', 'EVA', 'PPA', 'SHA', 'FOW', 'FOL', 'FO%', 'G_GP', 'A_GP', 'PTS_GP', 'SOG_GP', 'HIT_GP', 'BLK_GP', 'TOI_GP'
]

# Initialize lists to collect data
leaders_data = []

url = 'https://www.hockey-reference.com/leagues/NHL_2025_skaters.html#stats::goals'

try:
    html_content = fetch_webpage(url)
    soup = BeautifulSoup(html_content, 'html.parser')

    table = soup.select_one('#player_stats')
    if table:
        headers = [th.get_text(strip=True) for th in table.select("thead tr")[1].find_all("th")]
        df = pd.read_html(StringIO(str(table)))[0]
        df.columns = headers
        df = df.iloc[:-1, :]
        
        valid_rows = [
            row for row in table.select("tbody tr")
            if not any(cls in (row.get("class") or []) for cls in ["over_header", "thead", "norank"])
            and "League Average" not in row.get_text(strip=True)
        ]

        # Rename columns and clean data
        column_mapping = {'Team': 'TeamID', 'EV': 'EVA', 'PP': 'PPA', 'SH': 'SHA'}
        df.rename(columns=column_mapping, inplace=True)

        df = df[["Player", "Age", "TeamID", "Pos", "GP", "G", "A", "PTS", "SOG", "SPCT", "HIT", "BLK", "TOI", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA", "FOW", "FOL", "FO%"]]

        df["TOI"] = df["TOI"].apply(convert_toi_to_decimal)

        # Insert player IDs
        player_ids = [row.select_one("td[data-append-csv]").get("data-append-csv") for row in valid_rows if row.select_one("td[data-append-csv]")]
        df.insert(df.columns.get_loc("Player") + 1, "PlayerID", player_ids + [None] * (len(df) - len(player_ids)))

        # Add per-game stats
        for col in ["G", "A", "PTS", "SOG", "HIT", "BLK", "TOI"]:
            df[f"{col}_GP"] = df[col] / df["GP"]
            df[f"{col}_GP"] = df[f"{col}_GP"].fillna(0)

        df = df.reindex(columns=leaders_columns, fill_value=None)
        leaders_data.append(df)

    time.sleep(3)  # Avoid rate limits

except requests.RequestException as e:
    print(f"Error fetching data: {e}")
except Exception as e:
    print(f"Error processing data: {e}")

# Process leaders_data
if not leaders_data:
    print("No leader data was extracted. Ensure the table exists and the HTML structure is correct.")
else:
    leaders_df = pd.concat(leaders_data, ignore_index=True)
    leaders_df["TeamID"] = leaders_df["TeamID"].replace("UTA", "ARI")
    
    player_info = {
        "necasma01": ("Martin Necas"),
        "stuetti02": ("Tim Stutzle"),
        "kopitan01": ("Anze Kopitar"),
        "pastrda01": ("David Pastrnak"),
        "hertlto01": ("Tomas Hertl"),
        "lafreal01": ("Alexis Lafreniere"),
        "gaudrfr01": ("Frederick Gaudreau"),
        "holmssi01": ("Simon Holmstrom"),
        "teravte01": ("Teuvo Teravainen"),
        "burakan01": ("Andre Burakovsky"),
        "tatarto01": ("Tomas Tatar"),
        "palaton01": ("Ondrej Palat"),
        "puljuje01": ("Jesse Puljujarvi"),
        "branner01": ("Erik Brannstrom"),
        "vranaja01": ("Jakub Vrana"),
        "cernaer01": ("Erik Cernak"),
        "feherma01": ("Martin Fehervary"),
        "hoglani01": ("Nils Hoglander"),
        "lundeis01": ("Isac Lundestrom"),
        "parssju01": ("Juuso Parssinen"),
        "grundca01": ("Carl Grundstrom"),
        "kampfda01": ("David Kampf"),
        "nosekto01": ("Tomas Nosek"),
        "ratyaa01": ("Aatu Raty"),
        "amanni01": ("Nils Aman"),
        "maattol01": ("Olli Maatta"),
        "aubekni01": ("Nicolas Aube-Kubel"),
        "jiricda01": ("David Jiricek"),
        "valimju01": ("Juuso Valimaki"),
        "vanecvi01": ("Vitek Vanecek"),
        "vladada01": ("Daniel Vladar"),
        "barreal01": ("Alex Barre-Boulet"),
        "blumema01": ("Matej Blumel"),
        "dostalu01": ("Lukas Dostal"),
        "fleurma01": ("Marc-Andre Fleury"),
        "haggro01": ("Robert Hagg"),
        "hakanja01": ("Jani Hakanpaa"),
        "kahkoka01": ("Kaapo Kahkonen"),
        "marksja02": ("Jacob Markstrom"),
        "merzlel01": ("Elvis Merzlikins"),
        "mrazepe01": ("Petr Mrazek"),
        "rondbjo01": ("Jonas Rondbjerg"),
        "soderar01": ("Arvid Soderblom"),
        "sogaama01": ("Mads Sogaard"),
        "vlasima01": ("Marc-Edouard Vlasic"),
        "yloneje01": ("Jesse Ylonen"),
        "sodervi01": ("Victor Soderstrom"),
        "backsni02": ("Nicklas Backstrom"),
        "dubedi01": ("Dillon Dube"),
        "harvera01": ("Rafael Harvey-Pinard"),
        "jarnkca01": ("Calle Jarnkrok"),
        "jenikja01": ("Jan Jenik"),
        "jonssax01": ("Axel Jonsson-Fjallby"),
        "kelemmi01": ("Milos Kelemen"),
        "rosenca01": ("Calle Rosen"),
        "rouselu01": ("Lukas Rousek")
    }
    
    leaders_df["Player"] = leaders_df["PlayerID"].map(player_info).fillna(leaders_df["Player"])

    # Save to CSV
    leaders_path = os.path.join(base_path, "leaders.csv")
    leaders_df.to_csv(leaders_path, index=False, encoding="utf-8")
    print(f"Leaders saved to {leaders_path}")
    

goalie_columns = [
    'Player', 'PlayerID', 'Age', 'TeamID', 'GP', 'GS', 'W', 'L', 'OTL', 'GA', 'SA', 'SV', 'SV%', 'GAA', 'SO'
]

# Initialize lists to collect data
goalie_data = []

url = 'https://www.hockey-reference.com/leagues/NHL_2025_goalies.html#stats::games_goalie'

try:
    html_content = fetch_webpage(url)
    soup = BeautifulSoup(html_content, 'html.parser')

    table = soup.select_one('#goalie_stats')
    if table:
        headers = [th.get_text(strip=True) for th in table.select("thead tr")[1].find_all("th")]
        df = pd.read_html(StringIO(str(table)))[0]
        df.columns = headers
        df = df.iloc[:-1, :]
        
        valid_rows = [
            row for row in table.select("tbody tr")
            if not any(cls in (row.get("class") or []) for cls in ["over_header", "thead", "norank"])
            and "League Average" not in row.get_text(strip=True)
        ]

        # Rename columns and clean data
        column_mapping = {'Team': 'TeamID', 'T/O': 'OTL', 'Shots': 'SA'}
        df.rename(columns=column_mapping, inplace=True)

        df = df[['Player', 'Age', 'TeamID', 'GP', 'GS', 'W', 'L', 'OTL', 'GA', 'SA', 'SV', 'SV%', 'GAA', 'SO']]

        # Insert player IDs
        player_ids = [row.select_one("td[data-append-csv]").get("data-append-csv") for row in valid_rows if row.select_one("td[data-append-csv]")]
        df.insert(df.columns.get_loc("Player") + 1, "PlayerID", player_ids + [None] * (len(df) - len(player_ids)))

        df = df.reindex(columns=goalie_columns, fill_value=None)
        goalie_data.append(df)

    time.sleep(3)  # Avoid rate limits

except requests.RequestException as e:
    print(f"Error fetching data: {e}")
except Exception as e:
    print(f"Error processing data: {e}")

if not goalie_data:
    print("No goalie data was extracted. Ensure the table exists and the HTML structure is correct.")
else:
    goalie_df = pd.concat(goalie_data, ignore_index=True)
    goalie_df["TeamID"] = goalie_df["TeamID"].replace("UTA", "ARI")
    
    player_info = {
        "necasma01": ("Martin Necas"),
        "stuetti02": ("Tim Stutzle"),
        "kopitan01": ("Anze Kopitar"),
        "pastrda01": ("David Pastrnak"),
        "hertlto01": ("Tomas Hertl"),
        "lafreal01": ("Alexis Lafreniere"),
        "gaudrfr01": ("Frederick Gaudreau"),
        "holmssi01": ("Simon Holmstrom"),
        "teravte01": ("Teuvo Teravainen"),
        "burakan01": ("Andre Burakovsky"),
        "tatarto01": ("Tomas Tatar"),
        "palaton01": ("Ondrej Palat"),
        "puljuje01": ("Jesse Puljujarvi"),
        "branner01": ("Erik Brannstrom"),
        "vranaja01": ("Jakub Vrana"),
        "cernaer01": ("Erik Cernak"),
        "feherma01": ("Martin Fehervary"),
        "hoglani01": ("Nils Hoglander"),
        "lundeis01": ("Isac Lundestrom"),
        "parssju01": ("Juuso Parssinen"),
        "grundca01": ("Carl Grundstrom"),
        "kampfda01": ("David Kampf"),
        "nosekto01": ("Tomas Nosek"),
        "ratyaa01": ("Aatu Raty"),
        "amanni01": ("Nils Aman"),
        "maattol01": ("Olli Maatta"),
        "aubekni01": ("Nicolas Aube-Kubel"),
        "jiricda01": ("David Jiricek"),
        "valimju01": ("Juuso Valimaki"),
        "vanecvi01": ("Vitek Vanecek"),
        "vladada01": ("Daniel Vladar"),
        "barreal01": ("Alex Barre-Boulet"),
        "blumema01": ("Matej Blumel"),
        "dostalu01": ("Lukas Dostal"),
        "fleurma01": ("Marc-Andre Fleury"),
        "haggro01": ("Robert Hagg"),
        "hakanja01": ("Jani Hakanpaa"),
        "kahkoka01": ("Kaapo Kahkonen"),
        "marksja02": ("Jacob Markstrom"),
        "merzlel01": ("Elvis Merzlikins"),
        "mrazepe01": ("Petr Mrazek"),
        "rondbjo01": ("Jonas Rondbjerg"),
        "soderar01": ("Arvid Soderblom"),
        "sogaama01": ("Mads Sogaard"),
        "vlasima01": ("Marc-Edouard Vlasic"),
        "yloneje01": ("Jesse Ylonen"),
        "sodervi01": ("Victor Soderstrom"),
        "backsni02": ("Nicklas Backstrom"),
        "dubedi01": ("Dillon Dube"),
        "harvera01": ("Rafael Harvey-Pinard"),
        "jarnkca01": ("Calle Jarnkrok"),
        "jenikja01": ("Jan Jenik"),
        "jonssax01": ("Axel Jonsson-Fjallby"),
        "kelemmi01": ("Milos Kelemen"),
        "rosenca01": ("Calle Rosen"),
        "rouselu01": ("Lukas Rousek")
    }
    
    goalie_df["Player"] = goalie_df["PlayerID"].map(player_info).fillna(goalie_df["Player"])

    # Save to CSV
    goalie_path = os.path.join(base_path, "goalies.csv")
    goalie_df.to_csv(goalie_path, index=False, encoding="utf-8")
    print(f"Goalies saved to {goalie_path}")