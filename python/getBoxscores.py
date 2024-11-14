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

# Define the game IDs, home teams, and away teams
games_info = { 
    "202411130PIT": ("PIT", "DET"),
    "202411130WSH": ("WSH", "TOR"),
    "202411130UTA": ("UTA", "CAR"),
    "202411130COL": ("COL", "LAK"),
    "202411130ANA": ("ANA", "VEG")
}



# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\hockey"
file_paths = {
    "skaters": os.path.join(base_path, "hockeyRefBoxscores_Skaters25_2.csv"),
    "adv_skaters": os.path.join(base_path, "hockeyRefBoxscores_AdvSkaters25_2.csv")
}

# Initialize lists to collect data
skaters_data = []
adv_skaters_data = []

for game_id, (home_team, away_team) in games_info.items():
    url = f"https://www.hockey-reference.com/boxscores/{game_id}.html"

    try:
        print(f"Processing game ID {game_id} - Home Team: {home_team}, Away Team: {away_team}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract skaters table
        for team in [away_team, home_team]:
            table_selector = f"#{team}_skaters"
            table = soup.select_one(table_selector)
            if table:
                # Read table into DataFrame, excluding footer rows if present
                df = pd.read_html(StringIO(str(table)))[0]

                # Keep only rows within tbody (skip footer by limiting rows if needed)
                df = df.iloc[:table.select("tbody tr").__len__()]

                # Insert metadata columns
                df.insert(0, "Game ID", game_id)
                df.insert(1, "Home Team", home_team)
                df.insert(2, "Away Team", away_team)

                # Extract Player IDs from 'data-append-csv' attribute in <td> tags
                player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr td[data-append-csv]")]
                df["Player ID"] = player_ids + [None] * (len(df) - len(player_ids))  # Handle rows without Player IDs

                skaters_data.append(df)

        # Extract advanced skaters table
        for team in [away_team, home_team]:
            table_selector = f"#{team}_adv_ALLAll"
            table = soup.select_one(table_selector)
            if table:
                # Read table into DataFrame, excluding footer rows if present
                df = pd.read_html(StringIO(str(table)))[0]

                # Keep only rows within tbody
                df = df.iloc[:table.select("tbody tr").__len__()]

                # Insert metadata columns
                df.insert(0, "Game ID", game_id)
                df.insert(1, "Home Team", home_team)
                df.insert(2, "Away Team", away_team)

                # Extract Player IDs from 'data-append-csv' attribute in <td> tags
                player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr th[data-append-csv]")]
                df["Player ID"] = player_ids + [None] * (len(df) - len(player_ids))  # Handle rows without Player IDs

                adv_skaters_data.append(df)

        # Wait to avoid rate limiting
        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for game ID {game_id}: {e}")
    except Exception as e:
        print(f"Error processing data for game ID {game_id}: {e}")

# Save all collected data to CSV files by appending
if skaters_data:
    pd.concat(skaters_data, ignore_index=True).to_csv(file_paths['skaters'], index=False, encoding='utf-8', mode='a', header=not os.path.exists(file_paths['skaters']))
    print(f"Skaters data successfully appended to {file_paths['skaters']}")

if adv_skaters_data:
    pd.concat(adv_skaters_data, ignore_index=True).to_csv(file_paths['adv_skaters'], index=False, encoding='utf-8', mode='a', header=not os.path.exists(file_paths['adv_skaters']))
    print(f"Advanced skaters data successfully appended to {file_paths['adv_skaters']}")

if not any([skaters_data, adv_skaters_data]):
    print("No data collected.")
