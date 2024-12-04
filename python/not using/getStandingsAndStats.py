from io import StringIO 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import random
from ratelimit import limits, sleep_and_retry
import requests

REQUESTS_PER_MINUTE = 20
ONE_MINUTE = 60

@sleep_and_retry
@limits(calls=REQUESTS_PER_MINUTE, period=ONE_MINUTE)
def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# **File Paths**
base_path = r"C:\Users\ashle\Documents\Projects\hockey\data"
os.makedirs(base_path, exist_ok=True)

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
    merged_df = standings_df.merge(stats_df, on=["Team"], how="left")
    
    merged_df["ROW"] = merged_df["W"] - merged_df["SOW"]
    merged_df["GDiff"] = merged_df["GF"] - merged_df["GA"]
    merged_df["PIM"] = (merged_df["PIMperG"] * merged_df["GP"]).round(0).astype(int)
    merged_df["PIMA"] = (merged_df["PIMAperG"] * merged_df["GP"]).round(0).astype(int)
    merged_df["Team"] = merged_df["Team"].replace("Utah Hockey Club", "Arizona Coyotes")
    
    merged_df["Conference"] = merged_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown", "Unknown"))[0])
    merged_df["Division"] = merged_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown", "Unknown"))[1])
    merged_df["TeamID"] = merged_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown", "Unknown"))[2])

    merged_df.sort_values(by=["Conference", "Division", "Points"], ascending=[True, True, False], inplace=True)

    merged_df["Rk"] = (
        merged_df.groupby(["Conference", "Division"])
        .cumcount() + 1
    )

    merged_df = merged_df[final_columns]
    
    # Save the merged DataFrame to a single CSV file
    merged_file_path = os.path.join(base_path, "leaderTeams.csv")
    merged_df.to_csv(merged_file_path, index=False, encoding="utf-8")
    print(f"Merged data successfully saved to {merged_file_path}")
else:
    print("Insufficient data to merge.")