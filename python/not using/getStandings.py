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

# Define the conferences
conferences = {"EAS", "WES"}

# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\hockey"
file_paths = {"standings": os.path.join(base_path, "teamStandings.csv")}

# Initialize lists to collect data
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
            
            df.insert(0, "Conference", conf_name) 

            standings_data.append(df)

        # Wait to avoid rate limiting
        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for conference {conference}: {e}")
    except Exception as e:
        print(f"Error processing data for conference {conference}: {e}")

# Save all collected data to CSV files by appending
if standings_data:
    pd.concat(standings_data, ignore_index=True).to_csv(file_paths['standings'], index=False, encoding='utf-8', mode='a', header=not os.path.exists(file_paths['standings']))
    print(f"standings data successfully appended to {file_paths['standings']}")

if not any([standings_data]):
    print("No data collected.")
