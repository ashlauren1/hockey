from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os
from datetime import datetime

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
    "202411300NYR": ("NYR", "MTL"),
    "202411300FLA": ("FLA", "CAR"),
    "202411300TBL": ("TBL", "TOR"),
    "202411300NJD": ("NJD", "WSH"),
    "202411300PIT": ("PIT", "CGY"),
    "202411300STL": ("STL", "PHI"),
    "202411300LAK": ("LAK", "OTT"),
    "202411300NYI": ("NYI", "BUF"),
    "202411300MIN": ("MIN", "NSH"),
    "202411300COL": ("COL", "EDM"),
    "202411300VEG": ("VEG", "UTA"),
    "202411300SEA": ("SEA", "SJS")
}

# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\hockey"
file_paths = {
    "skaters": os.path.join(base_path, "hockeyRefBoxscores_Skaters25.csv"),
    "adv_skaters": os.path.join(base_path, "hockeyRefBoxscores_AdvSkaters25.csv")
}

skaters_columns = [
    "Rk", "Season", "Game", "GameID", "Date", "Home", "HomeName", "Away", "AwayName", "Player", "PlayerID", "Team", "TeamName", "Is_Home", "Opp", "OppName", "G", "A", "PTS", "SOG", "TOI", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA"
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

                # Keep only rows within tbody (skip footer by limiting rows if needed)
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
                df.insert(4, "Home", home_team)
                df.insert(5, "HomeName", home_team_name)
                df.insert(6, "Away", away_team)
                df.insert(7, "AwayName", away_team_name)
                
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

    # Reorder columns according to the specified schema
    merged_columns = [
        "Rk", "Season", "Game", "GameID", "Date", "Home", "HomeName", "Away", "AwayName", "Player", "PlayerID", "Team", "TeamName", "Is_Home", "Opp", "OppName", "G", "A", "PTS", "SOG", "HIT", "BLK", "TOI", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA", "SAT‑F"
    ]
    merged_df = merged_df.reindex(columns=merged_columns)

    # Save the merged DataFrame to a single CSV file
    merged_file_path = os.path.join(base_path, "hockeyRefBoxscores_Merged25.csv")
    merged_df.to_csv(merged_file_path, index=False, encoding="utf-8")
    print(f"Merged data successfully saved to {merged_file_path}")
else:
    print("Insufficient data to merge. Ensure both skaters and advanced skaters tables are populated.")

