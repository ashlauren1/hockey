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
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-webgl")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

# Initialize WebDriver
service = Service(r"C:\Users\ashle\AppData\Local\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Conferences and years to scrape
years = ["2025"]

def fetch_with_retry(driver, url, retries=3):
    for attempt in range(retries):
        try:
            driver.get(url)
            time.sleep(3)
            return BeautifulSoup(driver.page_source, "html.parser")
        except Exception as e:
            print(f"Retry {attempt + 1} for {url}: {e}")
    raise Exception(f"Failed to fetch {url} after {retries} attempts")

def read_table_with_second_thead(table):
    thead_rows = table.select("thead tr")
    headers = [th.get_text(strip=True) or "Team" for th in thead_rows[1].find_all("th")]
    df = pd.read_html(StringIO(str(table)), encoding="utf-8")[0]
    df.columns = headers
    return df

all_data = []

for year in years:
    url = f"https://www.hockey-reference.com/leagues/NHL_{year}.html"
    
    try:
        print(f"Processing {year}...")
        soup = fetch_with_retry(driver, url)

        # Process stats
        table_selector = "#stats"
        table = soup.select_one(table_selector)

        if table:
            header_row = table.select("thead tr")[1]
            headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
            
            headers[1] = "Team"
            stats_df = read_table_with_second_thead(table)            


            stats_df["Team"] = stats_df["Team"].str.strip().str.replace("*", "", regex=False)

        else:
            print(f"Stats table not found for {year}")
            continue

            all_data.append(stats_df)

    except Exception as e:
        print(f"Error processing {year}: {e}")

if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv(output_path, index=False)
    print(f"Data successfully saved to {output_path}")
else:
    print("No data available.")

driver.quit()
