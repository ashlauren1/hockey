from io import StringIO 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import random

# **File Paths**
base_path = r"C:\Users\ashle\Documents\Projects\hockey"
output_path = os.path.join(base_path, "teamStats.csv")
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
final_columns = [
    "Season", "Team", "AvAge", "GP", "W", "L", "OTL", "Points", "PtsPct", "SOW", "SOL", "GF", "GA", "GDiff", "SOG", "SPct", "SOGA", "SVPct", "PPG", "PPO", "PPpct", "PPGA", "PPOA", "PKpct", "SOS", "GF/G", "GA/G", "PIM/G", "oPIM/G"
]

# Function to fetch and parse tables
def fetch_and_parse(driver, url):
    driver.get(url)
    time.sleep(random.uniform(5, 10))  # Wait for 5-10 seconds randomly
    return BeautifulSoup(driver.page_source, "html.parser")

# Combine all data for years
all_data = []

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
            
            df = df[["Rk", "Team", "GP", "W", "L" ,"OL", "PTS", "PTS%", "GF", "GA", "SOW", "SOL", "SRS", "SOS", "GF/G", "GA/G", "PP", "PPO", "PP%", "PPA", "PPOA", "PK%", "SH", "SHA", "PIM/G", "oPIM/G", "S", "S%", "SA", "SV%"]]

        else:
            print(f"Stats table not found for {year}")
            continue
            
        all_data.append(df)
        print(f"Columns for {year}: {df.columns}")

    except Exception as e:
        print(f"Error processing {year}: {e}")

# Combine and save the final DataFrame
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv(output_path, index=False)
    print(f"Data successfully saved to {output_path}")
else:
    print("No data available.")

# Quit the browser
driver.quit()