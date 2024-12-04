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

def convert_toi_to_decimal(toi_str):
    """Convert TOI from 'mm:ss' to decimal minutes."""
    try:
        minutes, seconds = map(int, toi_str.split(':'))
        return minutes + seconds / 60
    except ValueError:
        return None

goalie_info = {
    's/sarosju01', 'h/helleco01', 'b/binnijo01', 'g/gustafi01', 'm/marksja02', 'm/montesa01', 'v/vasilan02', 'd/daccojo01', 'l/lankike01', 'm/mrazepe01', 's/shestig01', 's/swaymje01', 'b/blackma01', 'b/bobrose01', 'g/georgal01', 'h/hillad01', 'l/luukkuk01', 'o/oettija01', 's/skinnst01', 'm/merzlel01', 'r/rittida01', 's/sorokil01', 'd/dostalu01', 't/talboca01', 'u/ullmali01', 'k/kochepy01', 's/stolaan01', 'i/ingraco01', 't/thomplo01', 'v/vejmeka01', 'v/vladada01', 'w/wolfdu01', 'l/lindgch01', 'n/nedelal01', 'a/annunju01', 'e/erssosa01', 'v/vanecvi01', 'f/forsban01', 'k/knighsp01', 'k/korpijo01', 'k/kuempda01', 'p/primeca01', 'v/varlasi01', 'a/allenja01', 'f/fedotiv01', 'j/jarrytr01', 'l/lyonal01', 'm/martisp01', 'p/pickaca01', 's/samsoil01', 'b/blomqjo01', 'd/desmica01', 'g/grubaph01', 'h/hoferjo01', 't/tarasda02', 'w/wolljo01', 'k/kolosal01', 'l/levide01', 'q/quickjo01', 's/silovar01', 's/soderar01', 'c/comrier01', 'f/fleurma01', 'g/gibsojo02', 'w/wedgesc01', 'w/wedgesc01', 'w/wedgesc01', 'j/johanjo03', 'a/anderfr01', 'h/hussovi01', 'r/reimeja01', 'r/reimeja01', 'r/reimeja01', 'a/askarya01', 'h/hildede01', 'c/copleph01', 'k/kahkoka01', 'm/minertr01', 'p/peretya01', 'p/portier01', 's/schmiak01', 's/staubja01', 's/sogaama01'
}

goalie_columns = [
    'Season', 'PlayerID', "Date", "Tm", "Is_Home", "Opp", "DEC", "GA", "SA", "SV", "SV%", "SO", "TOI"
]

years = {'2023', '2024', '2025'}

# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\hockey"
goalie_path = os.path.join(base_path, "goalieBoxscores.csv")

# Initialize lists to collect data
goalie_data = []

for goalie_id in goalie_info:
    url = f"https://www.hockey-reference.com/players/{goalie_id}/gamelog/2025"

    try:
        print(f"Processing goalie {goalie_id}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        table = soup.select_one("#gamelog")
        
        if table:
            header_row = table.select("thead tr")[1]
            headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
            headers[5] = "Is_Home"

            # Read the table and set the headers
            df = pd.read_html(StringIO(str(table)), encoding="utf-8")[0]
            df.columns = headers
            
            df = df.iloc[:table.select("tbody tr").__len__()]
            
            df.columns = list(df.columns)
            
            df = df[["Date", "Tm", "Is_Home", "Opp", "DEC", "GA", "SA", "SV", "SV%", "SO", "TOI"]]
            
            if "TOI" in df.columns:
                df["TOI"] = df["TOI"].apply(convert_toi_to_decimal)

            # Insert metadata columns              
            df.insert(0, "Season", "2024-25")
            df.insert(1, "PlayerID", goalie_id)
            
            df = df.reindex(columns=goalie_columns, fill_value=None)

            goalie_data.append(df)

        # Wait to avoid rate limiting
        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for {goalie_id}: {e}")
    except Exception as e:
        print(f"Error processing data for {goalie_id}: {e}")

# Save all collected data to CSV files by appending
if goalie_data:
    goalie_df = pd.concat(goalie_data, ignore_index=True)
    
    goalie_df['Is_Home'] = goalie_df['Is_Home'].replace('' '1')
    goalie_df['Is_Home'] = goalie_df['Is_Home'].replace('@' '0')
    
    
    goalie_df.to_csv(goalie_path, index=False, header=False, encoding="utf-8")
    print(f"Goalie data successfully appended to {goalie_path}")

else:
    print("No data collected.")
