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

years_info = ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]

base_path = r"C:\Users\ashle\Documents\Projects\hockey"
output_path = os.path.join(base_path, "teamStandings.csv")
os.makedirs(base_path, exist_ok=True)

standings_data = []

def extract_standings_data(year, soup, conference):
    table_selector = f"#standings_{conference}"
    table = soup.select_one(table_selector)
    if not table:
        print(f"Could not find {conference} standings table for {year}")
        return None
    
    # Parse the table using pandas
    df = pd.read_html(str(table))[0]
    
    # Rename columns for consistency
    column_mapping = {
        "OL": "OTL",
        "PTS": "Points",
        "PTS%": "PtsPct"
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Add metadata columns
    df.insert(0, "Season", year)
    df.insert(1, "Conference", "Eastern" if "EAS" in conference else "Western")
    
    return df

# Loop over each year and scrape data
for year in years_info:
    url = f"https://www.hockey-reference.com/leagues/NHL_{year}.html"
    try:
        print(f"Fetching data for year {year}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, "html.parser")
        
        eastern_df = extract_standings_data(year, soup, "EAS")
        western_df = extract_standings_data(year, soup, "WES")
        
        if eastern_df is not None:
            standings_data.append(eastern_df)
        if western_df is not None:
            standings_data.append(western_df)
        
        time.sleep(3)  # Pause between requests
        
    except requests.RequestException as e:
        print(f"Request error for {year}: {e}")
    except Exception as e:
        print(f"Error processing {year}: {e}")

# Combine all standings data and save to CSV
if standings_data:
    standings_df = pd.concat(standings_data, ignore_index=True)
    standings_df.to_csv(output_path, index=False)
    print(f"Data successfully saved to {output_path}")
else:
    print("No data scraped.")
