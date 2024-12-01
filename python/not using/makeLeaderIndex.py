import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\hockey\data"
output_dir = r"C:\Users\ashle\Documents\Projects\hockey\leaders"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# **Load Data**
leaders_csv = os.path.join(data_dir, "leaders.csv")
leader_data = pd.read_csv(leaders_csv)

int_columns = ["G", "A", "PTS", "SOG", "HIT", "BLK", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA"]
decimal_columns = [col for col in leader_data.columns if col not in int_columns + ["Player", "PlayerID", "TeamID", "Position"]]

leader_data[int_columns] = leader_data[int_columns].fillna(0).astype(int)
leader_data[decimal_columns] = leader_data[decimal_columns].round(2)

def create_leader_directory(leader_data, output_file_path):
    stat_columns = {
        "G": "Goals",
        "A": "Assists",
        "PTS": "Points",
        "SOG": "Shots on Goal",
        "S%": "Shooting Percentage",
        "HIT": "Hits",
        "BLK": "Blocks",
        "TOI": "Time on Ice",
        "PIM": "Penalty Minutes",
        "EVG": "Even Strength Goals",
        "PPG": "Power Play Goals",
        "SHG": "Short-Handed Goals",
        "EVA": "Even Strength Assists",
        "PPA": "Power Play Assists",
        "SHA": "Short-Handed Assists",
        "G_GP": "Goals per Game",
        "A_GP": "Assists per Game",
        "PTS_GP": "Points per Game",
        "SOG_GP": "Shots on Goal per Game",
        "HIT_GP": "Hits per Game",
        "BLK_GP": "Blocks per Game",
        "TOI_GP": "Time on Ice per Game"
    }

    leaders = {}
    
    for key, display_name in stat_columns.items():
        if key in leader_data.columns:
            if key == "S%":
                filtered_data = leader_data[leader_data["SOG"] >= 30]
                if not filtered_data.empty:
                    max_value = filtered_data[key].max()
                    tied_leaders = filtered_data[filtered_data[key] == max_value]
                else:
                    continue
            else:
                max_value = leader_data[key].max()
                tied_leaders = leader_data[leader_data[key] == max_value]
            
            leaders[key] = [
                {
                    "player": row["Player"],
                    "player_id": row["PlayerID"],
                    "value": int(row[key]) if key in int_columns else round(row[key], 2)
                }
                for _, row in tied_leaders.iterrows()
            ]

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <script src="modalsMobileNavAndSearch.js"></script>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="stylesheet" href="commonStylesheet.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <title>Leaders Directory</title>
</head>

<body>
<div id="mobileTopnav">
    <div class="menuBarContainer mobile active">
        <a href="javascript:void(0);" class="icon" onclick="myFunction()"><i class="fa fa-bars"></i>Menu</a>
    </div>
    <div id="myLinks">
        <ul class="navLinks">
            <li class="nav-link"><a href="/hockey/" target="_blank">Projections</a></li>
            <li class="nav-link"><a href="/hockey/players/" target="_blank">Players</a></li>
            <li class="nav-link"><a href="/hockey/teams/" target="_blank">Teams</a></li>
            <li class="nav-link"><a href="/hockey/leaders/" target="_blank">Leaders</a></li>
            <li class="nav-link"><a href="/hockey/leaders/standings.html" target="_blank">Standings</a></li>
            <li class="nav-link"><a href="/hockey/boxscores/" target="_blank">Scores</a></li>
            <li class="nav-link"><a href="https://ashlauren1.github.io/basketball/" target="_blank">Basketball</a></li>
            <li class="nav-link"><a href="https://ashlauren1.github.io/ufc/" target="_blank">UFC</a></li>
        </ul>
    </div>
</div>

<div id="pageHeading">
	<div class="topnav">
        <a class="topnav-item" href="/hockey/" target="_blank">Projections</a>
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
        <h1>NHL Leaders</h1>
    </div>
</div>

    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>

<main>
<div id="leadersIndexContainer">
    <div id="seasons_list_container">
        <p class="title-caption">Leaders by Season:</p>
		<ul class="seasons_list">
            <li><a href="/hockey/leaders/2024-25_skaters.html">2024-25</a></li>
			<li><a href="/hockey/leaders/2023-24_skaters.html">2023-24</a></li>
            <li><a href="/hockey/leaders/2022-23_skaters.html">2022-23</a></li>
            <li><a href="/hockey/leaders/2021-22_skaters.html">2021-22</a></li>
            <li><a href="/hockey/leaders/2020-21_skaters.html">2020-21</a></li>
            <li><a href="/hockey/leaders/2019-20_skaters.html">2019-20</a></li>
            <li><a href="/hockey/leaders/2018-19_skaters.html">2018-19</a></li>
            <li><a href="/hockey/leaders/2017-18_skaters.html">2017-18</a></li>
		</ul>
	</div>
    <p class="title-caption">Current Leaders:</p>
    <div class="tabular">
    """
    
    for key, display_name in stat_columns.items():
        if key in leaders:
            leader_entries = ""
            is_tie = len(leaders[key]) > 1  # Check if there's a tie
            display_name_with_tie = f"{display_name} (Tie)" if is_tie else display_name
            leader_entries += f'<div class="groupedTabular">'
            
            for i, player in enumerate(leaders[key]):
                if i == 0:
                    leader_entries += f"""
        <div class="tabular_row">
            <div><strong>{display_name_with_tie}</strong></div>
            <div><a href="/hockey/players/{player['player_id']}.html">{player['player']}</a> ({player['value']})</div>
        </div>
                    """
                else:
                    leader_entries += f"""
        <div class="tabular_row">
            <div></div>
            <div><a href="/hockey/players/{player['player_id']}.html">{player['player']}</a> ({player['value']})</div>
        </div>
                    """
            leader_entries += f'</div>'

            html_content += leader_entries

    html_content += """
    </div>
</div>
</main>
<div class="footer"></div>
</body>
</html>
    """

    # Write the HTML content to a file
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Leaders index created at {output_file_path}")

# Create leader directory
output_file_path = os.path.join(output_dir, "index.html")
create_leader_directory(leader_data, output_file_path)
