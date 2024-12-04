from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Define rate limit parameters
REQUESTS_PER_MINUTE = 20
ONE_MINUTE = 60

@sleep_and_retry
@limits(calls=REQUESTS_PER_MINUTE, period=ONE_MINUTE)
def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

base_path = r"C:\Users\ashle\Documents\Projects\hockey"
output_path = os.path.join(base_path, "teamStatsAndStandings.csv")
os.makedirs(base_path, exist_ok=True)

# Define Chrome options
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-webgl")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

# Initialize WebDriver
service = Service(r"C:\Users\ashle\AppData\Local\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Conferences to scrape
conferences = ["EAS", "WES"]
years = ["2025"]

# Define columns for final output
final_columns = [
    "Season", "Team", "AvAge", "GP", "W", "L", "OTL", "Points", "PtsPct", "SOW", "SOL", "GF", "GA", "GDiff", "SOG", "SPct", "SOGA", "SVPct", "PPG", "PPO", "PPpct", "PPGA", "PPOA", "PKpct", "SOS", "GF/G", "GA/G", "PIM/G", "oPIM/G"
]

# Function to fetch and parse tables
def fetch_and_parse(driver, url):
    driver.get(url)
    time.sleep(random.uniform(5, 10))  # Wait for 5-10 seconds randomly
    return BeautifulSoup(driver.page_source, "html.parser")

# Function to read stats table with second thead row
def read_table_with_second_thead(stats_table):
    thead_rows = stats_table.select("thead tr")
    if len(thead_rows) > 1:
        second_thead = thead_rows[1]
        headers = [th.get_text(strip=True) if th.get_text(strip=True) else "Team" for th in second_thead.find_all("th")]
        df = pd.read_html(StringIO(str(stats_table)))[0]
        df.columns = headers
    else:
        df = pd.read_html(StringIO(str(stats_table)))[0]
    return df

# Combine all data for years
stats_data = []
standings_data = []

for year in years:
    url = f"https://www.hockey-reference.com/leagues/NHL_{year}.html"
    print(f"Processing {year}...")
    try:
        soup = fetch_and_parse(driver, url)

        stats_table = soup.select_one("#stats")
        if stats_table:
            print(stats_table)
            df = read_table_with_second_thead(stats_table)
            if "Team" not in df.columns:
                df.rename(columns={df.columns[1]: "Team"}, inplace=True)
            df["Team"] = df["Team"].str.strip().str.lower().str.replace("*", "", regex=False)
        else:
            print(f"Stats table not found for {year}")
            continue
            
        stats_data.append(df)
        print(f"Data for {year} successfully appended.")

    except Exception as e:
        print(f"Error processing {year}: {e}")

if stats_data:
    print("Stats data found.")
else:
    print("Stats data not found.")
    
# Quit the browser
driver.quit()

for year in years:
    url = f"https://www.hockey-reference.com/leagues/NHL_{year}.html"

    try:
        print(f"Processing eastern data")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        table_selector = f"#standings_EAS"
        table = soup.select_one(table_selector)
        
        if table:
            print(table)
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
            east_df = pd.read_html(StringIO(consolidated_html), encoding="utf-8")[0]
            
            standings_data.append(east_df)
        
        # Wait to avoid rate limiting
        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for eastern conference: {e}")
    except Exception as e:
        print(f"Error processing data for eastern conference: {e}")


for year in years:
    url = f"https://www.hockey-reference.com/leagues/NHL_{year}.html"

    try:
        print(f"Processing western data")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        table_selector = f"#standings_WES"
        table = soup.select_one(table_selector)
        
        if table:
            print(table)
            rows = table.select("tbody tr:not([class='thead'])")
            
            consolidated_rows = []
            for row in rows:
                if "Division" in row.get_text(strip=True):
                    continue
                consolidated_rows.append(row)
            
            consolidated_html = '<tbody>{}</tbody>'.format(
                ''.join(str(row) for row in consolidated_rows)
            )
            west_df = pd.read_html(StringIO(consolidated_html), encoding="utf-8")[0]
            
            standings_data.append(west_df)

        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for western conference: {e}")
    except Exception as e:
        print(f"Error processing data for western conference: {e}")

if stats_data and standings_data:
    stats_df = pd.concat(stats_data, ignore_index=True)
    standings_df = pd.concat(standings_data, ignore_index=True)

    merged_df = pd.merge(stats_df, standings_df, on='Team', how="left")

    merged_file_path = os.path.join(base_path, "teamStatsAndStandings.csv")
    merged_df.to_csv(merged_file_path, index=False, encoding="utf-8")
    print(f"Merged data successfully saved to {merged_file_path}")
else:
    print("Insufficient data to merge.")