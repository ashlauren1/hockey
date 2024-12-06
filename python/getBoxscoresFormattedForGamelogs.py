from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
import os
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random


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

def extract_date_from_game_id(game_id):
    date_str = game_id[:8]
    return datetime.strptime(date_str, "%Y%m%d").strftime("%m/%d/%Y")


# Define the game IDs, home teams, and away teams
games_info = {
    "202412050BUF": ("BUF", "WPG"),
    "202412050MTL": ("MTL", "NSH"),
    "202412050OTT": ("OTT", "DET"),
    "202412050TBL": ("TBL", "SJS"),
    "202412050PHI": ("PHI", "FLA"),
    "202412050CAR": ("CAR", "COL"),
    "202412050NYI": ("NYI", "SEA"),
    "202412050CGY": ("CGY", "STL"),
    "202412050EDM": ("EDM", "CBJ")
}
    
#    "202412060TOR": ("TOR", "WSH"),
#    "202412060NJD": ("NJD", "SEA"),
#    "202412060NYR": ("NYR", "PIT"),
#    "202412060VAN": ("VAN", "CBJ"),
#    "202412060VEG": ("VEG", "DAL"),
#    "202412060ANA": ("ANA", "MIN"),
#    "202412070BOS": ("BOS", "PHI"),
#    "202412070BUF": ("BUF", "UTA"),
#    "202412070CHI": ("CHI", "WPG"),
#    "202412070NYI": ("NYI", "CAR"),
#    "202412070FLA": ("FLA", "SJS"),
#    "202412070MTL": ("MTL", "WSH"),
#    "202412070OTT": ("OTT", "NSH"),
#    "202412070DET": ("DET", "COL"),
#    "202412070PIT": ("PIT", "TOR"),
#    "202412070LAK": ("LAK", "MIN"),
#    "202412070EDM": ("EDM", "STL"),
#    "202412080NYR": ("NYR", "SEA"),
#    "202412080VAN": ("VAN", "TBL"),
#    "202412080OTT": ("OTT", "NYI"),
#    "202412080WPG": ("WPG", "CBJ"),
#    "202412080NJD": ("NJD", "COL"),
#    "202412080PHI": ("PHI", "UTA"),
#    "202412080DAL": ("DAL", "CGY"),
#    "202412090BUF": ("BUF", "DET"),
#    "202412090NYR": ("NYR", "CHI"),
#    "202412090MTL": ("MTL", "ANA"),
#    "202412100NJD": ("NJD", "TOR"),
#    "202412100PIT": ("PIT", "COL"),
#    "202412100CAR": ("CAR", "SJS"),
#    "202412100CBJ": ("CBJ", "PHI"),
#    "202412100NYI": ("NYI", "LAK"),
#    "202412100NSH": ("NSH", "CGY"),
#    "202412100WPG": ("WPG", "BOS"),
#    "202412100EDM": ("EDM", "TBL"),
#    "202412100UTA": ("UTA", "MIN"),
#    "202412100VAN": ("VAN", "STL"),
#    "202412100SEA": ("SEA", "FLA"),
#    "202412110BUF": ("BUF", "NYR"),
#    "202412110OTT": ("OTT", "ANA"),
#    "202412120TOR": ("TOR", "ANA"),
#    "202412120MTL": ("MTL", "PIT"),
#    "202412120NJD": ("NJD", "LAK"),
#    "202412120PHI": ("PHI", "DET"),
#    "202412120CBJ": ("CBJ", "WSH"),
#    "202412120NYI": ("NYI", "CHI"),
#    "202412120STL": ("STL", "SJS"),
#    "202412120DAL": ("DAL", "NSH"),
#    "202412120MIN": ("MIN", "EDM"),
#    "202412120WPG": ("WPG", "VEG"),
#    "202412120COL": ("COL", "UTA"),
#    "202412120CGY": ("CGY", "TBL"),
#    "202412120VAN": ("VAN", "FLA"),
#    "202412120SEA": ("SEA", "BOS"),
#    "202412130CAR": ("CAR", "OTT"),
#    "202412140NJD": ("NJD", "CHI"),
#    "202412140NYR": ("NYR", "LAK"),
#    "202412140MIN": ("MIN", "PHI"),
#    "202412140EDM": ("EDM", "VEG"),
#    "202412140OTT": ("OTT", "PIT"),
#    "202412140DET": ("DET", "TOR"),
#    "202412140WSH": ("WSH", "BUF"),
#    "202412140CBJ": ("CBJ", "ANA"),
#    "202412140WPG": ("WPG", "MTL"),
#    "202412140DAL": ("DAL", "STL"),
#    "202412140COL": ("COL", "NSH"),
#    "202412140CGY": ("CGY", "FLA"),
#    "202412140VAN": ("VAN", "BOS"),
#    "202412140SJS": ("SJS", "UTA"),
#    "202412140SEA": ("SEA", "TBL"),
#    "202412150CHI": ("CHI", "NYI"),
#    "202412150TOR": ("TOR", "BUF"),
#    "202412150CAR": ("CAR", "CBJ"),
#    "202412150STL": ("STL", "NYR"),
#    "202412150MIN": ("MIN", "VEG"),
#    "202412160DAL": ("DAL", "WSH"),
#    "202412160EDM": ("EDM", "FLA"),
#    "202412160VAN": ("VAN", "COL"),
#    "202412170MTL": ("MTL", "BUF"),
#    "202412170TBL": ("TBL", "CBJ"),
#    "202412170PIT": ("PIT", "LAK"),
#    "202412170CAR": ("CAR", "NYI"),
#    "202412170STL": ("STL", "NJD"),
#    "202412170NSH": ("NSH", "NYR"),
#    "202412170CHI": ("CHI", "WSH"),
#    "202412170CGY": ("CGY", "BOS"),
#    "202412170SEA": ("SEA", "OTT"),
#    "202412170SJS": ("SJS", "WPG"),
#    "202412180DET": ("DET", "PHI"),
#    "202412180DAL": ("DAL", "TOR"),
#    "202412180MIN": ("MIN", "FLA"),
#    "202412180UTA": ("UTA", "VAN"),
#    "202412180ANA": ("ANA", "WPG"),
#    "202412190TBL": ("TBL", "STL"),
#    "202412190PHI": ("PHI", "LAK"),
#    "202412190CBJ": ("CBJ", "NJD"),
#    "202412190NSH": ("NSH", "PIT"),
#    "202412190CHI": ("CHI", "SEA"),
#    "202412190CGY": ("CGY", "OTT"),
#    "202412190EDM": ("EDM", "BOS"),
#    "202412190VEG": ("VEG", "VAN"),
#    "202412190SJS": ("SJS", "COL"),
#    "202412200BUF": ("BUF", "TOR"),
#    "202412200DET": ("DET", "MTL"),
#    "202412200FLA": ("FLA", "STL"),
#    "202412200WSH": ("WSH", "CAR"),
#    "202412200DAL": ("DAL", "NYR"),
#    "202412200MIN": ("MIN", "UTA"),
#    "202412200ANA": ("ANA", "COL"),
#    "202412210NSH": ("NSH", "LAK"),
#    "202412210CGY": ("CGY", "CHI"),
#    "202412210EDM": ("EDM", "SJS"),
#    "202412210BOS": ("BOS", "BUF"),
#    "202412210TOR": ("TOR", "NYI"),
#    "202412210MTL": ("MTL", "DET"),
#    "202412210NJD": ("NJD", "PIT"),
#    "202412210PHI": ("PHI", "CBJ"),
#    "202412210WPG": ("WPG", "MIN"),
#    "202412210VAN": ("VAN", "OTT"),
#    "202412210VEG": ("VEG", "SEA"),
#    "202412220NYR": ("NYR", "CAR"),
#    "202412220TBL": ("TBL", "FLA"),
#    "202412220WSH": ("WSH", "LAK"),
#    "202412220UTA": ("UTA", "ANA"),
#    "202412220COL": ("COL", "SEA"),
#    "202412220EDM": ("EDM", "OTT"),
#    "202412230NJD": ("NJD", "NYR"),
#    "202412230TOR": ("TOR", "WPG"),
#    "202412230BOS": ("BOS", "WSH"),
#    "202412230DET": ("DET", "STL"),
#    "202412230FLA": ("FLA", "TBL"),
#    "202412230PIT": ("PIT", "PHI"),
#    "202412230CBJ": ("CBJ", "MTL"),
#    "202412230NYI": ("NYI", "BUF"),
#    "202412230NSH": ("NSH", "CAR"),
#    "202412230MIN": ("MIN", "CHI"),
#    "202412230VAN": ("VAN", "SJS"),
#    "202412230UTA": ("UTA", "DAL"),
#    "202412230VEG": ("VEG", "ANA"),
#    "202412270BUF": ("BUF", "CHI"),
#    "202412270DET": ("DET", "TOR"),
#    "202412270NJD": ("NJD", "CAR"),
#    "202412270CBJ": ("CBJ", "BOS"),
#    "202412270STL": ("STL", "NSH"),
#    "202412270DAL": ("DAL", "MIN"),
#    "202412270UTA": ("UTA", "COL"),
#    "202412270SJS": ("SJS", "VEG"),
#    "202412280FLA": ("FLA", "MTL"),
#    "202412280VAN": ("VAN", "SEA"),
#    "202412280ANA": ("ANA", "PHI"),
#    "202412280LAK": ("LAK", "EDM"),
#    "202412280BOS": ("BOS", "CBJ"),
#    "202412280TOR": ("TOR", "WSH"),
#    "202412280TBL": ("TBL", "NYR"),
#    "202412280CAR": ("CAR", "NJD"),
#    "202412280WPG": ("WPG", "OTT"),
#    "202412280NYI": ("NYI", "PIT"),
#    "202412280SJS": ("SJS", "CGY"),
#    "202412290CHI": ("CHI", "DAL"),
#    "202412290ANA": ("ANA", "EDM"),
#    "202412290DET": ("DET", "WSH"),
#    "202412290TBL": ("TBL", "MTL"),
#    "202412290PIT": ("PIT", "NYI"),
#    "202412290STL": ("STL", "BUF"),
#    "202412290MIN": ("MIN", "OTT"),
#    "202412290VEG": ("VEG", "CGY"),
#    "202412290LAK": ("LAK", "PHI"),
#    "202412300FLA": ("FLA", "NYR"),
#    "202412300WPG": ("WPG", "NSH"),
#    "202412300SEA": ("SEA", "UTA"),
#    "202412310WSH": ("WSH", "BOS"),
#    "202412310TOR": ("TOR", "NYI"),
#    "202412310VEG": ("VEG", "MTL"),
#    "202412310CHI": ("CHI", "STL"),
#    "202412310DET": ("DET", "PIT"),
#    "202412310CBJ": ("CBJ", "CAR"),
#    "202412310DAL": ("DAL", "BUF"),
#    "202412310MIN": ("MIN", "NSH"),
#    "202412310COL": ("COL", "WPG"),
#    "202412310ANA": ("ANA", "NJD"),
#    "202412310SJS": ("SJS", "PHI"),
#    "202412310CGY": ("CGY", "VAN"),
#    "202412310EDM": ("EDM", "UTA"),
#    "202501010LAK": ("LAK", "NJD"),
#    "202501020FLA": ("FLA", "CAR"),
#    "202501020NYR": ("NYR", "BOS"),
#    "202501020WSH": ("WSH", "MIN"),
#    "202501020CBJ": ("CBJ", "DET"),
#    "202501020NYI": ("NYI", "TOR"),
#    "202501020DAL": ("DAL", "OTT"),
#    "202501020WPG": ("WPG", "ANA"),
#    "202501020COL": ("COL", "BUF"),
#    "202501020CGY": ("CGY", "UTA"),
#    "202501020VEG": ("VEG", "PHI"),
#    "202501020SEA": ("SEA", "VAN"),
#    "202501020SJS": ("SJS", "TBL"),
#    "202501030FLA": ("FLA", "PIT"),
#    "202501030CHI": ("CHI", "MTL"),
#    "202501030STL": ("STL", "OTT"),
#    "202501030EDM": ("EDM", "ANA"),
#    "202501030VAN": ("VAN", "NSH"),
#    "202501040WSH": ("WSH", "NYR"),
#    "202501040WPG": ("WPG", "DET"),
#    "202501040SJS": ("SJS", "NJD"),
#    "202501040TOR": ("TOR", "BOS"),
#    "202501040CAR": ("CAR", "MIN"),
#    "202501040CBJ": ("CBJ", "STL"),
#    "202501040COL": ("COL", "MTL"),
#    "202501040CGY": ("CGY", "NSH"),
#    "202501040DAL": ("DAL", "UTA"),
#    "202501040LAK": ("LAK", "TBL"),
#    "202501040VEG": ("VEG", "BUF"),
#    "202501040SEA": ("SEA", "EDM"),
#    "202501050CHI": ("CHI", "NYR"),
#    "202501050BOS": ("BOS", "NYI"),
#    "202501050CAR": ("CAR", "PIT"),
#    "202501050TOR": ("TOR", "PHI"),
#    "202501050ANA": ("ANA", "TBL"),
#    "202501060BUF": ("BUF", "WSH"),
#    "202501060MTL": ("MTL", "VAN"),
#    "202501060COL": ("COL", "FLA"),
#    "202501060SEA": ("SEA", "NJD"),
#    "202501070BOS": ("BOS", "EDM"),
#    "202501070DET": ("DET", "OTT"),
#    "202501070NYR": ("NYR", "DAL"),
#    "202501070PHI": ("PHI", "TOR"),
#    "202501070PIT": ("PIT", "CBJ"),
#    "202501070MIN": ("MIN", "STL"),
#    "202501070WPG": ("WPG", "NSH"),
#    "202501070ANA": ("ANA", "CGY"),
#    "202501070SJS": ("SJS", "VEG"),
#    "202501080WSH": ("WSH", "VAN"),
#    "202501080CHI": ("CHI", "COL"),
#    "202501080UTA": ("UTA", "FLA"),
#    "202501080LAK": ("LAK", "CGY"),
#    "202501090OTT": ("OTT", "BUF"),
#    "202501090TBL": ("TBL", "BOS"),
#    "202501090NYR": ("NYR", "NJD"),
#    "202501090PHI": ("PHI", "DAL"),
#    "202501090PIT": ("PIT", "EDM"),
#    "202501090CAR": ("CAR", "TOR"),
#    "202501090CBJ": ("CBJ", "SEA"),
#    "202501090STL": ("STL", "ANA"),
#    "202501090MIN": ("MIN", "COL"),
#    "202501090VEG": ("VEG", "NYI"),
#    "202501100DET": ("DET", "CHI"),
#    "202501100WSH": ("WSH", "MTL"),
#    "202501100CAR": ("CAR", "VAN"),
#    "202501100WPG": ("WPG", "LAK"),
#    "202501100UTA": ("UTA", "SJS"),
#    "202501110FLA": ("FLA", "BOS"),
#    "202501110BUF": ("BUF", "SEA"),
#    "202501110PIT": ("PIT", "OTT"),
#    "202501110TOR": ("TOR", "VAN"),
#    "202501110MTL": ("MTL", "DAL"),
#    "202501110NJD": ("NJD", "TBL"),
#    "202501110PHI": ("PHI", "ANA"),
#    "202501110CHI": ("CHI", "EDM"),
#    "202501110STL": ("STL", "CBJ"),
#    "202501110WPG": ("WPG", "COL"),
#    "202501110NSH": ("NSH", "WSH"),
#    "202501110UTA": ("UTA", "NYI"),
#    "202501110CGY": ("CGY", "LAK"),
#    "202501110VEG": ("VEG", "NYR"),
#    "202501110SJS": ("SJS", "MIN"),
#    "202501120DET": ("DET", "SEA"),
#    "202501120OTT": ("OTT", "DAL"),
#    "202501120PIT": ("PIT", "TBL"),
#    "202501120CAR": ("CAR", "ANA"),
#    "202501120VEG": ("VEG", "MIN"),
#    "202501130PHI": ("PHI", "FLA"),
#    "202501130CHI": ("CHI", "CGY"),
#    "202501130EDM": ("EDM", "LAK"),
#    "202501140BOS": ("BOS", "TBL"),
#    "202501140TOR": ("TOR", "DAL"),
#    "202501140DET": ("DET", "SJS"),
#    "202501140NJD": ("NJD", "FLA"),
#    "202501140PIT": ("PIT", "SEA"),
#    "202501140WSH": ("WSH", "ANA"),
#    "202501140CBJ": ("CBJ", "PHI"),
#    "202501140NYI": ("NYI", "OTT"),
#    "202501140STL": ("STL", "CGY"),
#    "202501140NSH": ("NSH", "VEG"),
#    "202501140WPG": ("WPG", "VAN"),
#    "202501140COL": ("COL", "NYR"),
#    "202501140UTA": ("UTA", "MTL"),
#    "202501150BUF": ("BUF", "CAR"),
#    "202501150MIN": ("MIN", "EDM"),
#    "202501160TOR": ("TOR", "NJD"),
#    "202501160OTT": ("OTT", "WSH"),
#    "202501160TBL": ("TBL", "ANA"),
#    "202501160FLA": ("FLA", "DET"),
#    "202501160CBJ": ("CBJ", "SJS"),
#    "202501160NYI": ("NYI", "PHI"),
#    "202501160STL": ("STL", "CGY"),
#    "202501160NSH": ("NSH", "CHI"),
#    "202501160DAL": ("DAL", "MTL"),
#    "202501160WPG": ("WPG", "SEA"),
#    "202501160UTA": ("UTA", "NYR"),
#    "202501160COL": ("COL", "EDM"),
#    "202501160VAN": ("VAN", "LAK"),
#    "202501170BUF": ("BUF", "PIT"),
#    "202501170CAR": ("CAR", "VEG"),
#    "202501180NJD": ("NJD", "PHI"),
#    "202501180OTT": ("OTT", "BOS"),
#    "202501180COL": ("COL", "DAL"),
#    "202501180FLA": ("FLA", "ANA"),
#    "202501180MTL": ("MTL", "TOR"),
#    "202501180TBL": ("TBL", "DET"),
#    "202501180NYR": ("NYR", "CBJ"),
#    "202501180WSH": ("WSH", "PIT"),
#    "202501180WPG": ("WPG", "CGY"),
#    "202501180NYI": ("NYI", "SJS"),
#    "202501180CHI": ("CHI", "VEG"),
#    "202501180NSH": ("NSH", "MIN"),
#    "202501180UTA": ("UTA", "STL"),
#    "202501180VAN": ("VAN", "EDM"),
#    "202501180SEA": ("SEA", "LAK"),
#    "202501190NJD": ("NJD", "OTT"),
#    "202501190MTL": ("MTL", "NYR"),
#    "202501190DAL": ("DAL", "DET"),
#    "202501200BOS": ("BOS", "SJS"),
#    "202501200COL": ("COL", "MIN"),
#    "202501200SEA": ("SEA", "BUF"),
#    "202501200VEG": ("VEG", "STL"),
#    "202501200TOR": ("TOR", "TBL"),
#    "202501200NYI": ("NYI", "CBJ"),
#    "202501200CHI": ("CHI", "CAR"),
#    "202501200UTA": ("UTA", "WPG"),
#    "202501200LAK": ("LAK", "PIT"),
#    "202501210MTL": ("MTL", "TBL"),
#    "202501210NYR": ("NYR", "OTT"),
#    "202501210PHI": ("PHI", "DET"),
#    "202501210NSH": ("NSH", "SJS"),
#    "202501210DAL": ("DAL", "CAR"),
#    "202501210EDM": ("EDM", "WSH"),
#    "202501210VAN": ("VAN", "BUF"),
#    "202501210ANA": ("ANA", "FLA"),
#    "202501220TOR": ("TOR", "CBJ"),
#    "202501220NJD": ("NJD", "BOS"),
#    "202501220COL": ("COL", "WPG"),
#    "202501220LAK": ("LAK", "FLA"),
#    "202501230BOS": ("BOS", "OTT"),
#    "202501230DET": ("DET", "MTL"),
#    "202501230NYR": ("NYR", "PHI"),
#    "202501230CAR": ("CAR", "CBJ"),
#    "202501230STL": ("STL", "VEG"),
#    "202501230MIN": ("MIN", "UTA"),
#    "202501230CGY": ("CGY", "BUF"),
#    "202501230EDM": ("EDM", "VAN"),
#    "202501230ANA": ("ANA", "PIT"),
#    "202501230SEA": ("SEA", "WSH"),
#    "202501230SJS": ("SJS", "NSH"),
#    "202501240NYI": ("NYI", "PHI"),
#    "202501240CHI": ("CHI", "TBL"),
#    "202501240DAL": ("DAL", "VEG"),
#    "202501240WPG": ("WPG", "UTA"),
#    "202501250BOS": ("BOS", "COL"),
#    "202501250EDM": ("EDM", "BUF"),
#    "202501250SEA": ("SEA", "PIT"),
#    "202501250MTL": ("MTL", "NJD"),
#    "202501250OTT": ("OTT", "TOR"),
#    "202501250DET": ("DET", "TBL"),
#    "202501250CBJ": ("CBJ", "LAK"),
#    "202501250STL": ("STL", "DAL"),
#    "202501250MIN": ("MIN", "CGY"),
#    "202501250NYI": ("NYI", "CAR"),
#    "202501250VAN": ("VAN", "WSH"),
#    "202501250ANA": ("ANA", "NSH"),
#    "202501250SJS": ("SJS", "FLA"),
#    "202501260NYR": ("NYR", "COL"),
#    "202501260OTT": ("OTT", "UTA"),
#    "202501260WPG": ("WPG", "CGY"),
#    "202501260CHI": ("CHI", "MIN"),
#    "202501260VEG": ("VEG", "FLA"),
#    "202501270DET": ("DET", "LAK"),
#    "202501270PHI": ("PHI", "NJD"),
#    "202501270STL": ("STL", "VAN"),
#    "202501270EDM": ("EDM", "SEA"),
#    "202501270SJS": ("SJS", "PIT"),
#    "202501280BUF": ("BUF", "BOS"),
#    "202501280MTL": ("MTL", "WPG"),
#    "202501280TBL": ("TBL", "CHI"),
#    "202501280NYR": ("NYR", "CAR"),
#    "202501280NYI": ("NYI", "COL"),
#    "202501280CGY": ("CGY", "WSH"),
#    "202501280VEG": ("VEG", "DAL"),
#    "202501280SEA": ("SEA", "ANA"),
#    "202501290TOR": ("TOR", "MIN"),
#    "202501290FLA": ("FLA", "LAK"),
#    "202501290NJD": ("NJD", "PHI"),
#    "202501290NSH": ("NSH", "VAN"),
#    "202501290UTA": ("UTA", "PIT"),
#    "202501300BOS": ("BOS", "WPG"),
#    "202501300MTL": ("MTL", "MIN"),
#    "202501300OTT": ("OTT", "WSH"),
#    "202501300TBL": ("TBL", "LAK"),
#    "202501300PHI": ("PHI", "NYI"),
#    "202501300CAR": ("CAR", "CHI"),
#    "202501300CGY": ("CGY", "ANA"),
#    "202501300EDM": ("EDM", "DET"),
#    "202501300VEG": ("VEG", "CBJ"),
#    "202501300SEA": ("SEA", "SJS"),
#    "202501310BUF": ("BUF", "NSH"),
#    "202501310DAL": ("DAL", "VAN"),
#    "202501310COL": ("COL", "STL"),
#    "202501310UTA": ("UTA", "CBJ"),
#    "202502010FLA": ("FLA", "CHI"),
#    "202502010BOS": ("BOS", "NYR"),
#    "202502010OTT": ("OTT", "MIN"),
#    "202502010TBL": ("TBL", "NYI"),
#    "202502010PIT": ("PIT", "NSH"),
#    "202502010WSH": ("WSH", "WPG"),
#    "202502010CAR": ("CAR", "LAK"),
#    "202502010EDM": ("EDM", "TOR"),
#    "202502010CGY": ("CGY", "DET"),
#    "202502020BUF": ("BUF", "NJD"),
#    "202502020COL": ("COL", "PHI"),
#    "202502020ANA": ("ANA", "MTL"),
#    "202502020FLA": ("FLA", "NYI"),
#    "202502020NYR": ("NYR", "VEG"),
#    "202502020DAL": ("DAL", "CBJ"),
#    "202502020UTA": ("UTA", "STL"),
#    "202502020VAN": ("VAN", "DET"),
#    "202502020SEA": ("SEA", "CGY"),
#    "202502030NSH": ("NSH", "OTT"),
#    "202502040BOS": ("BOS", "MIN"),
#    "202502040BUF": ("BUF", "CBJ"),
#    "202502040TBL": ("TBL", "OTT"),
#    "202502040PIT": ("PIT", "NJD"),
#    "202502040WSH": ("WSH", "FLA"),
#    "202502040NYI": ("NYI", "VEG"),
#    "202502040STL": ("STL", "EDM"),
#    "202502040WPG": ("WPG", "CAR"),
#    "202502040CGY": ("CGY", "TOR"),
#    "202502040UTA": ("UTA", "PHI"),
#    "202502040VAN": ("VAN", "COL"),
#    "202502040ANA": ("ANA", "DAL"),
#    "202502040SEA": ("SEA", "DET"),
#    "202502040SJS": ("SJS", "MTL"),
#    "202502050NYR": ("NYR", "BOS"),
#    "202502050CHI": ("CHI", "EDM"),
#    "202502050LAK": ("LAK", "MTL"),
#    "202502060TBL": ("TBL", "OTT"),
#    "202502060NJD": ("NJD", "VEG"),
#    "202502060PHI": ("PHI", "WSH"),
#    "202502060CBJ": ("CBJ", "UTA"),
#    "202502060STL": ("STL", "FLA"),
#    "202502060MIN": ("MIN", "CAR"),
#    "202502060CGY": ("CGY", "COL"),
#    "202502060SEA": ("SEA", "TOR"),
#    "202502060SJS": ("SJS", "VAN"),
#    "202502070NYR": ("NYR", "PIT"),
#    "202502070WPG": ("WPG", "NYI"),
#    "202502070CHI": ("CHI", "NSH"),
#    "202502070EDM": ("EDM", "COL"),
#    "202502070LAK": ("LAK", "DAL"),
#    "202502080MTL": ("MTL", "NJD"),
#    "202502080DET": ("DET", "TBL"),
#    "202502080CAR": ("CAR", "UTA"),
#    "202502080BOS": ("BOS", "VEG"),
#    "202502080FLA": ("FLA", "OTT"),
#    "202502080PHI": ("PHI", "PIT"),
#    "202502080CBJ": ("CBJ", "NYR"),
#    "202502080STL": ("STL", "CHI"),
#    "202502080VAN": ("VAN", "TOR"),
#    "202502080NSH": ("NSH", "BUF"),
#    "202502080MIN": ("MIN", "NYI"),
#    "202502080CGY": ("CGY", "SEA"),
#    "202502080LAK": ("LAK", "ANA"),
#    "202502080SJS": ("SJS", "DAL"),
#    "202502090WSH": ("WSH", "UTA"),
#    "202502090MTL": ("MTL", "TBL"),
#    "202502220PHI": ("PHI", "EDM"),
#    "202502220PIT": ("PIT", "WSH"),
#    "202502220DET": ("DET", "MIN"),
#    "202502220BUF": ("BUF", "NYR"),
#    "202502220FLA": ("FLA", "SEA"),
#    "202502220NJD": ("NJD", "DAL"),
#    "202502220NSH": ("NSH", "COL"),
#    "202502220BOS": ("BOS", "ANA"),
#    "202502220TOR": ("TOR", "CAR"),
#    "202502220OTT": ("OTT", "MTL"),
#    "202502220CBJ": ("CBJ", "CHI"),
#    "202502220STL": ("STL", "WPG"),
#    "202502220LAK": ("LAK", "UTA"),
#    "202502220VEG": ("VEG", "VAN"),
#    "202502230WSH": ("WSH", "EDM"),
#    "202502230PIT": ("PIT", "NYR"),
#    "202502230DET": ("DET", "ANA"),
#    "202502230TBL": ("TBL", "SEA"),
#    "202502230STL": ("STL", "COL"),
#    "202502230NSH": ("NSH", "NJD"),
#    "202502230CHI": ("CHI", "TOR"),
#    "202502230NYI": ("NYI", "DAL"),
#    "202502230CGY": ("CGY", "SJS"),
#    "202502230UTA": ("UTA", "VAN"),
#    "202502240WPG": ("WPG", "SJS"),
#    "202502240LAK": ("LAK", "VEG"),
#    "202502250BOS": ("BOS", "TOR"),
#    "202502250BUF": ("BUF", "ANA"),
#    "202502250MTL": ("MTL", "CAR"),
#    "202502250TBL": ("TBL", "EDM"),
#    "202502250PHI": ("PHI", "PIT"),
#    "202502250WSH": ("WSH", "CGY"),
#    "202502250CBJ": ("CBJ", "DAL"),
#    "202502250NYI": ("NYI", "NYR"),
#    "202502250STL": ("STL", "SEA"),
#    "202502250NSH": ("NSH", "FLA"),
#    "202502250MIN": ("MIN", "DET"),
#    "202502250UTA": ("UTA", "CHI"),
#    "202502260OTT": ("OTT", "WPG"),
#    "202502260COL": ("COL", "NJD"),
#    "202502260LAK": ("LAK", "VAN"),
#    "202502270BOS": ("BOS", "NYI"),
#    "202502270MTL": ("MTL", "SJS"),
#    "202502270DET": ("DET", "CBJ"),
#    "202502270TBL": ("TBL", "CGY"),
#    "202502270FLA": ("FLA", "EDM"),
#    "202502270PIT": ("PIT", "PHI"),
#    "202502270WSH": ("WSH", "STL"),
#    "202502270CAR": ("CAR", "BUF"),
#    "202502270NSH": ("NSH", "WPG"),
#    "202502270UTA": ("UTA", "MIN"),
#    "202502270VEG": ("VEG", "CHI"),
#    "202502270ANA": ("ANA", "VAN"),
#    "202502280NYR": ("NYR", "TOR"),
#    "202502280DAL": ("DAL", "LAK"),
#    "202502280COL": ("COL", "MIN"),
#    "202503010NYI": ("NYI", "NSH"),
#    "202503010WSH": ("WSH", "TBL"),
#    "202503010CBJ": ("CBJ", "DET"),
#    "202503010FLA": ("FLA", "CGY"),
#    "202503010PIT": ("PIT", "BOS"),
#    "202503010BUF": ("BUF", "MTL"),
#    "202503010OTT": ("OTT", "SJS"),
#    "202503010CAR": ("CAR", "EDM"),
#    "202503010WPG": ("WPG", "PHI"),
#    "202503010STL": ("STL", "LAK"),
#    "202503010UTA": ("UTA", "NJD"),
#    "202503010ANA": ("ANA", "CHI"),
#    "202503010SEA": ("SEA", "VAN"),
#    "202503020PIT": ("PIT", "TOR"),
#    "202503020MIN": ("MIN", "BOS"),
#    "202503020CAR": ("CAR", "CGY"),
#    "202503020DAL": ("DAL", "STL"),
#    "202503020NYR": ("NYR", "NSH"),
#    "202503020VEG": ("VEG", "NJD"),
#    "202503030WSH": ("WSH", "OTT"),
#    "202503030MTL": ("MTL", "BUF"),
#    "202503030FLA": ("FLA", "TBL"),
#    "202503030NYR": ("NYR", "NYI"),
#    "202503030TOR": ("TOR", "SJS"),
#    "202503030CHI": ("CHI", "LAK"),
#    "202503040BOS": ("BOS", "NSH"),
#    "202503040BUF": ("BUF", "SJS"),
#    "202503040DET": ("DET", "CAR"),
#    "202503040TBL": ("TBL", "CBJ"),
#    "202503040PHI": ("PHI", "CGY"),
#    "202503040NYI": ("NYI", "WPG"),
#    "202503040DAL": ("DAL", "NJD"),
#    "202503040COL": ("COL", "PIT"),
#    "202503040EDM": ("EDM", "ANA"),
#    "202503040SEA": ("SEA", "MIN"),
#    "202503050NYR": ("NYR", "WSH"),
#    "202503050CHI": ("CHI", "OTT"),
#    "202503050VEG": ("VEG", "TOR"),
#    "202503050VAN": ("VAN", "ANA"),
#    "202503050LAK": ("LAK", "STL"),
#    "202503060DET": ("DET", "UTA"),
#    "202503060TBL": ("TBL", "BUF"),
#    "202503060FLA": ("FLA", "CBJ"),
#    "202503060PHI": ("PHI", "WPG"),
#    "202503060CAR": ("CAR", "BOS"),
#    "202503060NSH": ("NSH", "SEA"),
#    "202503060DAL": ("DAL", "CGY"),
#    "202503060EDM": ("EDM", "MTL"),
#    "202503060COL": ("COL", "SJS"),
#    "202503070NJD": ("NJD", "WPG"),
#    "202503070WSH": ("WSH", "DET"),
#    "202503070CHI": ("CHI", "UTA"),
#    "202503070VAN": ("VAN", "MIN"),
#    "202503070VEG": ("VEG", "PIT"),
#    "202503070ANA": ("ANA", "STL"),
#    "202503080OTT": ("OTT", "NYR"),
#    "202503080PHI": ("PHI", "SEA"),
#    "202503080TBL": ("TBL", "BOS"),
#    "202503080FLA": ("FLA", "BUF"),
#    "202503080COL": ("COL", "TOR"),
#    "202503080CGY": ("CGY", "MTL"),
#    "202503080NSH": ("NSH", "CHI"),
#    "202503080LAK": ("LAK", "STL"),
#    "202503080EDM": ("EDM", "DAL"),
#    "202503080SJS": ("SJS", "NYI"),
#    "202503090PHI": ("PHI", "NJD"),
#    "202503090WSH": ("WSH", "SEA"),
#    "202503090MIN": ("MIN", "PIT"),
#    "202503090CAR": ("CAR", "WPG"),
#    "202503090NYR": ("NYR", "CBJ"),
#    "202503090VEG": ("VEG", "LAK"),
#    "202503090VAN": ("VAN", "DAL"),
#    "202503090ANA": ("ANA", "NYI"),
#    "202503100BUF": ("BUF", "EDM"),
#    "202503100OTT": ("OTT", "DET"),
#    "202503100COL": ("COL", "CHI"),
#    "202503100UTA": ("UTA", "TOR"),
#    "202503110BOS": ("BOS", "FLA"),
#    "202503110NJD": ("NJD", "CBJ"),
#    "202503110PHI": ("PHI", "OTT"),
#    "202503110PIT": ("PIT", "VEG"),
#    "202503110CAR": ("CAR", "TBL"),
#    "202503110MIN": ("MIN", "COL"),
#    "202503110WPG": ("WPG", "NYR"),
#    "202503110VAN": ("VAN", "MTL"),
#    "202503110ANA": ("ANA", "WSH"),
#    "202503110LAK": ("LAK", "NYI"),
#    "202503110SJS": ("SJS", "NSH"),
#    "202503120DET": ("DET", "BUF"),
#    "202503120CGY": ("CGY", "VAN"),
#    "202503120UTA": ("UTA", "ANA"),
#    "202503120SEA": ("SEA", "MTL"),
#    "202503130TOR": ("TOR", "FLA"),
#    "202503130OTT": ("OTT", "BOS"),
#    "202503130NJD": ("NJD", "EDM"),
#    "202503130PHI": ("PHI", "TBL"),
#    "202503130PIT": ("PIT", "STL"),
#    "202503130CBJ": ("CBJ", "VEG"),
#    "202503130MIN": ("MIN", "NYR"),
#    "202503130LAK": ("LAK", "WSH"),
#    "202503130SJS": ("SJS", "CHI"),
#    "202503140CAR": ("CAR", "DET"),
#    "202503140NYI": ("NYI", "EDM"),
#    "202503140WPG": ("WPG", "DAL"),
#    "202503140CGY": ("CGY", "COL"),
#    "202503140ANA": ("ANA", "NSH"),
#    "202503140SEA": ("SEA", "UTA"),
#    "202503150BUF": ("BUF", "VEG"),
#    "202503150PIT": ("PIT", "NJD"),
#    "202503150SJS": ("SJS", "WSH"),
#    "202503150BOS": ("BOS", "TBL"),
#    "202503150TOR": ("TOR", "OTT"),
#    "202503150MTL": ("MTL", "FLA"),
#    "202503150PHI": ("PHI", "CAR"),
#    "202503150CBJ": ("CBJ", "NYR"),
#    "202503150MIN": ("MIN", "STL"),
#    "202503150LAK": ("LAK", "NSH"),
#    "202503150VAN": ("VAN", "CHI"),
#    "202503160DET": ("DET", "VEG"),
#    "202503160COL": ("COL", "DAL"),
#    "202503160STL": ("STL", "ANA"),
#    "202503160NYR": ("NYR", "EDM"),
#    "202503160NYI": ("NYI", "FLA"),
#    "202503160VAN": ("VAN", "UTA"),
#    "202503160SEA": ("SEA", "WPG"),
#    "202503170BOS": ("BOS", "BUF"),
#    "202503170TBL": ("TBL", "PHI"),
#    "202503170CBJ": ("CBJ", "NJD"),
#    "202503170TOR": ("TOR", "CGY"),
#    "202503170MIN": ("MIN", "LAK"),
#    "202503180MTL": ("MTL", "OTT"),
#    "202503180NYR": ("NYR", "CGY"),
#    "202503180PIT": ("PIT", "NYI"),
#    "202503180WSH": ("WSH", "DET"),
#    "202503180NSH": ("NSH", "STL"),
#    "202503180DAL": ("DAL", "ANA"),
#    "202503180CHI": ("CHI", "SEA"),
#    "202503180EDM": ("EDM", "UTA"),
#    "202503180VAN": ("VAN", "WPG"),
#    "202503190TOR": ("TOR", "COL"),
#    "202503190MIN": ("MIN", "SEA"),
#    "202503200OTT": ("OTT", "COL"),
#    "202503200NJD": ("NJD", "CGY"),
#    "202503200NYR": ("NYR", "TOR"),
#    "202503200WSH": ("WSH", "PHI"),
#    "202503200CBJ": ("CBJ", "FLA"),
#    "202503200NYI": ("NYI", "MTL"),
#    "202503200STL": ("STL", "VAN"),
#    "202503200NSH": ("NSH", "ANA"),
#    "202503200DAL": ("DAL", "TBL"),
#    "202503200CHI": ("CHI", "LAK"),
#    "202503200EDM": ("EDM", "WPG"),
#    "202503200UTA": ("UTA", "BUF"),
#    "202503200VEG": ("VEG", "BOS"),
#    "202503200SJS": ("SJS", "CAR"),
#    "202503210PIT": ("PIT", "CBJ"),
#    "202503220NYR": ("NYR", "VAN"),
#    "202503220DAL": ("DAL", "PHI"),
#    "202503220MIN": ("MIN", "BUF"),
#    "202503220STL": ("STL", "CHI"),
#    "202503220NYI": ("NYI", "CGY"),
#    "202503220LAK": ("LAK", "CAR"),
#    "202503220WSH": ("WSH", "FLA"),
#    "202503220UTA": ("UTA", "TBL"),
#    "202503220MTL": ("MTL", "COL"),
#    "202503220NJD": ("NJD", "OTT"),
#    "202503220NSH": ("NSH", "TOR"),
#    "202503220VEG": ("VEG", "DET"),
#    "202503220EDM": ("EDM", "SEA"),
#    "202503220SJS": ("SJS", "BOS"),
#    "202503230CHI": ("CHI", "PHI"),
#    "202503230WPG": ("WPG", "BUF"),
#    "202503230FLA": ("FLA", "PIT"),
#    "202503230STL": ("STL", "NSH"),
#    "202503230VEG": ("VEG", "TBL"),
#    "202503230ANA": ("ANA", "CAR"),
#    "202503230LAK": ("LAK", "BOS"),
#    "202503240NJD": ("NJD", "VAN"),
#    "202503240NYI": ("NYI", "CBJ"),
#    "202503240DAL": ("DAL", "MIN"),
#    "202503240UTA": ("UTA", "DET"),
#    "202503250BUF": ("BUF", "OTT"),
#    "202503250TOR": ("TOR", "PHI"),
#    "202503250TBL": ("TBL", "PIT"),
#    "202503250CAR": ("CAR", "NSH"),
#    "202503250STL": ("STL", "MTL"),
#    "202503250MIN": ("MIN", "VEG"),
#    "202503250WPG": ("WPG", "WSH"),
#    "202503250COL": ("COL", "DET"),
#    "202503250CGY": ("CGY", "SEA"),
#    "202503250LAK": ("LAK", "NYR"),
#    "202503260NYI": ("NYI", "VAN"),
#    "202503260CHI": ("CHI", "NJD"),
#    "202503260EDM": ("EDM", "DAL"),
#    "202503260ANA": ("ANA", "BOS"),
#    "202503270BUF": ("BUF", "PIT"),
#    "202503270DET": ("DET", "OTT"),
#    "202503270TBL": ("TBL", "UTA"),
#    "202503270PHI": ("PHI", "MTL"),
#    "202503270NSH": ("NSH", "STL"),
#    "202503270MIN": ("MIN", "WSH"),
#    "202503270COL": ("COL", "LAK"),
#    "202503270CGY": ("CGY", "DAL"),
#    "202503270SEA": ("SEA", "EDM"),
#    "202503270SJS": ("SJS", "TOR"),
#    "202503280FLA": ("FLA", "UTA"),
#    "202503280CAR": ("CAR", "MTL"),
#    "202503280CBJ": ("CBJ", "VAN"),
#    "202503280WPG": ("WPG", "NJD"),
#    "202503280CHI": ("CHI", "VEG"),
#    "202503280ANA": ("ANA", "NYR"),
#    "202503290PHI": ("PHI", "BUF"),
#    "202503290TBL": ("TBL", "NYI"),
#    "202503290COL": ("COL", "STL"),
#    "202503290MIN": ("MIN", "NJD"),
#    "202503290NSH": ("NSH", "VEG"),
#    "202503290OTT": ("OTT", "CBJ"),
#    "202503290LAK": ("LAK", "TOR"),
#    "202503290DET": ("DET", "BOS"),
#    "202503290EDM": ("EDM", "CGY"),
#    "202503290SJS": ("SJS", "NYR"),
#    "202503290SEA": ("SEA", "DAL"),
#    "202503300FLA": ("FLA", "MTL"),
#    "202503300WSH": ("WSH", "BUF"),
#    "202503300WPG": ("WPG", "VAN"),
#    "202503300CHI": ("CHI", "UTA"),
#    "202503300PIT": ("PIT", "OTT"),
#    "202503300CAR": ("CAR", "NYI"),
#    "202503300ANA": ("ANA", "TOR"),
#    "202503300LAK": ("LAK", "SJS"),
#    "202503310NJD": ("NJD", "MIN"),
#    "202503310PHI": ("PHI", "NSH"),
#    "202503310COL": ("COL", "CGY"),
#    "202503310SEA": ("SEA", "DAL"),
#    "202504010BOS": ("BOS", "WSH"),
#    "202504010MTL": ("MTL", "FLA"),
#    "202504010OTT": ("OTT", "BUF"),
#    "202504010CBJ": ("CBJ", "NSH"),
#    "202504010NYI": ("NYI", "TBL"),
#    "202504010STL": ("STL", "DET"),
#    "202504010UTA": ("UTA", "CGY"),
#    "202504010VEG": ("VEG", "EDM"),
#    "202504010ANA": ("ANA", "SJS"),
#    "202504010LAK": ("LAK", "WPG"),
#    "202504020NYR": ("NYR", "MIN"),
#    "202504020CAR": ("CAR", "WSH"),
#    "202504020TOR": ("TOR", "FLA"),
#    "202504020CHI": ("CHI", "COL"),
#    "202504020VAN": ("VAN", "SEA"),
#    "202504030MTL": ("MTL", "BOS"),
#    "202504030OTT": ("OTT", "TBL"),
#    "202504030CBJ": ("CBJ", "COL"),
#    "202504030STL": ("STL", "PIT"),
#    "202504030DAL": ("DAL", "NSH"),
#    "202504030UTA": ("UTA", "LAK"),
#    "202504030CGY": ("CGY", "ANA"),
#    "202504030VEG": ("VEG", "WPG"),
#    "202504030SJS": ("SJS", "EDM"),
#    "202504040DET": ("DET", "CAR"),
#    "202504040WSH": ("WSH", "CHI"),
#    "202504040NYI": ("NYI", "MIN"),
#    "202504050NJD": ("NJD", "NYR"),
#    "202504050OTT": ("OTT", "FLA"),
#    "202504050DAL": ("DAL", "PIT"),
#    "202504050VAN": ("VAN", "ANA"),
#    "202504050LAK": ("LAK", "EDM"),
#    "202504050BOS": ("BOS", "CAR"),
#    "202504050BUF": ("BUF", "TBL"),
#    "202504050TOR": ("TOR", "CBJ"),
#    "202504050MTL": ("MTL", "PHI"),
#    "202504050STL": ("STL", "COL"),
#    "202504050UTA": ("UTA", "WPG"),
#    "202504050CGY": ("CGY", "VEG"),
#    "202504050SJS": ("SJS", "SEA"),
#    "202504060NYI": ("NYI", "WSH"),
#    "202504060MIN": ("MIN", "DAL"),
#    "202504060OTT": ("OTT", "CBJ"),
#    "202504060DET": ("DET", "FLA"),
#    "202504060BUF": ("BUF", "BOS"),
#    "202504060CHI": ("CHI", "PIT"),
#    "202504060NSH": ("NSH", "MTL"),
#    "202504060VAN": ("VAN", "VEG"),
#    "202504070NYR": ("NYR", "TBL"),
#    "202504070WPG": ("WPG", "STL"),
#    "202504070ANA": ("ANA", "EDM"),
#    "202504070LAK": ("LAK", "SEA"),
#    "202504070SJS": ("SJS", "CGY"),
#    "202504080BUF": ("BUF", "CAR"),
#    "202504080MTL": ("MTL", "DET"),
#    "202504080FLA": ("FLA", "TOR"),
#    "202504080NJD": ("NJD", "BOS"),
#    "202504080CBJ": ("CBJ", "OTT"),
#    "202504080PIT": ("PIT", "CHI"),
#    "202504080NSH": ("NSH", "NYI"),
#    "202504080DAL": ("DAL", "VAN"),
#    "202504080UTA": ("UTA", "SEA"),
#    "202504080COL": ("COL", "VEG"),
#    "202504090TBL": ("TBL", "TOR"),
#    "202504090NYR": ("NYR", "PHI"),
#    "202504090MIN": ("MIN", "SJS"),
#    "202504090EDM": ("EDM", "STL"),
#    "202504090ANA": ("ANA", "CGY"),
#    "202504100BOS": ("BOS", "CHI"),
#    "202504100FLA": ("FLA", "DET"),
#    "202504100WSH": ("WSH", "CAR"),
#    "202504100CBJ": ("CBJ", "BUF"),
#    "202504100NYI": ("NYI", "NYR"),
#    "202504100DAL": ("DAL", "WPG"),
#    "202504100COL": ("COL", "VAN"),
#    "202504100UTA": ("UTA", "NSH"),
#    "202504100VEG": ("VEG", "SEA"),
#    "202504100LAK": ("LAK", "ANA"),
#    "202504110OTT": ("OTT", "MTL"),
#    "202504110TBL": ("TBL", "DET"),
#    "202504110NJD": ("NJD", "PIT"),
#    "202504110EDM": ("EDM", "SJS"),
#    "202504110CGY": ("CGY", "MIN"),
#    "202504120PHI": ("PHI", "NYI"),
#    "202504120CAR": ("CAR", "NYR"),
#    "202504120LAK": ("LAK", "COL"),
#    "202504120FLA": ("FLA", "BUF"),
#    "202504120TOR": ("TOR", "MTL"),
#    "202504120CBJ": ("CBJ", "WSH"),
#    "202504120CHI": ("CHI", "WPG"),
#    "202504120DAL": ("DAL", "UTA"),
#    "202504120VAN": ("VAN", "MIN"),
#    "202504120VEG": ("VEG", "NSH"),
#    "202504120SEA": ("SEA", "STL"),
#    "202504130OTT": ("OTT", "PHI"),
#    "202504130NJD": ("NJD", "NYI"),
#    "202504130PIT": ("PIT", "BOS"),
#    "202504130CAR": ("CAR", "TOR"),
#    "202504130TBL": ("TBL", "BUF"),
#    "202504130WSH": ("WSH", "CBJ"),
#    "202504130WPG": ("WPG", "EDM"),
#    "202504130CGY": ("CGY", "SJS"),
#    "202504130ANA": ("ANA", "COL"),
#    "202504140MTL": ("MTL", "CHI"),
#    "202504140DET": ("DET", "DAL"),
#    "202504140FLA": ("FLA", "NYR"),
#    "202504140NSH": ("NSH", "UTA"),
#    "202504140EDM": ("EDM", "LAK"),
#    "202504140VAN": ("VAN", "SJS"),
#    "202504150BOS": ("BOS", "NJD"),
#    "202504150BUF": ("BUF", "TOR"),
#    "202504150OTT": ("OTT", "CHI"),
#    "202504150TBL": ("TBL", "FLA"),
#    "202504150PHI": ("PHI", "CBJ"),
#    "202504150NYI": ("NYI", "WSH"),
#    "202504150STL": ("STL", "UTA"),
#    "202504150MIN": ("MIN", "ANA"),
#    "202504150CGY": ("CGY", "VEG"),
#    "202504150SEA": ("SEA", "LAK"),
#    "202504160MTL": ("MTL", "CAR"),
#    "202504160WPG": ("WPG", "ANA"),
#    "202504160NJD": ("NJD", "DET"),
#    "202504160NSH": ("NSH", "DAL"),
#    "202504160VAN": ("VAN", "VEG"),
#    "202504160SJS": ("SJS", "EDM"),
#    "202504170BUF": ("BUF", "PHI"),
#    "202504170TOR": ("TOR", "DET"),
#    "202504170OTT": ("OTT", "CAR"),
#    "202504170NYR": ("NYR", "TBL"),
#    "202504170PIT": ("PIT", "WSH"),
#    "202504170CBJ": ("CBJ", "NYI")

