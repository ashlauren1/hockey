from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random


# Define Chrome options
chrome_options = Options()
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-webgl')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

# Initialize WebDriver
service = Service(r"C:\Users\ashle\AppData\Local\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)


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
        minutes, seconds = map(int, toi_str.split(':'))
        return minutes + seconds / 60
    except ValueError:
        return None

def extract_date_from_game_id(game_id):
    date_str = game_id[:8]
    return datetime.strptime(date_str, "%Y%m%d").strftime("%m/%d/%Y")


# Define the game IDs, home teams, and away teams
games_info = {
    "202412010DET": ("DET", "VAN"),
    "202412010BOS": ("BOS", "MTL"),
    "202412010CHI": ("CHI", "CBJ"),
    "202412010DAL": ("DAL", "WPG"),
    "202412010ANA": ("ANA", "OTT"),
    "202412020NYR": ("NYR", "NJD"),
    "202412020TOR": ("TOR", "CHI"),
    "202412020UTA": ("UTA", "DAL"),
    "202412030BOS": ("BOS", "DET"),
    "202412030BUF": ("BUF", "COL"),
    "202412030MTL": ("MTL", "NYI"),
    "202412030PIT": ("PIT", "FLA"),
    "202412030WSH": ("WSH", "SJS"),
    "202412030CAR": ("CAR", "SEA"),
    "202412030MIN": ("MIN", "VAN"),
    "202412030WPG": ("WPG", "STL"),
    "202412030CGY": ("CGY", "CBJ"),
    "202412030VEG": ("VEG", "EDM")
}

# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\hockey"
data_path = r"C:\Users\ashle\Documents\Projects\hockey\data"

skaters_columns = [
    "Season", "Gm#", "Game", "GameID", "Date", "Player", "PlayerID", "Team", "TeamName", "Is_Home", "Opp", "OppName", "G", "A", "PTS", "SOG", "TOI", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA"
]

# Initialize lists to collect data
skaters_data = []
adv_skaters_data = []

for game_id, (home_team, away_team) in games_info.items():
    url = f"https://www.hockey-reference.com/boxscores/{game_id}.html"

    try:
        print(f"Processing game ID {game_id} - Home Team: {home_team}, Away Team: {away_team}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get full team names
        home_team_section = soup.select_one(f"#{home_team}_skaters_sh")
        away_team_section = soup.select_one(f"#{away_team}_skaters_sh")
        home_team_name = home_team_section.find("h2").get_text(strip=True) if home_team_section else "Unknown"
        away_team_name = away_team_section.find("h2").get_text(strip=True) if away_team_section else "Unknown"

        # Extract skaters table
        for team, team_name, is_home in [
            (home_team, home_team_name, True),
            (away_team, away_team_name, False),
        ]:
            table_selector = f"#{team}_skaters"
            table = soup.select_one(table_selector)
            if table:
                # Extract the correct header row (second row in the <thead>)
                header_row = table.select("thead tr")[1]
                headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

                # Read the table and set the headers
                df = pd.read_html(StringIO(str(table)), encoding="utf-8")[0]
                df.columns = headers
                
                # Fix encoding issues in player names
                df["Player"] = df["Player"].str.encode('latin1').str.decode('utf-8', errors='ignore')

                df = df.iloc[:table.select("tbody tr").__len__()]

                column_mapping = {
                    "S": "SOG", 
                    "EV": ["EVG", "EVA"],  # Two EV columns
                    "PP": ["PPG", "PPA"],  # Two PP columns
                    "SH": ["SHG", "SHA"],  # Two SH columns
                }
                
                column_names = list(df.columns)
                for i, col in enumerate(column_names):
                    if col == "EV":
                        column_names[i] = column_mapping["EV"].pop(0)
                    elif col == "PP":
                        column_names[i] = column_mapping["PP"].pop(0)
                    elif col == "SH":
                        column_names[i] = column_mapping["SH"].pop(0)
                    elif col == "S":
                        column_names[i] = column_mapping["S"]
                df.columns = column_names
                
                df = df[["Rk", "Player", "G", "A", "PTS", "SOG", "TOI", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA"]]
                
                if "TOI" in df.columns:
                    df["TOI"] = df["TOI"].apply(convert_toi_to_decimal)

                # Insert metadata columns              
                df.insert(0, "Season", "2024-25")
                df.insert(1, "Game", f"{home_team} vs {away_team}")
                df.insert(2, "GameID", game_id)
                df.insert(3, "Date", extract_date_from_game_id(game_id))     
                
                # Extract Player IDs from 'data-append-csv' attribute in <td> tags
                player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr td[data-append-csv]")]
                df.insert(df.columns.get_loc("Player") + 1, "PlayerID", player_ids + [None] * (len(df) - len(player_ids)))
                df.insert(df.columns.get_loc("Player") + 2, "Team", home_team if is_home else away_team)
                df.insert(df.columns.get_loc("Player") + 3, "TeamName", home_team_name if is_home else away_team_name)
                df.insert(df.columns.get_loc("Player") + 4, "Is_Home", 1 if is_home else 0)
                df.insert(df.columns.get_loc("Player") + 5, "Opp", away_team if is_home else home_team)
                df.insert(df.columns.get_loc("Player") + 6, "OppName", away_team_name if is_home else home_team_name)
                
                df = df.reindex(columns=skaters_columns, fill_value=None)

                skaters_data.append(df)

        # Extract advanced skaters table
        for team in [away_team, home_team]:
            table_selector = f"#{team}_adv_ALLAll"
            table = soup.select_one(table_selector)
            if table:
                # Read the table and set the headers
                df = pd.read_html(StringIO(str(table)), encoding="utf-8")[0]
                
                # Keep only rows within tbody
                df = df.iloc[:table.select("tbody tr").__len__()]

                # Insert metadata columns
                df.insert(0, "GameID", game_id)

                # Extract Player IDs from 'data-append-csv' attribute in <td> tags
                player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr th[data-append-csv]")]
                df["PlayerID"] = player_ids + [None] * (len(df) - len(player_ids))  # Handle rows without Player IDs

                adv_skaters_data.append(df)

        # Wait to avoid rate limiting
        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for game ID {game_id}: {e}")
    except Exception as e:
        print(f"Error processing data for game ID {game_id}: {e}")


# Merge skaters_data and adv_skaters_data
if skaters_data and adv_skaters_data:
    skaters_df = pd.concat(skaters_data, ignore_index=True)
    adv_skaters_df = pd.concat(adv_skaters_data, ignore_index=True)

    # Merge on PlayerID and GameID
    merged_df = skaters_df.merge(
        adv_skaters_df[["GameID", "PlayerID", "HIT", "BLK", "SAT‑F"]],
        on=["GameID", "PlayerID"],
        how="left"
    )
    
    merged_df = (
        merged_df.groupby(["GameID", "Team"])
        .head(18)
        .reset_index(drop=True)
    )

    # Reorder columns according to the specified schema
    merged_columns = [
        "Season", "Gm#", "Game", "GameID", "Date", "Player", "PlayerID", "Team", "TeamName", "Is_Home", "Opp", "OppName", "G", "A", "PTS", "SOG", "HIT", "BLK", "TOI", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA"
    ]
    merged_df = merged_df.reindex(columns=merged_columns)
    
    merged_df["Team"] = merged_df["Team"].replace("UTA", "ARI")
    merged_df["TeamName"] = merged_df["TeamName"].replace("Utah Hockey Club", "Arizona Coyotes")
    merged_df["Opp"] = merged_df["Opp"].replace("UTA", "ARI")
    merged_df["OppName"] = merged_df["OppName"].replace("Utah Hockey Club", "Arizona Coyotes")
    
# Load existing gamelogs.csv to get the max Gm# for each player
metrics_file_path = r"C:\Users\ashle\Documents\Projects\hockey\data\gamelogs.csv"
if os.path.exists(metrics_file_path):
    metrics_data = pd.read_csv(metrics_file_path, parse_dates=["Date"], low_memory=False)
else:
    metrics_data = pd.DataFrame(columns=["PlayerID", "Gm#", "Date"])

# Sort merged_df by PlayerID and Date to ensure chronological order
merged_df["Date"] = pd.to_datetime(merged_df["Date"], errors="coerce")
merged_df.sort_values(by=["PlayerID", "Date"], inplace=True)

# Get the max Gm# for each player from the existing data
max_game_nums = metrics_data.groupby("PlayerID")["Gm#"].max().fillna(0).to_dict()

def assign_game_number(row):
    player_id = row["PlayerID"]
    if player_id in max_game_nums:
        # Player exists in metrics_data
        return max_game_nums[player_id] + 1 + merged_df[
            (merged_df["PlayerID"] == player_id) & (merged_df["Date"] < row["Date"])
        ].shape[0]
    else:
        # New player, assign game numbers sequentially
        return merged_df[(merged_df["PlayerID"] == player_id)].groupby("PlayerID").cumcount().loc[row.name] + 1

# Apply the function to assign Gm#
merged_df["Gm#"] = merged_df.apply(assign_game_number, axis=1)


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
    "rouselu01": ("Lukas Rousek"),    
}

# Replace player names for those found in player_info
merged_df["Player"] = merged_df["PlayerID"].map(player_info).fillna(merged_df["Player"])


# Save the updated gamelogs
final_gamelogs_path = os.path.join(base_path, "gamelogs1.csv")
merged_df.to_csv(final_gamelogs_path, mode='a', index=False, encoding="utf-8")
print(f"Updated gamelogs saved to {final_gamelogs_path}")


# Create gameIndex.csv
game_index_data = (
    merged_df.groupby(["GameID", "Season", "Date", "Game", "Team", "Is_Home", "TeamName"])
    .agg({"G": "sum"})  # Sum goals for each team
    .reset_index()
)

# Split into Home and Away data
home_data = game_index_data[game_index_data["Is_Home"] == 1].rename(
    columns={"Team": "HomeID", "G": "G", "TeamName": "Home"}
)
away_data = game_index_data[game_index_data["Is_Home"] == 0].rename(
    columns={"Team": "AwayID", "G": "GA", "TeamName": "Away"}
)

# Merge Home and Away data for each game
game_index = pd.merge(
    home_data[["GameID", "Season", "Date", "Game", "Home", "HomeID", "G"]],
    away_data[["GameID", "Away", "AwayID", "GA"]],
    on="GameID",
    how="inner"
)

# Reorder columns
game_index = game_index[
    ["Season", "Date", "Game", "GameID", "Home", "HomeID", "G", "Away", "AwayID", "GA"]
]

# Save to gameIndex.csv
game_index_file_path = os.path.join(data_path, "gameindex.csv")
game_index.to_csv(game_index_file_path, mode='a', index=False, header=False, encoding="utf-8")
print(f"Game index saved to {game_index_file_path}")


# Aggregate team-level statistics
team_stats = (
    merged_df.groupby(["GameID", "Team", "Is_Home", "TeamName", "Opp"])
    .agg({
        "G": "sum",
        "A": "sum",
        "PTS": "sum",
        "SOG": "sum",
        "HIT": "sum",
        "BLK": "sum"
    })
    .reset_index()
)

# Prepare opponent stats
opponent_stats = team_stats.rename(
    columns={
        "G": "GA", "A": "AA", "PTS": "PTSA", "SOG": "SOGA", "HIT": "HITA", "BLK": "BLKA",
        "Team": "OppID", "TeamName": "OppName"
    }
)

# Merge team stats with opponent stats
team_gamelogs = pd.merge(
    team_stats,
    opponent_stats[["GameID", "OppID", "GA", "AA", "PTSA", "SOGA", "HITA", "BLKA"]],
    left_on=["GameID", "Opp"],
    right_on=["GameID", "OppID"],
    how="inner"
)

# Drop redundant columns
team_gamelogs = team_gamelogs.drop(columns=["OppID"])

# Add season and date columns from the original merged_df
game_info = merged_df[["GameID", "Season", "Date"]].drop_duplicates()
team_gamelogs = pd.merge(team_gamelogs, game_info, on="GameID", how="left")

# Rename and reorder columns
team_gamelogs = team_gamelogs.rename(columns={"TeamName": "Team", "Team": "TeamID"})
team_gamelogs = team_gamelogs[
    [
        "Season", "Date", "GameID", "Team", "TeamID", "Is_Home", "Opp",
        "G", "A", "PTS", "SOG", "HIT", "BLK", "GA", "AA", "PTSA", "SOGA", "HITA", "BLKA"
    ]
]

# Save to teamGamelogs1.csv
team_gamelogs_file_path = os.path.join(data_path, "teamgamelogs.csv")
team_gamelogs.to_csv(team_gamelogs_file_path, mode='a', index=False, header=False,encoding="utf-8")
print(f"Team gamelogs saved to {team_gamelogs_file_path}")


# Conferences to scrape
conferences = ["EAS", "WES"]
years = ["2025"]

# Define columns for final output
stats_columns = ["Team", "GP", "W", "L", "OTL", "Points", "PtsPct", "GF", "GA", "SOW", "SOL", "PPG", "PPO", "PPpct", "PPGA", "PPOA", "PKpct", "PIMperG", "PIMAperG", "SOG", "SPct", "SOGA", "SVPct"]

standings_columns = ["Conference", "Team", "RW"]

final_columns = ["Conference", "Division", "Rk", "TeamID", "Team", "GP", "W", "L", "OTL", "Points", "PtsPct", "RW", "ROW", "SOW", "GF", "GA", "GDiff", "SOG", "SPct", "SOGA", "SVPct", "PPG", "PPO", "PPpct", "PPGA", "PPOA", "PKpct", "PIM", "PIMA"]

team_info = {
    "Florida Panthers": ("Eastern", "Atlantic", "FLA"),
    "Toronto Maple Leafs": ("Eastern", "Atlantic", "TOR"),
    "Tampa Bay Lightning": ("Eastern", "Atlantic", "TBL"),
    "Boston Bruins": ("Eastern", "Atlantic", "BOS"),
    "Buffalo Sabres": ("Eastern", "Atlantic", "BUF"),
    "Detroit Red Wings": ("Eastern", "Atlantic", "DET"),
    "Ottawa Senators": ("Eastern", "Atlantic", "OTT"),
    "Montreal Canadiens": ("Eastern", "Atlantic", "MTL"),
    "Washington Capitals": ("Eastern", "Metropolitan", "WSH"),
    "New Jersey Devils": ("Eastern", "Metropolitan", "NJD"),
    "Carolina Hurricanes": ("Eastern", "Metropolitan", "CAR"),
    "New York Rangers": ("Eastern", "Metropolitan", "NYR"),
    "Philadelphia Flyers": ("Eastern", "Metropolitan", "PHI"),
    "New York Islanders": ("Eastern", "Metropolitan", "NYI"),
    "Pittsburgh Penguins": ("Eastern", "Metropolitan", "PIT"),
    "Columbus Blue Jackets": ("Eastern", "Metropolitan", "CBJ"),
    "Winnipeg Jets": ("Western", "Central", "WPG"),
    "Minnesota Wild": ("Western", "Central", "MIN"),
    "Dallas Stars": ("Western", "Central", "DAL"),
    "Colorado Avalanche": ("Western", "Central", "COL"),
    "Arizona Coyotes": ("Western", "Central", "ARI"),
    "St. Louis Blues": ("Western", "Central", "STL"),
    "Nashville Predators": ("Western", "Central", "NSH"),
    "Chicago Blackhawks": ("Western", "Central", "CHI"),
    "Vegas Golden Knights": ("Western", "Pacific", "VEG"),
    "Los Angeles Kings": ("Western", "Pacific", "LAK"),
    "Edmonton Oilers": ("Western", "Pacific", "EDM"),
    "Calgary Flames": ("Western", "Pacific", "CGY"),
    "Vancouver Canucks": ("Western", "Pacific", "VAN"),
    "Seattle Kraken": ("Western", "Pacific", "SEA"),
    "San Jose Sharks": ("Western", "Pacific", "SJS"),
    "Anaheim Ducks": ("Western", "Pacific", "ANA")
}

# Function to fetch and parse tables
def fetch_and_parse(driver, url):
    driver.get(url)
    time.sleep(random.uniform(5, 10))  # Wait for 5-10 seconds randomly
    return BeautifulSoup(driver.page_source, "html.parser")

# Combine all data for years
stats_data = []

for year in years:
    url = f"https://www.hockey-reference.com/leagues/NHL_{year}.html"
    print(f"Processing {year}...")
    try:
        soup = fetch_and_parse(driver, url)
        table = soup.select_one("#stats")
        if table:
            header_row = table.select("thead tr")[1]
            headers = [th.get_text(strip=True) if th.get_text(strip=True) else "Team" for th in header_row.find_all("th")]
            
            rows = table.select("tbody tr")
            
            valid_rows = [
                row for row in rows
                if len(row.find_all("td")) > 0
            ]
            
            consolidated_html = '<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>'.format(
                ''.join(f'<th>{header}</th>' for header in headers),
                ''.join(str(row) for row in valid_rows)
            )
            df = pd.read_html(StringIO(consolidated_html), encoding="utf-8")[0]
            df.columns = headers
            
            column_mapping = {
                "OL": "OTL",
                "PTS": "Points",
                "PTS%": "PtsPct",
                "PP": "PPG",
                "PP%": "PPpct",
                "PPA": "PPGA",
                "PK%": "PKpct",
                "PIM/G": "PIMperG",
                "oPIM/G": "PIMAperG",
                "S": "SOG",
                "S%": "SPct",
                "SA": "SOGA",
                "SV%": "SVPct"
            }
            
            column_names = list(df.columns)
            for i, col in enumerate(column_names):
                if col == "OL":
                    column_names[i] = column_mapping["OL"]
                elif col == "PTS":
                    column_names[i] = column_mapping["PTS"]
                elif col == "PTS%":
                    column_names[i] = column_mapping["PTS%"]
                elif col == "PP":
                    column_names[i] = column_mapping["PP"]
                elif col == "PP%":
                    column_names[i] = column_mapping["PP%"]
                elif col == "PPA":
                    column_names[i] = column_mapping["PPA"]
                elif col == "PK%":
                    column_names[i] = column_mapping["PK%"]
                elif col == "PIM/G":
                    column_names[i] = column_mapping["PIM/G"]
                elif col == "oPIM/G":
                    column_names[i] = column_mapping["oPIM/G"]
                elif col == "S":
                    column_names[i] = column_mapping["S"]
                elif col == "S%":
                    column_names[i] = column_mapping["S%"]
                elif col == "SA":
                    column_names[i] = column_mapping["SA"]    
                elif col == "SV%":
                    column_names[i] = column_mapping["SV%"]
            df.columns = column_names    

            
            df = df[["Team", "GP", "W", "L", "OTL", "Points", "PtsPct", "GF", "GA", "SOW", "SOL", "PPG", "PPO", "PPpct", "PPGA", "PPOA", "PKpct", "PIMperG", "PIMAperG", "SOG", "SPct", "SOGA", "SVPct"]]
            
            df = df.reindex(columns=stats_columns, fill_value=None)
            
        stats_data.append(df)

    except Exception as e:
        print(f"Error processing {year}: {e}")

driver.quit()

standings_data = []

for conference in conferences:
    url = f"https://www.hockey-reference.com/leagues/NHL_2025.html"

    try:
        print(f"Processing data")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        conf_section = soup.select_one(f"#standings_{conference}_sh")
        conf_name = conf_section.find("h2").get_text(strip=True) if conf_section else "Unknown"

        table_selector = f"#standings_{conference}"
        table = soup.select_one(table_selector)
        if table:
            header_row = table.select("thead tr")[0]
            headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
            
            headers[0] = "Team"
            
            rows = table.select("tbody tr:not([class='thead'])")
            
            consolidated_rows = []
            for row in rows:
                if "Division" in row.get_text(strip=True):
                    continue
                consolidated_rows.append(row)
            
            consolidated_html = '<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>'.format(
                ''.join(f'<th>{header}</th>' for header in headers),
                ''.join(str(row) for row in consolidated_rows)
            )
            
            df = pd.read_html(StringIO(consolidated_html), encoding="utf-8")[0]
            df.columns = headers
            
            df = df[["Team", "RW"]]
            
            df.insert(0, "Conference", conf_name)
            
            df = df.reindex(columns=standings_columns, fill_value=None)

            standings_data.append(df)

        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for conference {conference}: {e}")
    except Exception as e:
        print(f"Error processing data for conference {conference}: {e}")

# Merge skaters_data and adv_skaters_data
if stats_data and standings_data:
    stats_df = pd.concat(stats_data, ignore_index=True)
    standings_df = pd.concat(standings_data, ignore_index=True)

    # Merge on PlayerID and GameID
    merged_standings_df = standings_df.merge(stats_df, on=["Team"], how="left")
    
    merged_standings_df["ROW"] = merged_standings_df["W"] - merged_standings_df["SOW"]
    merged_standings_df["GDiff"] = merged_standings_df["GF"] - merged_standings_df["GA"]
    merged_standings_df["PIM"] = (merged_standings_df["PIMperG"] * merged_standings_df["GP"]).round(0).astype(int)
    merged_standings_df["PIMA"] = (merged_standings_df["PIMAperG"] * merged_standings_df["GP"]).round(0).astype(int)
    merged_standings_df["Team"] = merged_standings_df["Team"].replace("Utah Hockey Club", "Arizona Coyotes")
    
    merged_standings_df["Conference"] = merged_standings_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown", "Unknown"))[0])
    merged_standings_df["Division"] = merged_standings_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown", "Unknown"))[1])
    merged_standings_df["TeamID"] = merged_standings_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown", "Unknown"))[2])

    merged_standings_df.sort_values(by=["Conference", "Division", "Points"], ascending=[True, True, False], inplace=True)

    merged_standings_df["Rk"] = (
        merged_standings_df.groupby(["Conference", "Division"])
        .cumcount() + 1
    )

    merged_standings_df = merged_standings_df[final_columns]
    
    # Save the merged DataFrame to a single CSV file
    
    merged_file_path = os.path.join(data_path, "leaderTeams.csv")
    merged_standings_df.to_csv(merged_file_path, index=False, encoding="utf-8")
    print(f"Merged data successfully saved to {merged_file_path}")
else:
    print("Insufficient data to merge.")