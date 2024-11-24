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
teams_info = {   
    "ANA",
    "BOS",
    "BUF",
    "CAR",
    "CBJ",
    "CGY",
    "CHI",
    "COL",
    "DAL",
    "DET",
    "EDM",
    "FLA",
    "LAK",
    "MIN",
    "MTL",
    "NJD",
    "NSH",
    "NYI",
    "NYR",
    "OTT",
    "PHI",
    "PIT",
    "SEA",
    "SJS",
    "STL",
    "TBL",
    "TOR",
    "UTA",
    "VAN",
    "VEG",
    "WPG",
    "WSH"
}


# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\hockey"
file_paths = {
    "teams": os.path.join(base_path, "hockeyRef_TeamGamelogs.csv")
}

# Initialize lists to collect data
teams_data = []

for team_id in teams_info:
    url = f"https://www.hockey-reference.com/teams/{team_id}/2025_gamelog.html"

    try:
        print(f"Processing team {team_id}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        table_selector = f"#tm_gamelog_rs"
        table = soup.select_one(table_selector)
        if table:
            df = pd.read_html(StringIO(str(table)))[0]

            df.insert(0, "Team ID", team_id)

            teams_data.append(df)

        # Wait to avoid rate limiting
        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for team {team_id}: {e}")
    except Exception as e:
        print(f"Error processing data for team {team_id}: {e}")

# Save all collected data to CSV files by appending
if teams_data:
    pd.concat(teams_data, ignore_index=True).to_csv(file_paths['teams'], index=False, encoding='utf-8', mode='a', header=not os.path.exists(file_paths['teams']))
    print(f"Teams data successfully appended to {file_paths['teams']}")

if not any([teams_data]):
    print("No data collected.")
