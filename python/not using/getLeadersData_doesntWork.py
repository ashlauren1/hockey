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

games_info = {
    "2025"
}

base_path = r"C:\Users\ashle\Documents\Projects\hockey"
file_path = {
    "standings": os.path.join(base_path, "teamStats.csv")
}

standings_data = []

for game_id in games_info:
    url = f"https://www.hockey-reference.com/leagues/NHL_{game_id}.html"

    try:
        print(f"Processing game ID {game_id}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        table_selector = f"#stats"
        table = soup.select_one(table_selector)
        if table:
            df = pd.read_html(StringIO(str(table)))[0]
            df = df.iloc[:table.select("tbody tr").__len__()]
            df.insert(0, "Game ID", game_id)
            
            standings_data.append(df)
                
        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for game ID {game_id}: {e}")
    except Exception as e:
        print(f"Error processing data for game ID {game_id}: {e}")

# Save all collected data to CSV files by appending
if standings_data:
    pd.concat(standings_data, ignore_index=True).to_csv(file_path['standings'], index=False, encoding='utf-8', mode='a', header=not os.path.exists(file_path['standings']))
    print(f"standings data successfully appended to {file_path['standings']}")

if not any([standings_data]):
    print("No data collected.")