# File paths for the CSV outputs
base_path = r"C:\Users\ashle\Documents\Projects\hockey"
data_path = r"C:\Users\ashle\Documents\Projects\hockey\data"

skaters_columns = [
    "Season", "Gm#", "Game", "GameID", "Date", "Player", "PlayerID", "Team", "TeamName", "Is_Home", "Opp", "OppName", "G", "A", "PTS", "SOG", "TOI", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA"
]

# Initialize lists to collect data
skaters_data = []
adv_skaters_data = []

for game_id, (home_team, away_team) in games_info.items():
    url = f"https://www.hockey-reference.com/boxscores/{game_id}.html"

    try:
        print(f"Processing game ID {game_id} - Home Team: {home_team}, Away Team: {away_team}")
        html_content = fetch_webpage(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get full team names
        home_team_section = soup.select_one(f"#{home_team}_skaters_sh")
        away_team_section = soup.select_one(f"#{away_team}_skaters_sh")
        home_team_name = home_team_section.find("h2").get_text(strip=True) if home_team_section else "Unknown"
        away_team_name = away_team_section.find("h2").get_text(strip=True) if away_team_section else "Unknown"

        # Extract skaters table
        for team, team_name, is_home in [
            (home_team, home_team_name, True),
            (away_team, away_team_name, False),
        ]:
            table_selector = f"#{team}_skaters"
            table = soup.select_one(table_selector)
            if table:
                # Extract the correct header row (second row in the <thead>)
                header_row = table.select("thead tr")[1]
                headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

                # Read the table and set the headers
                df = pd.read_html(StringIO(str(table)), encoding="utf-8")[0]
                df.columns = headers
                
                # Fix encoding issues in player names
                df["Player"] = df["Player"].str.encode('latin1').str.decode('utf-8', errors='ignore')

                df = df.iloc[:table.select("tbody tr").__len__()]

                column_mapping = {
                    "S": "SOG", 
                    "EV": ["EVG", "EVA"],  # Two EV columns
                    "PP": ["PPG", "PPA"],  # Two PP columns
                    "SH": ["SHG", "SHA"],  # Two SH columns
                }
                
                column_names = list(df.columns)
                for i, col in enumerate(column_names):
                    if col == "EV":
                        column_names[i] = column_mapping["EV"].pop(0)
                    elif col == "PP":
                        column_names[i] = column_mapping["PP"].pop(0)
                    elif col == "SH":
                        column_names[i] = column_mapping["SH"].pop(0)
                    elif col == "S":
                        column_names[i] = column_mapping["S"]
                df.columns = column_names
                
                df = df[["Rk", "Player", "G", "A", "PTS", "SOG", "TOI", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA"]]
                
                if "TOI" in df.columns:
                    df["TOI"] = df["TOI"].apply(convert_toi_to_decimal)

                # Insert metadata columns              
                df.insert(0, "Season", "2024-25")
                df.insert(1, "Game", f"{home_team} vs {away_team}")
                df.insert(2, "GameID", game_id)
                df.insert(3, "Date", extract_date_from_game_id(game_id))     
                
                # Extract Player IDs from 'data-append-csv' attribute in <td> tags
                player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr td[data-append-csv]")]
                df.insert(df.columns.get_loc("Player") + 1, "PlayerID", player_ids + [None] * (len(df) - len(player_ids)))
                df.insert(df.columns.get_loc("Player") + 2, "Team", home_team if is_home else away_team)
                df.insert(df.columns.get_loc("Player") + 3, "TeamName", home_team_name if is_home else away_team_name)
                df.insert(df.columns.get_loc("Player") + 4, "Is_Home", 1 if is_home else 0)
                df.insert(df.columns.get_loc("Player") + 5, "Opp", away_team if is_home else home_team)
                df.insert(df.columns.get_loc("Player") + 6, "OppName", away_team_name if is_home else home_team_name)
                
                df = df.reindex(columns=skaters_columns, fill_value=None)

                skaters_data.append(df)

        # Extract advanced skaters table
        for team in [away_team, home_team]:
            table_selector = f"#{team}_adv_ALLAll"
            table = soup.select_one(table_selector)
            if table:
                # Read the table and set the headers
                df = pd.read_html(StringIO(str(table)), encoding="utf-8")[0]
                
                # Keep only rows within tbody
                df = df.iloc[:table.select("tbody tr").__len__()]

                # Insert metadata columns
                df.insert(0, "GameID", game_id)

                # Extract Player IDs from 'data-append-csv' attribute in <td> tags
                player_ids = [cell.get("data-append-csv") for cell in table.select("tbody tr th[data-append-csv]")]
                df["PlayerID"] = player_ids + [None] * (len(df) - len(player_ids))  # Handle rows without Player IDs

                adv_skaters_data.append(df)

        # Wait to avoid rate limiting
        time.sleep(3)
        
    except requests.RequestException as e:
        print(f"Error fetching data for game ID {game_id}: {e}")
    except Exception as e:
        print(f"Error processing data for game ID {game_id}: {e}")


# Merge skaters_data and adv_skaters_data
if skaters_data and adv_skaters_data:
    skaters_df = pd.concat(skaters_data, ignore_index=True)
    adv_skaters_df = pd.concat(adv_skaters_data, ignore_index=True)

    # Merge on PlayerID and GameID
    merged_df = skaters_df.merge(
        adv_skaters_df[["GameID", "PlayerID", "HIT", "BLK", "SAT‑F"]],
        on=["GameID", "PlayerID"],
        how="left"
    )
    
    merged_df = (
        merged_df.groupby(["GameID", "Team"])
        .head(18)
        .reset_index(drop=True)
    )

    # Reorder columns according to the specified schema
    merged_columns = [
        "Season", "Gm#", "Game", "GameID", "Date", "Player", "PlayerID", "Team", "TeamName", "Is_Home", "Opp", "OppName", "G", "A", "PTS", "SOG", "HIT", "BLK", "TOI", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA"
    ]
    merged_df = merged_df.reindex(columns=merged_columns)
    
    merged_df["Team"] = merged_df["Team"].replace("UTA", "ARI")
    merged_df["TeamName"] = merged_df["TeamName"].replace("Utah Hockey Club", "Arizona Coyotes")
    merged_df["Opp"] = merged_df["Opp"].replace("UTA", "ARI")
    merged_df["OppName"] = merged_df["OppName"].replace("Utah Hockey Club", "Arizona Coyotes")
    
# Load existing gamelogs.csv to get the max Gm# for each player
metrics_file_path = r"C:\Users\ashle\Documents\Projects\hockey\data\gamelogs.csv"
if os.path.exists(metrics_file_path):
    metrics_data = pd.read_csv(metrics_file_path, parse_dates=["Date"], low_memory=False)
else:
    metrics_data = pd.DataFrame(columns=["PlayerID", "Gm#", "Date"])

# Sort merged_df by PlayerID and Date to ensure chronological order
merged_df["Date"] = pd.to_datetime(merged_df["Date"], errors="coerce")
merged_df.sort_values(by=["PlayerID", "Date"], inplace=True)

# Get the max Gm# for each player from the existing data
max_game_nums = metrics_data.groupby("PlayerID")["Gm#"].max().fillna(0).to_dict()

def assign_game_number(row):
    player_id = row["PlayerID"]
    if player_id in max_game_nums:
        # Player exists in metrics_data
        return max_game_nums[player_id] + 1 + merged_df[
            (merged_df["PlayerID"] == player_id) & (merged_df["Date"] < row["Date"])
        ].shape[0]
    else:
        # New player, assign game numbers sequentially
        return merged_df[(merged_df["PlayerID"] == player_id)].groupby("PlayerID").cumcount().loc[row.name] + 1

# Apply the function to assign Gm#
merged_df["Gm#"] = merged_df.apply(assign_game_number, axis=1)


player_info = {
    "acciano01": ("Noel Acciari"),
    "addisca01": ("Calen Addison"),
    "afanaeg01": ("Egor Afanasyev"),
    "ahose01": ("Sebastian Aho"),
    "ahose02": ("Sebastian Aho"),
    "alexani01": ("Nikita Alexandrov"),
    "alexeal01": ("Alexander Alexeyev"),
    "allanno01": ("Nolan Allan"),
    "allenja01": ("Jake Allen"),
    "amadimi01": ("Michael Amadio"),
    "amanni01": ("Nils Aman"),
    "anderfr01": ("Frederik Andersen"),
    "anderja01": ("Jaret Anderson-Dolan"),
    "anderjo05": ("Josh Anderson"),
    "anderjo08": ("Joey Anderson"),
    "andermi02": ("Mikey Anderson"),
    "anderra01": ("Rasmus Andersson"),
    "andraem01": ("Emil Andrae"),
    "anglety01": ("Tyler Angle"),
    "annunju01": ("Justus Annunen"),
    "applema01": ("Mason Appleton"),
    "armiajo01": ("Joel Armia"),
    "arvidvi01": ("Viktor Arvidsson"),
    "astonza01": ("Zach Aston-Reese"),
    "athanan01": ("Andreas Athanasiou"),
    "atkinca01": ("Cam Atkinson"),
    "attarro01": ("Ronnie Attard"),
    "aubekni01": ("Nicolas Aube-Kubel"),
    "audymjo01": ("Jonathan Marchessault"),
    "backlmi01": ("Mikael Backlund"),
    "backos01": ("Oskar Back"),
    "backsni02": ("Nicklas Backstrom"),
    "bahlke01": ("Kevin Bahl"),
    "baileju01": ("Justin Bailey"),
    "bainsar01": ("Arshdeep Bains"),
    "balinuv01": ("Uvis Balinskis"),
    "barabal01": ("Alexander Barabanov"),
    "barbaiv01": ("Ivan Barbashev"),
    "barkoal01": ("Aleksander Barkov"),
    "barreal01": ("Alex Barre-Boulet"),
    "barrity01": ("Tyson Barrie"),
    "barroju01": ("Justin Barron"),
    "barromo01": ("Morgan Barron"),
    "barzama01": ("Mathew Barzal"),
    "bastina01": ("Nathan Bastian"),
    "bathedr01": ("Drake Batherson"),
    "beanja01": ("Jake Bean"),
    "bearet01": ("Ethan Bear"),
    "beauvan01": ("Anthony Beauvillier"),
    "beckmad01": ("Adam Beckman"),
    "bedarco01": ("Connor Bedard"),
    "beechjo01": ("John Beecher"),
    "belpelo01": ("Louis Belpedio"),
    "beniema01": ("Matty Beniers"),
    "bennesa01": ("Sam Bennett"),
    "bennima01": ("Matt Benning"),
    "bennja01": ("Jamie Benn"),
    "benoisi01": ("Simon Benoit"),
    "bensoza01": ("Zach Benson"),
    "berggjo02": ("Jonatan Berggren"),
    "bernaja01": ("Jacob Bernard-Docker"),
    "bertuty01": ("Tyler Bertuzzi"),
    "binnijo01": ("Jordan Binnington"),
    "birobr01": ("Brandon Biro"),
    "bjorkol01": ("Oliver Bjorkstrand"),
    "bjugsni01": ("Nick Bjugstad"),
    "blackco01": ("Colin Blackwell"),
    "blackma01": ("Mackenzie Blackwood"),
    "blakeja02": ("Jackson Blake"),
    "blankni01": ("Nick Blankenburg"),
    "blomqjo01": ("Joel Blomqvist"),
    "bluegte01": ("Teddy Blueger"),
    "blumema01": ("Matej Blumel"),
    "bobrose01": ("Sergei Bobrovsky"),
    "boesebr01": ("Brock Boeser"),
    "bogosza01": ("Zach Bogosian"),
    "boldusa01": ("Samuel Bolduc"),
    "bolduza01": ("Zachary Bolduc"),
    "boldyma01": ("Matt Boldy"),
    "boqviad01": ("Adam Boqvist"),
    "boqvije01": ("Jesper Boqvist"),
    "bordeth01": ("Thomas Bordeleau"),
    "borgewi01": ("Will Borgen"),
    "borturo01": ("Robert Bortuzzo"),
    "bouchev01": ("Evan Bouchard"),
    "bourqma01": ("Mavrik Bourque"),
    "boydtr01": ("Travis Boyd"),
    "branner01": ("Erik Brannstrom"),
    "brattje01": ("Jesper Bratt"),
    "brazeju01": ("Justin Brazeau"),
    "brindga01": ("Gavin Brindley"),
    "brinkbo01": ("Bobby Brink"),
    "brissbr01": ("Brendan Brisson"),
    "brobeph01": ("Philip Broberg"),
    "brodijo01": ("Jonas Brodin"),
    "broditj01": ("Tj Brodie"),
    "brodzjo01": ("Jonny Brodzinski"),
    "brownco02": ("Connor Brown"),
    "brownjo01": ("Josh Brown"),
    "brysoja01": ("Jacob Bryson"),
    "buchnpa01": ("Pavel Buchnevich"),
    "buntimi01": ("Michael Bunting"),
    "burakan01": ("Andre Burakovsky"),
    "burnsbr01": ("Brent Burns"),
    "burroky01": ("Kyle Burroughs"),
    "butleca01": ("Cameron Butler"),
    "byfiequ01": ("Quinton Byfield"),
    "byrambo01": ("Bowen Byram"),
    "caggidr01": ("Drake Caggiula"),
    "carcomi01": ("Michael Carcone"),
    "cardwet01": ("Ethan Cardwell"),
    "carlide01": ("Declan Carlile"),
    "carlobr01": ("Brandon Carlo"),
    "carlsjo01": ("John Carlson"),
    "carlsle01": ("Leo Carlsson"),
    "carrial01": ("Alexandre Carrier"),
    "carrisa01": ("Sam Carrick"),
    "carriwi01": ("William Carrier"),
    "carteje01": ("Jeff Carter"),
    "caseyse01": ("Seamus Casey"),
    "catesno01": ("Noah Cates"),
    "caufico01": ("Cole Caufield"),
    "cecico01": ("Cody Ceci"),
    "celebma01": ("Macklin Celebrini"),
    "cernaer01": ("Erik Cernak"),
    "chaboth01": ("Thomas Chabot"),
    "chaffmi01": ("Mitchell Chaffee"),
    "chartro01": ("Rourke Chartier"),
    "chatfja01": ("Jalen Chatfield"),
    "chiarbe01": ("Ben Chiarot"),
    "chibrni01": ("Nikita Chibrikov"),
    "chinaye01": ("Yegor Chinakhov"),
    "chishde01": ("Declan Chisholm"),
    "cholode01": ("Dennis Cholowski"),
    "chrisja01": ("Jake Christiansen"),
    "chychja01": ("Jakob Chychrun"),
    "chytifi01": ("Filip Chytil"),
    "cirelan01": ("Anthony Cirelli"),
    "cizikca01": ("Casey Cizikas"),
    "claguka01": ("Kale Clague"),
    "clarkbr02": ("Brandt Clarke"),
    "clarkgr01": ("Graeme Clarke"),
    "cliftco01": ("Connor Clifton"),
    "cluttca01": ("Cal Clutterbuck"),
    "coghldy01": ("Dylan Coghlan"),
    "coglian01": ("Andrew Cogliano"),
    "colansa01": ("Sam Colangelo"),
    "coleia01": ("Ian Cole"),
    "colembl01": ("Blake Coleman"),
    "coltoro01": ("Ross Colton"),
    "comphj.01": ("J.T. Compher"),
    "comrier01": ("Eric Comrie"),
    "condolu01": ("Lucas Condotta"),
    "connoky01": ("Kyle Connor"),
    "coolelo01": ("Logan Cooley"),
    "copleph01": ("Pheonix Copley"),
    "coppan01": ("Andrew Copp"),
    "cormilu01": ("Lukas Cormier"),
    "coronma01": ("Matt Coronato"),
    "cottepa01": ("Paul Cotter"),
    "cousini01": ("Nick Cousins"),
    "coutulo01": ("Logan Couture"),
    "coutuse01": ("Sean Couturier"),
    "coylech01": ("Charlie Coyle"),
    "cozendy01": ("Dylan Cozens"),
    "crevilo01": ("Louis Crevier"),
    "crookan01": ("Angus Crookshank"),
    "crosbsi01": ("Sidney Crosby"),
    "crottca01": ("Cameron Crotty"),
    "crousla01": ("Lawson Crouse"),
    "crozima01": ("Maxwell Crozier"),
    "cuyllwi01": ("Will Cuylle"),
    "czarnau01": ("Austin Czarnik"),
    "daccojo01": ("Joey Daccord"),
    "dachki01": ("Kirby Dach"),
    "dadonev01": ("Evgenii Dadonov"),
    "dahlira01": ("Rasmus Dahlin"),
    "danauph01": ("Phillip Danault"),
    "danfoju01": ("Justin Danforth"),
    "deanza01": ("Zach Dean"),
    "debrial01": ("Alex Debrincat"),
    "debruja01": ("Jake Debrusk"),
    "dehaaca01": ("Calvin De Haan"),
    "delbelu01": ("Luca Del Bel Belluz"),
    "delgama01": ("Marc Del Gaizo"),
    "dellaty01": ("Ty Dellandrea"),
    "delmaet01": ("Ethan Del Mastro"),
    "demeldy01": ("Dylan Demelo"),
    "dermotr01": ("Travis Dermott"),
    "deshavi01": ("Vincent Desharnais"),
    "deslani01": ("Nicolas Deslauriers"),
    "desmica01": ("Casey Desmith"),
    "dickija01": ("Jason Dickinson"),
    "digiuph01": ("Phillip Di Giuseppe"),
    "dillobr01": ("Brenden Dillon"),
    "doanjo01": ("Josh Doan"),
    "dobsono01": ("Noah Dobson"),
    "domima01": ("Max Domi"),
    "donatry01": ("Ryan Donato"),
    "dorofpa01": ("Pavel Dorofeyev"),
    "dostalu01": ("Lukas Dostal"),
    "doughdr01": ("Drew Doughty"),
    "dowdni01": ("Nic Dowd"),
    "dowliju01": ("Justin Dowling"),
    "draisle01": ("Leon Draisaitl"),
    "drouijo01": ("Jonathan Drouin"),
    "druryja01": ("Jack Drury"),
    "drysdja01": ("Jamie Drysdale"),
    "dubedi01": ("Dillon Dube"),
    "dubepi01": ("Pierrick Dube"),
    "duboipi01": ("Pierre-Luc Dubois"),
    "duchema01": ("Matt Duchene"),
    "duclaan01": ("Anthony Duclair"),
    "duehrwa01": ("Walker Duehr"),
    "duhaibr01": ("Brandon Duhaime"),
    "dumbama01": ("Matt Dumba"),
    "dumoubr01": ("Brian Dumoulin"),
    "dunnvi02": ("Vince Dunn"),
    "durzise01": ("Sean Durzi"),
    "dvorach01": ("Christian Dvorak"),
    "eberljo01": ("Jordan Eberle"),
    "edmunjo01": ("Joel Edmundson"),
    "edstrad01": ("Adam Edstrom"),
    "edvinsi01": ("Simon Edvinsson"),
    "ehlerni01": ("Nikolaj Ehlers"),
    "eicheja01": ("Jack Eichel"),
    "ekblaaa01": ("Aaron Ekblad"),
    "ekholma01": ("Mattias Ekholm"),
    "eklunwi01": ("William Eklund"),
    "ekmanol01": ("Oliver Ekman-Larsson"),
    "ellerla01": ("Lars Eller"),
    "emberty01": ("Ty Emberson"),
    "engluan01": ("Andreas Englund"),
    "engvapi01": ("Pierre Engvall"),
    "entwima01": ("Mackenzie Entwistle"),
    "eriksjo02": ("Joel Eriksson Ek"),
    "erssosa01": ("Samuel Ersson"),
    "evanglu01": ("Luke Evangelista"),
    "evansja02": ("Jake Evans"),
    "evansry01": ("Ryker Evans"),
    "eyssimi01": ("Michael Eyssimont"),
    "fabbrda01": ("Dante Fabbro"),
    "fabbrro01": ("Robby Fabbri"),
    "faberbr01": ("Brock Faber"),
    "faksara01": ("Radek Faksa"),
    "fantiad01": ("Adam Fantilli"),
    "farabjo01": ("Joel Farabee"),
    "faschhu01": ("Hudson Fasching"),
    "fastje01": ("Jesper Fast"),
    "faulkju01": ("Justin Faulk"),
    "fedotiv01": ("Ivan Fedotov"),
    "feherma01": ("Martin Fehervary"),
    "ferrama01": ("Mario Ferraro"),
    "fialake01": ("Kevin Fiala"),
    "fischch01": ("Christian Fischer"),
    "fixwotr01": ("Trey Fix-Wolansky"),
    "fleurca01": ("Cale Fleury"),
    "fleurha01": ("Haydn Fleury"),
    "fleurma01": ("Marc-Andre Fleury"),
    "foegewa01": ("Warren Foegele"),
    "foersty01": ("Tyson Foerster"),
    "foligma01": ("Marcus Foligno"),
    "foligni01": ("Nick Foligno"),
    "footeno01": ("Nolan Foote"),
    "forbode01": ("Derek Forbort"),
    "forsban01": ("Anton Forsberg"),
    "forsbfi01": ("Filip Forsberg"),
    "forslgu02": ("Gustav Forsling"),
    "foudyje01": ("Jean-Luc Foudy"),
    "foudyli01": ("Liam Foudy"),
    "fowleca01": ("Cam Fowler"),
    "foxad01": ("Adam Fox"),
    "fredetr01": ("Trent Frederic"),
    "froesby01": ("Byron Froese"),
    "frostmo01": ("Morgan Frost"),
    "gadjojo01": ("Jonah Gadjovich"),
    "gallabr01": ("Brendan Gallagher"),
    "gardnrh01": ("Rhett Gardner"),
    "garlaco01": ("Conor Garland"),
    "gaudead01": ("Adam Gaudette"),
    "gaudrfr01": ("Frederick Gaudreau"),
    "gaudrjo01": ("Johnny Gaudreau"),
    "gauncbr01": ("Brendan Gaunce"),
    "gauthcu01": ("Cutter Gauthier"),
    "gauthju01": ("Julien Gauthier"),
    "gavrivl01": ("Vladislav Gavrikov"),
    "gawdigl01": ("Glenn Gawdin"),
    "geekico01": ("Conor Geekie"),
    "geekimo01": ("Morgan Geekie"),
    "georgal01": ("Alexandar Georgiev"),
    "georgis01": ("Isaiah George"),
    "gignabr01": ("Brandon Gignac"),
    "gilbede01": ("Dennis Gilbert"),
    "gilespa01": ("Patrick Giles"),
    "ginniad01": ("Adam Ginning"),
    "giordma01": ("Mark Giordano"),
    "girarsa01": ("Samuel Girard"),
    "girgeze01": ("Zemgus Girgensons"),
    "giroucl01": ("Claude Giroux"),
    "glassco01": ("Cody Glass"),
    "glendlu01": ("Luke Glendening"),
    "goligal01": ("Alex Goligoski"),
    "goncaga01": ("Gage Goncalves"),
    "goodrba01": ("Barclay Goodrow"),
    "gostish01": ("Shayne Gostisbehere"),
    "gourdya01": ("Yanni Gourde"),
    "grafco01": ("Collin Graf"),
    "granlmi01": ("Mikael Granlund"),
    "gravery01": ("Ryan Graves"),
    "greenjo02": ("Jordan Greenway"),
    "greeraj01": ("A.J. Greer"),
    "gregono01": ("Noah Gregor"),
    "greigri01": ("Ridly Greig"),
    "grubaph01": ("Philipp Grubauer"),
    "grudejo02": ("Jonathan Gruden"),
    "grundca01": ("Carl Grundstrom"),
    "grzelma01": ("Matt Grzelcyk"),
    "gudasra01": ("Radko Gudas"),
    "gudbrer01": ("Erik Gudbranson"),
    "guenema01": ("Maxence Guenette"),
    "guentdy01": ("Dylan Guenther"),
    "guentja01": ("Jake Guentzel"),
    "guhleka01": ("Kaiden Guhle"),
    "gushcda01": ("Daniil Gushchin"),
    "gustada01": ("David Gustafsson"),
    "gustaer02": ("Erik Gustafsson"),
    "gustafi01": ("Filip Gustavsson"),
    "guttmco01": ("Cole Guttman"),
    "hagelbr01": ("Brandon Hagel"),
    "hagueni01": ("Nicolas Hague"),
    "hakanja01": ("Jani Hakanpaa"),
    "hallta02": ("Taylor Hall"),
    "halonbr01": ("Brian Halonen"),
    "hamanha01": ("Hardy Haman Aktell"),
    "hamblja01": ("James Hamblin"),
    "hamildo01": ("Dougie Hamilton"),
    "hamontr01": ("Travis Hamonic"),
    "hanifno01": ("Noah Hanifin"),
    "hanlejo01": ("Joel Hanley"),
    "harkija01": ("Jansen Harkins"),
    "harleth01": ("Thomas Harley"),
    "harrijo01": ("Jordan Harris"),
    "hartmry01": ("Ryan Hartman"),
    "harvera01": ("Rafael Harvey-Pinard"),
    "hataksa01": ("Santeri Hatakka"),
    "hathaga01": ("Garnet Hathaway"),
    "haulaer01": ("Erik Haula"),
    "haydejo01": ("John Hayden"),
    "hayeske01": ("Kevin Hayes"),
    "haytoba01": ("Barrett Hayton"),
    "hedmavi01": ("Victor Hedman"),
    "heineda01": ("Danton Heinen"),
    "heineem01": ("Emil Heineman"),
    "heiskmi01": ("Miro Heiskanen"),
    "helleco01": ("Connor Hellebuyck"),
    "henriad01": ("Adam Henrique"),
    "hertlto01": ("Tomas Hertl"),
    "hildede01": ("Dennis Hildeby"),
    "hillad01": ("Adin Hill"),
    "hintzro01": ("Roope Hintz"),
    "hirosak01": ("Akito Hirose"),
    "hischni01": ("Nico Hischier"),
    "hoferjo01": ("Joel Hofer"),
    "hoglani01": ("Nils Hoglander"),
    "hollju01": ("Justin Holl"),
    "hollody01": ("Dylan Holloway"),
    "holmbpo01": ("Pontus Holmberg"),
    "holmssi01": ("Simon Holmstrom"),
    "holtzal01": ("Alexander Holtz"),
    "honzesa01": ("Samuel Honzek"),
    "horvabo01": ("Bo Horvat"),
    "howdebr01": ("Brett Howden"),
    "hronefi01": ("Filip Hronek"),
    "huberjo01": ("Jonathan Huberdeau"),
    "hugheja03": ("Jack Hughes"),
    "hughelu01": ("Luke Hughes"),
    "hughequ01": ("Quinn Hughes"),
    "huntda01": ("Daemon Hunt"),
    "hussovi01": ("Ville Husso"),
    "hutsola01": ("Lane Hutson"),
    "huttobe01": ("Ben Hutton"),
    "huttogr01": ("Grant Hutton"),
    "hymanza01": ("Zach Hyman"),
    "iafalal01": ("Alex Iafallo"),
    "ingraco01": ("Connor Ingram"),
    "ioriovi01": ("Vincent Iorio"),
    "iskharu01": ("Ruslan Iskhakov"),
    "ivaniv01": ("Ivan Ivan"),
    "jankoma01": ("Mark Jankowski"),
    "janmama02": ("Mattias Janmark"),
    "jarnkca01": ("Calle Jarnkrok"),
    "jarrytr01": ("Tristan Jarry"),
    "jarvero01": ("Roby Jarventie"),
    "jarvise01": ("Seth Jarvis"),
    "jeannta01": ("Tanner Jeannot"),
    "jenikja01": ("Jan Jenik"),
    "jennebo01": ("Boone Jenner"),
    "jenseni02": ("Nick Jensen"),
    "jiricda01": ("David Jiricek"),
    "johanal01": ("Albert Johansson"),
    "johanjo03": ("Jonas Johansson"),
    "johanlu01": ("Lucas Johansen"),
    "johanma03": ("Marcus Johansson"),
    "johnser01": ("Erik Johnson"),
    "johnsja02": ("Jack Johnson"),
    "johnske01": ("Kent Johnson"),
    "johnsma04": ("Marc Johnstone"),
    "johnsre01": ("Reese Johnson"),
    "johnsro02": ("Ross Johnston"),
    "johnsry03": ("Ryan Johnson"),
    "johnsty01": ("Tyler Johnson"),
    "johnswy01": ("Wyatt Johnston"),
    "jokihhe01": ("Henri Jokiharju"),
    "jonesca01": ("Caleb Jones"),
    "jonesma03": ("Max Jones"),
    "jonesse01": ("Seth Jones"),
    "jonesza01": ("Zac Jones"),
    "jonssax01": ("Axel Jonsson-Fjallby"),
    "josepma01": ("Mathieu Joseph"),
    "joseppi01": ("Pierre-Olivier Joseph"),
    "joshuda01": ("Dakota Joshua"),
    "josiro01": ("Roman Josi"),
    "juulsno01": ("Noah Juulsen"),
    "kadrina01": ("Nazem Kadri"),
    "kahkoka01": ("Kaapo Kahkonen"),
    "kaisewy01": ("Wyatt Kaiser"),
    "kakkoka01": ("Kaapo Kakko"),
    "kaliyar01": ("Arthur Kaliyev"),
    "kampfda01": ("David Kampf"),
    "kaneev01": ("Evander Kane"),
    "kanepa01": ("Patrick Kane"),
    "kapanka01": ("Kasperi Kapanen"),
    "kapanol01": ("Oliver Kapanen"),
    "kapriki01": ("Kirill Kaprizov"),
    "karlser01": ("Erik Karlsson"),
    "karlsli01": ("Linus Karlsson"),
    "karlswi01": ("William Karlsson"),
    "kartyty01": ("Tye Kartye"),
    "kaspema01": ("Marco Kasper"),
    "kastema01": ("Mark Kastelic"),
    "kelemmi01": ("Milos Kelemen"),
    "kellecl01": ("Clayton Keller"),
    "kellypa01": ("Parker Kelly"),
    "kempead01": ("Adrian Kempe"),
    "kempph01": ("Philip Kemp"),
    "kerfoal01": ("Alex Kerfoot"),
    "kessema01": ("Matthew Kessel"),
    "kessemi01": ("Michael Kesselring"),
    "khusnma01": ("Marat Khusnutdinov"),
    "killoal01": ("Alex Killorn"),
    "kirklju01": ("Justin Kirkland"),
    "kivirjo01": ("Joel Kiviranta"),
    "klapkad01": ("Adam Klapka"),
    "klevety01": ("Tyler Kleven"),
    "kniesma01": ("Matthew Knies"),
    "knighsp01": ("Spencer Knight"),
    "knyzhni01": ("Nikolai Knyzhov"),
    "kochepy01": ("Pyotr Kochetkov"),
    "kochpa01": ("Patrik Koch"),
    "koepkco01": ("Cole Koepke"),
    "koleske01": ("Keegan Kolesar"),
    "kolosal01": ("Aleksei Kolosov"),
    "kolyavl01": ("Vladislav Kolyachonok"),
    "konectr01": ("Travis Konecny"),
    "kopitan01": ("Anze Kopitar"),
    "korchke01": ("Kevin Korchinski"),
    "korczka01": ("Kaedan Korczak"),
    "korpijo01": ("Joonas Korpisalo"),
    "kostikl01": ("Klim Kostin"),
    "kotkaje01": ("Jesperi Kotkaniemi"),
    "kovacjo01": ("Johnathan Kovacevic"),
    "kovalni01": ("Nikolai Kovalenko"),
    "krebspe01": ("Peyton Krebs"),
    "kreidch01": ("Chris Kreider"),
    "krugto01": ("Torey Krug"),
    "kucheni01": ("Nikita Kucherov"),
    "kuempda01": ("Darcy Kuemper"),
    "kulakbr01": ("Brett Kulak"),
    "kulicji01": ("Jiri Kulich"),
    "kulikdm01": ("Dmitry Kulikov"),
    "kuninlu01": ("Luke Kunin"),
    "kuparra01": ("Rasmus Kupari"),
    "kuralse01": ("Sean Kuraly"),
    "kurasph01": ("Philipp Kurashev"),
    "kuzmean01": ("Andrei Kuzmenko"),
    "kuzneya01": ("Yan Kuznetsov"),
    "kylinol01": ("Oliver Kylington"),
    "kyroujo01": ("Jordan Kyrou"),
    "labanke01": ("Kevin Labanc"),
    "labersa01": ("Samuel Laberge"),
    "lacomja01": ("Jackson Lacombe"),
    "laferal01": ("Alex Laferriere"),
    "laffesa01": ("Sam Lafferty"),
    "lafreal01": ("Alexis Lafreniere"),
    "lainepa01": ("Patrik Laine"),
    "lambebr01": ("Brad Lambert"),
    "lamouma01": ("Maveric Lamoureux"),
    "lankike01": ("Kevin Lankinen"),
    "lapiehe01": ("Hendrix Lapierre"),
    "larkidy01": ("Dylan Larkin"),
    "larssad01": ("Adam Larsson"),
    "laughsc01": ("Scott Laughton"),
    "laukoja01": ("Jakub Lauko"),
    "lauzoje01": ("Jeremy Lauzon"),
    "lavoira01": ("Raphael Lavoie"),
    "lazarcu01": ("Curtis Lazar"),
    "leasobr01": ("Brett Leason"),
    "leddyni01": ("Nick Leddy"),
    "leean01": ("Anders Lee"),
    "leean02": ("Andre Lee"),
    "lehkoar01": ("Artturi Lehkonen"),
    "letankr01": ("Kris Letang"),
    "levide01": ("Devon Levi"),
    "lewistr01": ("Trevor Lewis"),
    "lheurza01": ("Zachary L'Heureux"),
    "liljeti01": ("Timothy Liljegren"),
    "lindbos01": ("Oskar Lindblom"),
    "lindees01": ("Esa Lindell"),
    "lindgch01": ("Charlie Lindgren"),
    "lindgry01": ("Ryan Lindgren"),
    "lindhel01": ("Elias Lindholm"),
    "lindhha01": ("Hampus Lindholm"),
    "lindko01": ("Kole Lind"),
    "lizotbl01": ("Blake Lizotte"),
    "lohrema01": ("Mason Lohrei"),
    "lombery01": ("Ryan Lomberg"),
    "lorenst01": ("Steven Lorentz"),
    "lowryad01": ("Adam Lowry"),
    "luchaje01": ("Jett Luchanko"),
    "ludvijo01": ("John Ludvig"),
    "lundean01": ("Anton Lundell"),
    "lundeis01": ("Isac Lundestrom"),
    "lundkni01": ("Nils Lundkvist"),
    "luneatr01": ("Tristan Luneau"),
    "luostee01": ("Eetu Luostarinen"),
    "luukkuk01": ("Ukko-Pekka Luukkonen"),
    "lycksol01": ("Olle Lycksell"),
    "lyonal01": ("Alex Lyon"),
    "lyubuil01": ("Ilya Lyubushkin"),
    "maattol01": ("Olli Maatta"),
    "maccema01": ("Matias Maccelli"),
    "macdeku01": ("Kurtis MacDermid"),
    "maceama01": ("Mackenzie MacEachern"),
    "macewza01": ("Zack MacEwen"),
    "mackina01": ("Nathan MacKinnon"),
    "macleky01": ("Kyle MacLean"),
    "mahurjo01": ("Josh Mahura"),
    "mailllo01": ("Logan Mailloux"),
    "makarca01": ("Cale Makar"),
    "malatja01": ("James Malatesta"),
    "malenbe01": ("Beck Malenstyn"),
    "malinsa01": ("Sam Malinski"),
    "malkiev01": ("Evgeni Malkin"),
    "mancivi01": ("Victor Mancini"),
    "mangian01": ("Andrew Mangiapane"),
    "mansojo01": ("Josh Manson"),
    "manthan01": ("Anthony Mantha"),
    "marchbr03": ("Brad Marchand"),
    "marchki01": ("Kirill Marchenko"),
    "marchma01": ("Mason Marchment"),
    "marinjo01": ("John Marino"),
    "marksja02": ("Jacob Markstrom"),
    "marnemi01": ("Mitch Marner"),
    "maroopa01": ("Pat Maroon"),
    "martial01": ("Alec Martinez"),
    "martiem01": ("Emil Lilleberg"),
    "martijo01": ("Jordan Martinook"),
    "martima02": ("Matt Martin"),
    "mathemi01": ("Mike Matheson"),
    "matinni01": ("Nikolas Matinpalo"),
    "matthau01": ("Auston Matthews"),
    "mayfisc01": ("Scott Mayfield"),
    "mcavoch01": ("Charlie McAvoy"),
    "mcbaija03": ("Jack McBain"),
    "mccabja01": ("Jake McCabe"),
    "mccanja01": ("Jared McCann"),
    "mccarmi01": ("Michael McCarron"),
    "mccorma01": ("Max McCormick"),
    "mcdavco01": ("Connor McDavid"),
    "mcdonry01": ("Ryan McDonagh"),
    "mcginbr01": ("Brock McGinn"),
    "mcginhu01": ("Hugh McGing"),
    "mcgroru01": ("Rutger McGroarty"),
    "mcilrdy01": ("Dylan McIlrath"),
    "mclauma01": ("Marc McLaughlin"),
    "mcleomi01": ("Michael McLeod"),
    "mcleory01": ("Ryan McLeod"),
    "mcmanbo02": ("Bobby McMann"),
    "mcmicco01": ("Connor McMichael"),
    "mcnabbr01": ("Brayden McNabb"),
    "mctavma01": ("Mason McTavish"),
    "mcwarco01": ("Cole McWard"),
    "meierti01": ("Timo Meier"),
    "merceda01": ("Dawson Mercer"),
    "merelwa01": ("Waltteri Merela"),
    "merkuge01": ("Georgii Merkulov"),
    "mermida01": ("Dakota Mermis"),
    "merrijo01": ("Jon Merrill"),
    "merzlel01": ("Elvis Merzlikins"),
    "meyerca01": ("Carson Meyer"),
    "michkma01": ("Matvei Michkov"),
    "middlja01": ("Jake Middleton"),
    "mikheil01": ("Ilya Mikheyev"),
    "mikkoni01": ("Niko Mikkola"),
    "milanso01": ("Sonny Milano"),
    "milleco02": ("Colin Miller"),
    "millejt01": ("J.T. Miller"),
    "milleka01": ("K'Andre Miller"),
    "mintefr01": ("Fraser Minten"),
    "mintypa01": ("Pavel Mintyukov"),
    "miromda01": ("Daniil Miromanov"),
    "mirosiv01": ("Ivan Miroshnichenko"),
    "misyuda01": ("Daniil Misyul"),
    "mitteca01": ("Casey Mittelstadt"),
    "monahse01": ("Sean Monahan"),
    "montesa01": ("Sam Montembeault"),
    "montobr01": ("Brandon Montour"),
    "mooretr01": ("Trevor Moore"),
    "morelma01": ("Mason Morelli"),
    "morrijo04": ("Josh Morrissey"),
    "morrilo01": ("Logan Morrison"),
    "morrosc02": ("Scott Morrow"),
    "moserja01": ("J.J. Moser"),
    "mottety01": ("Tyler Motte"),
    "moverja01": ("Jacob Moverare"),
    "mrazepe01": ("Petr Mrazek"),
    "mukhash01": ("Shakir Mukhamadullin"),
    "murphco02": ("Connor Murphy"),
    "murrabr02": ("Brett Murray"),
    "myersph01": ("Philippe Myers"),
    "myersty01": ("Tyler Myers"),
    "nadeabr01": ("Bradly Nadeau"),
    "namesvl01": ("Vladislav Namestnikov"),
    "nashri02": ("Riley Nash"),
    "nazarfr01": ("Frank Nazar"),
    "necasma01": ("Martin Necas"),
    "nedelal01": ("Alex Nedeljkovic"),
    "neighja01": ("Jake Neighbours"),
    "nelsobr01": ("Brock Nelson"),
    "nemecsi01": ("Simon Nemec"),
    "nesteni02": ("Nikita Nesterenko"),
    "newhoal01": ("Alex Newhook"),
    "nichuva01": ("Valeri Nichushkin"),
    "niedeni01": ("Nino Niederreiter"),
    "nietoma01": ("Matt Nieto"),
    "noesest01": ("Stefan Noesen"),
    "norrijo01": ("Josh Norris"),
    "nosekto01": ("Tomas Nosek"),
    "novakth01": ("Tommy Novak"),
    "nugenry01": ("Ryan Nugent-Hopkins"),
    "nurseda01": ("Darnell Nurse"),
    "nylanwi01": ("William Nylander"),
    "nyquigu01": ("Gustav Nyquist"),
    "obrieli01": ("Liam O'Brien"),
    "oconndr01": ("Drew O'Connor"),
    "oconnlo01": ("Logan O'Connor"),
    "oettija01": ("Jake Oettinger"),
    "ohgreli01": ("Liam Ohgren"),
    "olausos01": ("Oskar Olausson"),
    "oleksja01": ("Jamie Oleksiak"),
    "olivima01": ("Mathieu Olivier"),
    "olofsgu01": ("Gustav Olofsson"),
    "olofsvi01": ("Victor Olofsson"),
    "oreilry01": ("Ryan O'Reilly"),
    "orlovdm01": ("Dmitry Orlov"),
    "oshietj01": ("T.J. Oshie"),
    "ostapza01": ("Zack Ostapchuk"),
    "othmabr01": ("Brennan Othmann"),
    "ovechal01": ("Alex Ovechkin"),
    "pachabr01": ("Brayden Pachal"),
    "pacioma01": ("Max Pacioretty"),
    "pageaje01": ("Jean-Gabriel Pageau"),
    "palaton01": ("Ondrej Palat"),
    "palmiky01": ("Kyle Palmieri"),
    "panarar01": ("Artemi Panarin"),
    "parayco01": ("Colton Parayko"),
    "parssju01": ("Juuso Parssinen"),
    "pastrda01": ("David Pastrnak"),
    "paulni01": ("Nicholas Paul"),
    "paveljo01": ("Joe Pavelski"),
    "pavelon02": ("Ondrej Pavel"),
    "pearsta01": ("Tanner Pearson"),
    "peekean01": ("Andrew Peeke"),
    "pelecad01": ("Adam Pelech"),
    "pelleja01": ("Jakob Pelletier"),
    "perbini01": ("Nick Perbix"),
    "perfeco01": ("Cole Perfetti"),
    "perroda01": ("David Perron"),
    "perryco01": ("Corey Perry"),
    "perunsc01": ("Scott Perunovich"),
    "pescebr01": ("Brett Pesce"),
    "petanni01": ("Nic Petan"),
    "peterjo01": ("Jj Peterka"),
    "petroal01": ("Alexander Petrovic"),
    "petryje01": ("Jeff Petry"),
    "petteel01": ("Elias Pettersson"),
    "pettema01": ("Marcus Pettersson"),
    "pezzemi01": ("Michael Pezzetta"),
    "phillis01": ("Isaak Phillips"),
    "philpno01": ("Noah Philp"),
    "pickaca01": ("Calvin Pickard"),
    "pietral01": ("Alex Pietrangelo"),
    "pintosh01": ("Shane Pinto"),
    "pionkne01": ("Neal Pionk"),
    "podkova01": ("Vasily Podkolzin"),
    "poehlry01": ("Ryan Poehling"),
    "pointbr01": ("Brayden Point"),
    "poitrma01": ("Matthew Poitras"),
    "polinja01": ("Jason Polin"),
    "ponomva01": ("Vasiliy Ponomarev"),
    "pospima01": ("Martin Pospisil"),
    "poturan01": ("Andrew Poturalski"),
    "poulisa01": ("Sam Poulin"),
    "powerow01": ("Owen Power"),
    "primeca01": ("Cayden Primeau"),
    "prishni01": ("Nikita Prishchepov"),
    "protaal01": ("Aliaksei Protas"),
    "provoiv01": ("Ivan Provorov"),
    "puljuje01": ("Jesse Puljujarvi"),
    "pulocry01": ("Ryan Pulock"),
    "puustva01": ("Valtteri Puustinen"),
    "pyyhtmi01": ("Mikael Pyyhtia"),
    "quickjo01": ("Jonathan Quick"),
    "quinnja01": ("Jack Quinn"),
    "raddyda01": ("Darren Raddysh"),
    "raddyta01": ("Taylor Raddysh"),
    "rakelri01": ("Rickard Rakell"),
    "rantami01": ("Mikko Rantanen"),
    "rasmumi01": ("Michael Rasmussen"),
    "ratyaa01": ("Aatu Raty"),
    "ratyak01": ("Aku Raty"),
    "raymolu01": ("Lucas Raymond"),
    "reavery01": ("Ryan Reaves"),
    "regenpa01": ("Pavol Regenda"),
    "reichlu01": ("Lukas Reichel"),
    "reillmi01": ("Mike Reilly"),
    "reimeja01": ("James Reimer"),
    "reinhco01": ("Cole Reinhardt"),
    "reinhsa01": ("Sam Reinhart"),
    "rempash01": ("Sheldon Rempal"),
    "rempema01": ("Matt Rempe"),
    "riellmo01": ("Morgan Rielly"),
    "rifaima01": ("Marshall Rifai"),
    "ristora01": ("Rasmus Ristolainen"),
    "ritchca01": ("Calum Ritchie"),
    "rittida01": ("David Rittich"),
    "roberja01": ("Jason Robertson"),
    "roberni01": ("Nicholas Robertson"),
    "robiner01": ("Eric Robinson"),
    "rodriev01": ("Evan Rodrigues"),
    "romanal01": ("Alexander Romanov"),
    "rondbjo01": ("Jonas Rondbjerg"),
    "rooneke01": ("Kevin Rooney"),
    "roosfi01": ("Filip Roos"),
    "rosenca01": ("Calle Rosen"),
    "rosenis01": ("Isak Rosen"),
    "rosloja01": ("Jack Roslovic"),
    "rossima01": ("Marco Rossi"),
    "rouselu01": ("Lukas Rousek"),
    "royjo01": ("Joshua Roy"),
    "royma04": ("Matt Roy"),
    "royni01": ("Nicolas Roy"),
    "ruhwech01": ("Chad Ruhwedel"),
    "rustbr01": ("Bryan Rust"),
    "ruttaja02": ("Jan Rutta"),
    "ryande01": ("Derek Ryan"),
    "saadbr01": ("Brandon Saad"),
    "sabousc01": ("Scott Sabourin"),
    "sambedy01": ("Dylan Samberg"),
    "samosma01": ("Mackie Samoskevich"),
    "samsoil01": ("Ilya Samsonov"),
    "samuema02": ("Mattias Samuelsson"),
    "sandeja01": ("Jake Sanderson"),
    "sandira01": ("Rasmus Sandin"),
    "sanhetr01": ("Travis Sanheim"),
    "sarosju01": ("Juuse Saros"),
    "savarda01": ("David Savard"),
    "savoima01": ("Matt Savoie"),
    "scandma01": ("Marco Scandella"),
    "scanlbr01": ("Brandon Scanlin"),
    "scheima01": ("Mark Scheifele"),
    "schenbr01": ("Brayden Schenn"),
    "schenlu01": ("Luke Schenn"),
    "schmani01": ("Nick Schmaltz"),
    "schmina01": ("Nate Schmidt"),
    "schnebr01": ("Braden Schneider"),
    "schulju01": ("Justin Schultz"),
    "schwaja01": ("Jaden Schwartz"),
    "schwico01": ("Cole Schwindt"),
    "seeleni01": ("Nick Seeler"),
    "seguity01": ("Tyler Seguin"),
    "seidemo01": ("Moritz Seider"),
    "seneybr01": ("Brett Seney"),
    "sergami01": ("Mikhail Sergachev"),
    "severda01": ("Damon Severson"),
    "sgarbmi01": ("Michael Sgarbossa"),
    "sharaye01": ("Yegor Sharangovich"),
    "shawma01": ("Mason Shaw"),
    "shearco01": ("Conor Sheary"),
    "sheary01": ("Ryan Shea"),
    "sherwki01": ("Kiefer Sherwood"),
    "shestig01": ("Igor Shesterkin"),
    "siegejo01": ("Jonas Siegenthaler"),
    "silfvja01": ("Jakob Silfverberg"),
    "sillico01": ("Cole Sillinger"),
    "silovar01": ("Arturs Silovs"),
    "sissoco01": ("Colton Sissons"),
    "skinnje01": ("Jeff Skinner"),
    "skinnst01": ("Stuart Skinner"),
    "skjeibr01": ("Brady Skjei"),
    "slafkju01": ("Juraj Slafkovsky"),
    "slaggla01": ("Landon Slaggert"),
    "slavija01": ("Jaccob Slavin"),
    "smejkji01": ("Jiri Smejkal"),
    "smithbr05": ("Brendan Smith"),
    "smithco02": ("Cole Smith"),
    "smithcr01": ("Craig Smith"),
    "smithgi01": ("Givani Smith"),
    "smithre01": ("Reilly Smith"),
    "smithwi01": ("Will Smith"),
    "snivejo01": ("Joe Snively"),
    "soderar01": ("Arvid Soderblom"),
    "sodervi01": ("Victor Soderstrom"),
    "sogaama01": ("Mads Sogaard"),
    "solovil01": ("Ilya Solovyov"),
    "sorokil01": ("Ilya Sorokin"),
    "soucyca01": ("Carson Soucy"),
    "sourdju01": ("Justin Sourdif"),
    "spencjo01": ("Jordan Spence"),
    "spronda01": ("Daniel Sprong"),
    "spurgja01": ("Jared Spurgeon"),
    "staaljo01": ("Jordan Staal"),
    "stamkst01": ("Steven Stamkos"),
    "stanklo01": ("Logan Stankoven"),
    "stanllo01": ("Logan Stanley"),
    "stastsp01": ("Spencer Stastney"),
    "stechtr01": ("Troy Stecher"),
    "steelsa01": ("Sam Steel"),
    "steenos01": ("Oskar Steen"),
    "steeval02": ("Alex Steeves"),
    "stenlke01": ("Kevin Stenlund"),
    "stephch02": ("Chandler Stephenson"),
    "stephmi01": ("Mitchell Stephens"),
    "stienma01": ("Matt Stienburg"),
    "stivajo01": ("Jack St. Ivany"),
    "stolaan01": ("Anthony Stolarz"),
    "stonema01": ("Mark Stone"),
    "stromdy01": ("Dylan Strome"),
    "stromry01": ("Ryan Strome"),
    "strubja01": ("Jayden Struble"),
    "stuetti02": ("Tim Stutzle"),
    "sturmni01": ("Nico Sturm"),
    "sundqos01": ("Oskar Sundqvist"),
    "suterpi01": ("Pius Suter"),
    "suterry01": ("Ryan Suter"),
    "suzukni01": ("Nick Suzuki"),
    "svechan01": ("Andrei Svechnikov"),
    "swaymje01": ("Jeremy Swayman"),
    "szubema01": ("Maksymilian Szuber"),
    "talboca01": ("Cam Talbot"),
    "tanevbr01": ("Brandon Tanev"),
    "tanevch01": ("Chris Tanev"),
    "tarasda02": ("Daniil Tarasov"),
    "tarasvl01": ("Vladimir Tarasenko"),
    "tatarto01": ("Tomas Tatar"),
    "tavarjo01": ("John Tavares"),
    "teravte01": ("Teuvo Teravainen"),
    "terrytr01": ("Troy Terry"),
    "texieal01": ("Alexandre Texier"),
    "theodsh01": ("Shea Theodore"),
    "thomaak01": ("Akil Thomas"),
    "thomaro01": ("Robert Thomas"),
    "thompja01": ("Jack Thompson"),
    "thomplo01": ("Logan Thompson"),
    "thompta01": ("Tage Thompson"),
    "thrunhe01": ("Henry Thrun"),
    "timmico01": ("Conor Timmins"),
    "tinorja01": ("Jarred Tinordi"),
    "tippeow01": ("Owen Tippett"),
    "tkachbr01": ("Brady Tkachuk"),
    "tkachma01": ("Matthew Tkachuk"),
    "toewsde01": ("Devon Toews"),
    "toffoty01": ("Tyler Toffoli"),
    "tolvaee01": ("Eeli Tolvanen"),
    "tomasph01": ("Philip Tomasino"),
    "tonindo01": ("Dominic Toninato"),
    "toropal01": ("Alexey Toropchenko"),
    "treniya01": ("Yakov Trenin"),
    "trochvi01": ("Vincent Trocheck"),
    "troubja01": ("Jacob Trouba"),
    "tsyplma01": ("Maxim Tsyplakov"),
    "tuchal01": ("Alex Tuch"),
    "tuckety01": ("Tyler Tucker"),
    "tufteri01": ("Riley Tufte"),
    "turcoal02": ("Alex Turcotte"),
    "tynant.01": ("T.J. Tynan"),
    "ullmali01": ("Linus Ullmark"),
    "vaakaur01": ("Urho Vaakanainen"),
    "valimju01": ("Juuso Valimaki"),
    "vanecvi01": ("Vitek Vanecek"),
    "vanrija01": ("James Van Riemsdyk"),
    "vanritr01": ("Trevor Van Riemsdyk"),
    "varlasi01": ("Semyon Varlamov"),
    "vasilan02": ("Andrei Vasilevskiy"),
    "vatrafr01": ("Frank Vatrano"),
    "vejmeka01": ("Karel Vejmelka"),
    "velenjo01": ("Joe Veleno"),
    "verhaca01": ("Carter Verhaeghe"),
    "veseyji02": ("Jimmy Vesey"),
    "vilarga01": ("Gabriel Vilardi"),
    "vladada01": ("Daniel Vladar"),
    "vlasial01": ("Alex Vlasic"),
    "vlasima01": ("Marc-Edouard Vlasic"),
    "vorondi01": ("Dmitri Voronkov"),
    "vranaja01": ("Jakub Vrana"),
    "wagnech01": ("Chris Wagner"),
    "wahlsol01": ("Oliver Wahlstrom"),
    "walkena01": ("Nathan Walker"),
    "walkesa01": ("Sammy Walker"),
    "walkese01": ("Sean Walker"),
    "walmaja01": ("Jake Walman"),
    "watsoau01": ("Austin Watson"),
    "wedgesc01": ("Scott Wedgewood"),
    "weegama01": ("Mackenzie Weegar"),
    "wennbal01": ("Alex Wennberg"),
    "werenza01": ("Zach Werenski"),
    "whiteza01": ("Zach Whitecloud"),
    "wilsoto01": ("Tom Wilson"),
    "wintery01": ("Ryan Winterton"),
    "wolfdu01": ("Dustin Wolf"),
    "wolljo01": ("Joseph Woll"),
    "woodmi01": ("Miles Wood"),
    "wothepa01": ("Parker Wotherspoon"),
    "wrighsh01": ("Shane Wright"),
    "xhekaar01": ("Arber Xhekaj"),
    "yamamka01": ("Kailer Yamamoto"),
    "yloneje01": ("Jesse Ylonen"),
    "yorkca01": ("Cam York"),
    "zachapa01": ("Pavel Zacha"),
    "zadorni01": ("Nikita Zadorov"),
    "zamulye01": ("Yegor Zamula"),
    "zaryco01": ("Connor Zary"),
    "zegratr01": ("Trevor Zegras"),
    "zellwol01": ("Olen Zellweger"),
    "zettefa01": ("Fabian Zetterlund"),
    "zibanmi01": ("Mika Zibanejad"),
    "zubar01": ("Artem Zub"),
    "zuccama01": ("Mats Zuccarello"),
    "zuckeja01": ("Jason Zucker"),
    "helensa02": ("Samuel Helenius"),
    "jostty01": ("Tyson Jost"),
    "richaan01": ("Anthony Richard"),
    "dewarco01": ("Connor Dewar"),
    "lekkejo01": ("Jonathan Lekkerimaki"),
    "denisgr01": ("Grigori Denisenko"),
    "oestejo01": ("Jordan Oesterle"),
    "helledr01": ("Drew Helleson"),
    "schueco01": ("Corey Schueneman"),
    "pickeow01": ("Owen Pickering"),
    "milnemi01": ("Michael Milne"),
    "brownpa02": ("Patrick Brown"),
    "meyerbe01": ("Ben Meyers"),
    "vielje01": ("Jeffrey Viel"),
    "granshe01": ("Helge Grans"),
    "jonesbe01": ("Ben Jones"),
    "burkeca01": ("Callahan Burke"),
    "haggro01": ("Robert Hagg"),
    "bowersh01": ("Shane Bowers"),
    "shorede01": ("Devin Shore"),
    "grebeni01": ("Nikita Grebenkin"),
    "sassoma01": ("Max Sasson"),
    "svechfe01": ("Fedor Svechkov"),
    "nylanal01": ("Alexander Nylander"),
    "berarbr02": ("Brett Berard"),
    "heinovi01": ("Ville Heinola"),
    "bradlch01": ("Chase Bradley"),
    "wilsbad01": ("Adam Wilsby"),
    "hardmmi01": ("Mike Hardman"),
    "legarna01": ("Nathan Legare")
}

# Replace player names for those found in player_info
merged_df["Player"] = merged_df["PlayerID"].map(player_info).fillna(merged_df["Player"])

# Save the updated gamelogs
final_gamelogs_path = os.path.join(data_path, "gamelogs.csv")
merged_df.to_csv(final_gamelogs_path, mode='a', index=False, header=False, encoding="utf-8")
print(f"Updated gamelogs saved to {final_gamelogs_path}")

# Create gameIndex.csv
game_index_data = (
    merged_df.groupby(["GameID", "Season", "Date", "Game", "Team", "Is_Home", "TeamName"])
    .agg({"G": "sum"})  # Sum goals for each team
    .reset_index()
)

# Split into Home and Away data
home_data = game_index_data[game_index_data["Is_Home"] == 1].rename(
    columns={"Team": "HomeID", "G": "G", "TeamName": "Home"}
)
away_data = game_index_data[game_index_data["Is_Home"] == 0].rename(
    columns={"Team": "AwayID", "G": "GA", "TeamName": "Away"}
)

# Merge Home and Away data for each game
game_index = pd.merge(
    home_data[["GameID", "Season", "Date", "Game", "Home", "HomeID", "G"]],
    away_data[["GameID", "Away", "AwayID", "GA"]],
    on="GameID",
    how="inner"
)

# Reorder columns
game_index = game_index[
    ["Season", "Date", "Game", "GameID", "Home", "HomeID", "G", "Away", "AwayID", "GA"]
]

# Save to gameIndex.csv
game_index_file_path = os.path.join(data_path, "gameindex.csv")
game_index.to_csv(game_index_file_path, mode='a', index=False, header=False, encoding="utf-8")
print(f"Game index saved to {game_index_file_path}")


# Aggregate team-level statistics
team_stats = (
    merged_df.groupby(["GameID", "Team", "Is_Home", "TeamName", "Opp"])
    .agg({
        "G": "sum",
        "A": "sum",
        "PTS": "sum",
        "SOG": "sum",
        "HIT": "sum",
        "BLK": "sum"
    })
    .reset_index()
)

# Prepare opponent stats
opponent_stats = team_stats.rename(
    columns={
        "G": "GA", "A": "AA", "PTS": "PTSA", "SOG": "SOGA", "HIT": "HITA", "BLK": "BLKA",
        "Team": "OppID", "TeamName": "OppName"
    }
)

# Merge team stats with opponent stats
team_gamelogs = pd.merge(
    team_stats,
    opponent_stats[["GameID", "OppID", "GA", "AA", "PTSA", "SOGA", "HITA", "BLKA"]],
    left_on=["GameID", "Opp"],
    right_on=["GameID", "OppID"],
    how="inner"
)

# Drop redundant columns
team_gamelogs = team_gamelogs.drop(columns=["OppID"])

# Add season and date columns from the original merged_df
game_info = merged_df[["GameID", "Season", "Date"]].drop_duplicates()
team_gamelogs = pd.merge(team_gamelogs, game_info, on="GameID", how="left")

# Rename and reorder columns
team_gamelogs = team_gamelogs.rename(columns={"TeamName": "Team", "Team": "TeamID"})
team_gamelogs = team_gamelogs[
    [
        "Season", "Date", "GameID", "Team", "TeamID", "Is_Home", "Opp",
        "G", "A", "PTS", "SOG", "HIT", "BLK", "GA", "AA", "PTSA", "SOGA", "HITA", "BLKA"
    ]
]

# Save to teamGamelogs1.csv
team_gamelogs_file_path = os.path.join(data_path, "teamgamelogs.csv")
team_gamelogs.to_csv(team_gamelogs_file_path, mode='a', index=False, header=False,encoding="utf-8")
print(f"Team gamelogs saved to {team_gamelogs_file_path}")


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
    merged_standings_df = standings_df.merge(stats_df, on=["Team"], how="left")
    
    merged_standings_df["ROW"] = merged_standings_df["W"] - merged_standings_df["SOW"]
    merged_standings_df["GDiff"] = merged_standings_df["GF"] - merged_standings_df["GA"]
    merged_standings_df["PIM"] = (merged_standings_df["PIMperG"] * merged_standings_df["GP"]).round(0).astype(int)
    merged_standings_df["PIMA"] = (merged_standings_df["PIMAperG"] * merged_standings_df["GP"]).round(0).astype(int)
    merged_standings_df["Team"] = merged_standings_df["Team"].replace("Utah Hockey Club", "Arizona Coyotes")
    
    merged_standings_df["Conference"] = merged_standings_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown", "Unknown"))[0])
    merged_standings_df["Division"] = merged_standings_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown", "Unknown"))[1])
    merged_standings_df["TeamID"] = merged_standings_df["Team"].map(lambda x: team_info.get(x, ("Unknown", "Unknown", "Unknown"))[2])

    merged_standings_df.sort_values(by=["Conference", "Division", "Points"], ascending=[True, True, False], inplace=True)

    merged_standings_df["Rk"] = (
        merged_standings_df.groupby(["Conference", "Division"])
        .cumcount() + 1
    )

    merged_standings_df = merged_standings_df[final_columns]
    
    # Save the merged DataFrame to a single CSV file
    
    merged_file_path = os.path.join(data_path, "leaderTeams.csv")
    merged_standings_df.to_csv(merged_file_path, index=False, encoding="utf-8")
    print(f"Merged data successfully saved to {merged_file_path}")
else:
    print("Insufficient data to merge.")