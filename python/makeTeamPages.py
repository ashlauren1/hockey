import pandas as pd
import os

# **File Paths**
team_csv = r"C:\Users\ashle\Documents\Projects\hockey\data\teamgamelogs.csv"
output_dir = r"C:\Users\ashle\Documents\Projects\hockey\teams"

# **Ensure Output Directory Exists**
os.makedirs(output_dir, exist_ok=True)

# **Load Data Once**
data = pd.read_csv(team_csv)

# **Part 1: Create Team Directory (index.html)**
def create_team_directory(data, output_dir):
    unique_teams = data.drop_duplicates(subset=["Team", "TeamID"]).sort_values(by="Team")
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Directory</title>
    <link rel="stylesheet" href="stylesheet.css">
    <script src="script.js"></script>
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    </head>
    <body>
    <div class="topnav">
        <a href="/hockey/" target="_blank">Projections</a>
        <a href="/hockey/players/" target="_blank">Players</a>
        <a href="/hockey/teams/" target="_blank">Teams</a>
        <a href="/hockey/leaders/" target="_blank">Leaders</a>
        <a href="/hockey/leaders/standings.html" target="_blank">Standings</a>
        <a href="/hockey/boxscores/" target="_blank">Scores</a>
        <a href="https://ashlauren1.github.io/basketball/" target="_blank">Basketball</a>
        <a href="https://ashlauren1.github.io/ufc/" target="_blank">UFC</a>
    </div>
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for a player or team...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
        <div class="header">
        <h1>Team Directory</h1>
        </div>
        <button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>
        <div id="index-container">
        <table id="team-index">
            <thead>
                <tr>
                    <th>Team</th>
                </tr>
            </thead>
            <tbody>
    """

    # Populate the table with each unique team and link
    for _, row in unique_teams.iterrows():
        team_name = row["Team"]
        team_id = row["TeamID"]

        html_content += f"""
            <tr>
                <td style="text-align:left"><a href="/hockey/teams/{team_id}.html">{team_name}</a></td>
            </tr>
        """

    # Close the table and HTML tags
    html_content += """
            </tbody>
        </table>
        <div class="footer"></div>
    </body>
    </html>
    """

    # Write the HTML content to a file
    output_file_path = os.path.join(output_dir, "index.html")
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Team directory created at {output_file_path}")

# **Part 2: Generate Individual Team Pages**
def create_team_pages(data, output_dir):
    grouped_data = data.groupby('TeamID')

    for team_id, team_data in grouped_data:
        team_name = team_data.iloc[0]['Team']
        team_filename = os.path.join(output_dir, f"{team_id}.html")

        # Start HTML content for the team's gamelog
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{team_name}</title>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <script src="script.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
</head>
<body>
<div id="page-heading">
	<div class="topnav">
        <a class="topnav-item active" href="/hockey/" target="_blank">Projections</a>
        <a class="topnav-item" href="/hockey/players/" target="_blank">Players</a>
        <a class="topnav-item" href="/hockey/teams/" target="_blank">Teams</a>
        <a class="topnav-item" href="/hockey/leaders/" target="_blank">Leaders</a>
        <a class="topnav-item" href="/hockey/leaders/standings.html" target="_blank">Standings</a>
        <a class="topnav-item" href="/hockey/boxscores/" target="_blank">Scores</a>
        <a class="topnav-item" href="https://ashlauren1.github.io/basketball/" target="_blank">Basketball</a>
        <a class="topnav-item" href="https://ashlauren1.github.io/ufc/" target="_blank">UFC</a>
    </div>
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for a player or team...">
        <button id="search-button">Search</button>
        <div id="search-results"></div>
    </div>
	<div class="header">
        <h1>{team_name} Gamelog</h1>
    </div>
</div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    
<div id="team-container">
    <div class="button-container">
        <button id="toggle-selection-btn">Show Selected Only</button>
        <button id="clear-filters-btn">Remove Filters</button>
        <button id="clear-all-btn">Clear All</button>
    </div>
    <div id="glossary-placeholder"></div>

    <div id="glossaryModal" class="modal">
        <div id="glossary-modal-content">
        <span class="closeGlossary">&times;</span>
            <ul class="tiebreaker-modal-list" type="none">
                <li>GP:&nbsp;&nbsp;Games Played</li>
                <li>GF:&nbsp;&nbsp;Goals</li>
                <li>SOG:&nbsp;&nbsp;Shots on Goal</li>
                <li>PIM:&nbsp;&nbsp;Penalties in Minutes</li>
                <li>PPG:&nbsp;&nbsp;Power Play Goals</li>
                <li>PPO:&nbsp;&nbsp;Power Play Opportunities</li>
                <li>SHG:&nbsp;&nbsp;Short-Handed Goals</li>
                <li>SOGA:&nbsp;&nbsp;Shots Against</li>
                <li>PIMA:&nbsp;&nbsp;Opponent Penalties in Minutes</li>
                <li>PPGA:&nbsp;&nbsp;Power Play Goals Against</li>
                <li>PPOA:&nbsp;&nbsp;Power Play Opportunities Against</li>
                <li>SHGA:&nbsp;&nbsp;Short-Handed Goals Against</li>
                <li>CF:&nbsp;&nbsp;Corsi For at Even Strength -- Shots on Goal + Blocked Attempts + Missed Shots</li>
                <li>CA:&nbsp;&nbsp;Corsi Against at Even Strength -- Shots on Goal + Blocked Attempts + Missed Shots</li>
                <li>CF%:&nbsp;&nbsp;Corsi For % at Even Strength -- CF / (CF + CA)</li>
                <li>FF:&nbsp;&nbsp;Fenwick For at Even Strength -- Shots + Misses</li>
                <li>FA:&nbsp;&nbsp;Fenwick Against at Even Strength -- Shots + Misses</li>
                <li>FF%:&nbsp;&nbsp;Fenwick For % at Even Strength -- FF / (FF + FA)</li>
                <li>FOW:&nbsp;&nbsp;Faceoff Wins</li>
                <li>FOL:&nbsp;&nbsp;Faceoff Losses</li>
                <li>FO%:&nbsp;&nbsp;Faceoff Win Percentage</li>
            </ul>
        </div>
    </div>
    
        <table id="team-table">
        <colgroup>
        <col style="width:70px">
        <col style="width:94px">
        <col span="13" style="width:48px">
        </colgroup>
            <thead>
                <tr>
                    <th>Season</th>
                    <th>Date</th>
                    <th>Team</th>
                    <th></th>
                    <th>Opp</th>
                    <th data-tip="Goals">G</th>
                    <th data-tip="Assists">A</th>
                    <th data-tip="Points">PTS</th>
                    <th data-tip="Shots on Goal">SOG</th>
                    <th data-tip="Goals">HIT</th>
                    <th data-tip="Goals">BLK</th>
                    <th data-tip="Goals Against">GA</th>
                    <th data-tip="Shots on Goal Against">SOGA</th>
                    <th data-tip="Hits Against">HITA</th>
                    <th data-tip="Blocks Against">BLKA</th>
                </tr>
            <tr id="filter-row">
            </tr>
            </thead>
            <tbody>
        '''

        # Add rows for each game in the team's gamelog
        for _, row in team_data.iterrows():
            html_content += f'''
                <tr>
                    <td style="text-align:left">{row['Season']}</td>
                    <td style="text-align:left"><a href="/hockey/boxscores/{row['GameID']}.html" target="_blank">{row['Date']}</a></td>
                    <td><a href="/hockey/teams/{row['TeamID']}.html" target="_blank">{row['TeamID']}</a></td>
                    <td>{'vs' if row['Is_Home'] == 1 else '@'}</td>
                    <td><a href="/hockey/teams/{row['Opp']}.html" target="_blank">{row['Opp']}</a></td>
                    <td>{row['G']}</td>
                    <td>{row['A']}</td>
                    <td>{row['PTS']}</td>
                    <td>{row['SOG']}</td>
                    <td>{row['HIT']}</td>
                    <td>{row['BLK']}</td>
                    <td>{row['GA']}</td>
                    <td>{row['SOGA']}</td>
                    <td>{row['HITA']}</td>
                    <td>{row['BLKA']}</td>
                </tr>
            '''

        # Close HTML content
        html_content += '''
                </tbody>
            </table>
            </div>
        </body>
        </html>
        '''

        # Write to HTML file
        with open(team_filename, 'w') as file:
            file.write(html_content)

    print("Team Pages created successfully.")

# **Run the Functions**
create_team_directory(data, output_dir)
create_team_pages(data, output_dir)
