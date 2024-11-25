import pandas as pd
import os
import re
from datetime import datetime
from tqdm import tqdm
import json

# File paths
metrics_file_path = r"C:\Users\ashle\Documents\Projects\hockey\data\gamelogs.csv"
lines_file_path = r"C:\Users\ashle\Documents\Projects\hockey\data\todayLines.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\hockey\index.html"
rosters_file_path = r"C:\Users\ashle\Documents\Projects\hockey\data\rosters.csv"

rosters_data = pd.read_csv(rosters_file_path)
metrics_data = pd.read_csv(metrics_file_path,  parse_dates=["Date"], low_memory=False)
lines_data = pd.read_csv(lines_file_path)

player_links = {f"{row['Player']} ({row['TeamID']})": f"/hockey/players/{row['PlayerID']}.html" 
                for _, row in rosters_data.iterrows()}

team_links = {row['Team']: f"/hockey/teams/{row['TeamID']}.html" 
              for _, row in rosters_data.drop_duplicates('TeamID').iterrows()}


# Write out to JSON with proper formatting
with open("players.json", "w") as f:
    json.dump(player_links, f, indent=4)

with open("teams.json", "w") as f:
    json.dump(team_links, f)

print("players.json and teams.json created successfully!")


# Convert relevant columns to numeric types to avoid type errors
metrics_data[['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK']] = metrics_data[['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK']].apply(pd.to_numeric, errors='coerce')
metrics_data['TOI'] = pd.to_numeric(metrics_data['TOI'], errors='coerce')

# Create a dictionary mapping GameID to Game
game_mapping = lines_data.set_index('GameID')['Game'].to_dict()

# Filter for players in lines.csv
lines_players = lines_data['PlayerID'].unique()
metrics_data = metrics_data[metrics_data['PlayerID'].isin(lines_players)]

# Functions to calculate averages and ratios
def calculate_average_stats(group):
    return {stat: group[stat].mean() for stat in ['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK', 'TOI']}

def calculate_over_ratio(filtered_data, line, stat):
    over_count = (filtered_data[stat] > line).sum()
    total_games = len(filtered_data)
    return f"{over_count}/{total_games}" if total_games > 0 else "0/0"

# Aggregated stats
player_home_stats = metrics_data[metrics_data['Is_Home'] == 1].groupby('PlayerID').apply(calculate_average_stats, include_groups=False).to_dict()
player_away_stats = metrics_data[metrics_data['Is_Home'] == 0].groupby('PlayerID').apply(calculate_average_stats, include_groups=False).to_dict()
player_vs_opp_stats = metrics_data.groupby(['PlayerID', 'Opp']).apply(calculate_average_stats, include_groups=False).to_dict()

team_home_stats = metrics_data[metrics_data['Is_Home'] == 1].groupby('Team').apply(calculate_average_stats, include_groups=False).to_dict()
team_away_stats = metrics_data[metrics_data['Is_Home'] == 0].groupby('Team').apply(calculate_average_stats, include_groups=False).to_dict()
team_vs_opp_stats = metrics_data.groupby(['Team', 'Opp']).apply(calculate_average_stats, include_groups=False).to_dict()

# Projections function
def get_projected_stats(player_id, team, opp, is_home):
    home_away_stats = player_home_stats.get(player_id) if is_home == 1 else player_away_stats.get(player_id)
    opp_stats = player_vs_opp_stats.get((player_id, opp))
    team_home_away_stats = team_home_stats.get(team) if is_home == 1 else team_away_stats.get(team)
    team_opp_stats = team_vs_opp_stats.get((team, opp))
    
    player_game_count = len(metrics_data[metrics_data['PlayerID'] == player_id])
    if player_game_count >= 5:
        if home_away_stats and opp_stats:
            return {k: (0.8 * opp_stats[k] + 0.2 * home_away_stats[k]) for k in opp_stats}
        return home_away_stats or opp_stats or {stat: 0 for stat in ['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK', 'TOI']}
    else:
        player_weighted_stats = {k: (0.8 * opp_stats[k] + 0.2 * home_away_stats[k]) for k in opp_stats} if home_away_stats and opp_stats else home_away_stats or opp_stats or {stat: 0 for stat in ['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK', 'TOI']}
        team_weighted_stats = {k: (0.8 * team_opp_stats[k] + 0.2 * team_home_away_stats[k]) for k in team_opp_stats} if team_home_away_stats and team_opp_stats else team_home_away_stats or team_opp_stats or {stat: 0 for stat in ['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK', 'TOI']}
        return {k: (0.7 * player_weighted_stats[k] + 0.3 * team_weighted_stats[k]) for k in player_weighted_stats}

# Ratio calculations based on max game number
def calculate_ratios(player_data, stat, line):
    max_game_num = player_data['Gm#'].max()
    last_n_games = {5: 'L5', 10: 'L10', 20: 'L20', 30: 'L30'}
    ratios = {}
    for n, label in last_n_games.items():
        recent_games = player_data[player_data['Gm#'] >= max_game_num - n + 1]
        ratios[label] = calculate_over_ratio(recent_games, line, stat)
    return ratios

# Probability calculation function
weights = {"opponent": 0.80, "home_away": 0.20}
def calculate_probability(data, stat, line):
    return (data[stat] > line).mean() if len(data) > 0 else 0

# Initialize a set to store unique (player_id, opp) pairs
h2h_pairs = set()

# Generate final results
final_results = []
columns = ['Game', 'Team', 'Player', 'Type', 'Stat', 'Line', 'Proj.', 'Diff.', 'Prob.', '2024-25', 'H2H', 'L5', 'L10', 'L20', '2023-24', 'All']

unique_combinations = set()

# Process each game
for _, game in tqdm(lines_data.iterrows(), total=lines_data.shape[0]):
    player_id = game['PlayerID']
    team = game['Team']
    is_home = game['Is_Home']
    opp = game['Opp']
    game_id = game['GameID']
    game_display = game_mapping.get(game['GameID'], game['GameID'])
    
    # Add the player-opponent pair to the set
    h2h_pairs.add((player_id, opp))
    
    player_data = metrics_data[metrics_data['PlayerID'] == player_id]
    lines_for_player = lines_data[lines_data['PlayerID'] == player_id]
    
    if not player_data.empty and not lines_for_player.empty:
        player_name = lines_for_player.iloc[0]['Player']  # Fetch player name
        projected_stats = get_projected_stats(player_id, team, opp, is_home)
        
        # Process each line for player
        for _, line_row in lines_for_player.iterrows():
            stat = line_row['Stat']
            line_value = line_row['Line']
            stat_type = line_row['Type']
            
            unique_key = (player_id, stat, line_value, stat_type)
            if unique_key in unique_combinations:
                continue  # Skip this row if already processed
            
            # Add to set of unique combinations
            unique_combinations.add(unique_key)
            
            
            # Helper function to safely evaluate ratios
            def safe_eval_ratio(ratio_str):
                try:
                    if '/' in ratio_str:
                        x, n = map(int, ratio_str.split('/'))
                        return f"{(x / n):.2f}" if n != 0 else ratio_str  # Avoid division by zero
                    return ratio_str
                except ZeroDivisionError:
                    return ratio_str

            # Calculate difference and probability
            projected_value = projected_stats.get(stat, 0)
            difference = projected_value - line_value
            opp_data = player_data[player_data['Opp'] == opp]
            opp_prob = calculate_probability(opp_data, stat, line_value)
            home_away_data = player_data[player_data['Is_Home'] == is_home]
            home_away_prob = calculate_probability(home_away_data, stat, line_value)
            weighted_prob = (weights["opponent"] * opp_prob + weights["home_away"] * home_away_prob)

            # Calculate H2H and last N games ratios
            h2h_ratio = calculate_over_ratio(opp_data, line_value, stat)  # Keeps {x / n} format

            # Convert ratios to decimal if possible; otherwise, keep original
            season_ratio_raw = calculate_over_ratio(player_data[player_data['Season'] == '2024-25'], line_value, stat)
            season_ratio = safe_eval_ratio(season_ratio_raw)

            last_n_ratios = calculate_ratios(player_data, stat, line_value)
            l5_ratio = safe_eval_ratio(last_n_ratios['L5'])
            l10_ratio = safe_eval_ratio(last_n_ratios['L10'])
            l20_ratio = safe_eval_ratio(last_n_ratios['L20'])

            prev_season_ratio_raw = calculate_over_ratio(player_data[player_data['Season'] == '2023-24'], line_value, stat)
            prev_season_ratio = safe_eval_ratio(prev_season_ratio_raw)

            all_ratio_raw = calculate_over_ratio(player_data, line_value, stat)
            all_ratio = safe_eval_ratio(all_ratio_raw)

            # Compile row and add to results
            result_row = {
                'Game': game_display,
                'Team': team,
                'Player': player_name,
                'PlayerID': player_id,
                'Opp': opp,
                'Type': stat_type,
                'Stat': stat,
                'Line': line_value,
                'Proj.': projected_value,
                'Diff.': difference,
                'Prob.': weighted_prob,
                '24-25': season_ratio,
                'H2H': h2h_ratio,
                'L5': l5_ratio,
                'L10': l10_ratio,
                'L20': l20_ratio,
                '23-24': prev_season_ratio,
                'All': all_ratio
            }
            final_results.append(result_row)

# Generate H2H pages
def sanitize_filename(filename):
    # Remove invalid characters
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def generate_h2h_pages(metrics_data, h2h_pairs, output_dir):
    h2h_dir = os.path.join(output_dir, 'h2h')
    os.makedirs(h2h_dir, exist_ok=True)

    for player_id, opp in h2h_pairs:
        # Filter the data for this player and opponent
        group = metrics_data[(metrics_data['PlayerID'] == player_id) & (metrics_data['Opp'] == opp)]
        if group.empty:
            continue
        player_name = group.iloc[0]['Player']
        opp_name = opp  # Assuming 'Opp' is a team abbreviation

        # Sanitize the filename
        filename = os.path.join(h2h_dir, sanitize_filename(f"{player_id}_vs_{opp}.html"))

        # Start HTML content
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{player_name} vs {opp_name} - Previous Matchups</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel=Stylesheet href=stylesheet.css>
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <script>
    document.addEventListener("DOMContentLoaded", async function () {{
        const searchBar = document.getElementById("search-bar");
        const searchResults = document.getElementById("search-results");
        const searchButton = document.getElementById("search-button");

        let playerLinks = {{}};
        let teamLinks = {{}};

        // Load players and teams data from JSON files
        async function loadLinks() {{
            playerLinks = await fetch('players.json').then(response => response.json());
            teamLinks = await fetch('teams.json').then(response => response.json());
        }}

        await loadLinks();  // Ensure links are loaded before searching

        // Filter data and show suggestions based on input
        function updateSuggestions() {{
            const query = searchBar.value.trim().toLowerCase();
            searchResults.innerHTML = ""; // Clear previous results

            if (query === "") return;

            // Combine players and teams for search
            const combinedLinks = {{ ...playerLinks, ...teamLinks }};
            const matchingEntries = Object.entries(combinedLinks)
                .filter(([name]) => name.toLowerCase().includes(query))  // Matches on both name and ID
                .slice(0, 10); // Limit to top 10

            matchingEntries.forEach(([name, url]) => {{
                const resultItem = document.createElement("div");
                resultItem.classList.add("suggestion");

                // Proper case for names
                resultItem.textContent = name;

                resultItem.addEventListener("click", () => {{
                    window.open(url, "_self");
                }});
                searchResults.appendChild(resultItem);
            }});

            if (matchingEntries.length > 0) {{
                searchResults.style.display = "block"; // Show results if matches are found
            }} else {{
                const noResultItem = document.createElement("div");
                noResultItem.classList.add("no-result");
                noResultItem.textContent = "No results found.";
                searchResults.appendChild(noResultItem);
                searchResults.style.display = "block";
            }}
        }}
        
        document.addEventListener("click", function(event) {{
            if (!searchResults.contains(event.target) && event.target !== searchBar) {{
                searchResults.style.display = "none";
            }}
        }});

        // Add event listener to search bar
        searchBar.addEventListener("input", updateSuggestions);
        
        function redirectToSearchResults() {{
        const query = searchBar.value.trim().toLowerCase();;
        if (query) {{
            window.location.href = `/hockey/search_results.html?query=${{encodeURIComponent(query)}}`;
        }}
    }}

    // Add event listeners for search
    searchBar.addEventListener("keypress", function (e) {{
        if (e.key === "Enter") {{
            redirectToSearchResults();
        }}
    }});

    searchButton.addEventListener("click", redirectToSearchResults);
}});

document.addEventListener("DOMContentLoaded", function () {{
    var glossaryModal = document.getElementById("glossaryModal");
    var glossaryModalButton = document.getElementById("glossaryButton");
    var glossaryModalContent = document.getElementById("glossary-modal-content");
    var closeGlossaryModal = document.getElementsByClassName("closeGlossary")[0];

    glossaryModalButton.onclick = function() {{
        glossaryModal.classList.add("open");
        glossaryModal.style.display = "block";
    }}

    closeGlossaryModal.onclick = function() {{
        glossaryModal.classList.remove("open");
        glossaryModal.style.display = "none";
    }}

    window.onclick = function(event) {{
        if (event.target === glossaryModal) {{
            glossaryModal.style.display = "none";
        }}
    }}
}})
        
document.addEventListener("DOMContentLoaded", function () {{
    const container = document.getElementById("table-container");

    const glossaryButton = document.createElement("button");
    glossaryButton.id = "glossaryButton";
    glossaryButton.innerText = "Glossary";
    container.querySelector(".title-caption").appendChild(glossaryButton);

    function setupModal(modalId, buttonId, closeClass) {{
        const modal = document.getElementById(modalId);
        const button = document.getElementById(buttonId);
        const closeButton = modal.querySelector(`.${{closeClass}}`);

        // Toggle modal visibility when button is clicked
        button.onclick = function () {{
            const isOpen = modal.classList.contains("open");
            modal.style.display = isOpen ? "none" : "block";
            modal.classList.toggle("open", !isOpen);
        }};

        // Close modal when the close button is clicked
        closeButton.onclick = function () {{
            modal.style.display = "none";
            modal.classList.remove("open");
        }};

        // Close modal when clicking outside the modal content
        window.onclick = function (event) {{
            if (event.target === modal) {{
                modal.style.display = "none";
                modal.classList.remove("open");
            }}
        }};
    }}

    setupModal("glossaryModal", "glossaryButton", "closeGlossary");
}});
</script>
</head>
<body>
<div class="mobile">
	<a class="activeMobile" href="/hockey/" target="_blank">Home</a>
	<div id="myLinks">
		<a href="/hockey/players/" target="_blank">Players</a>
        <a href="/hockey/teams/" target="_blank">Teams</a>
        <a href="/hockey/leaders/" target="_blank">Leaders</a>
        <a href="/hockey/leaders/standings.html" target="_blank">Standings</a>
        <a href="/hockey/boxscores/" target="_blank">Scores</a>
        <a href="https://ashlauren1.github.io/basketball/" target="_blank">Basketball</a>
        <a href="https://ashlauren1.github.io/ufc/" target="_blank">UFC</a>
	</div>
	<a href="javascript:void(0);" class="icon" onclick="myFunction()">
		<i class="fa fa-bars"></i>
	</a>


<script>
function myFunction() {{
  var x = document.getElementById("myLinks");
  if (x.style.display === "block") {{
    x.style.display = "none";
  }} else {{
    x.style.display = "block";
  }}
}}
</script>
</div>


<div id="page-heading">
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
		<h1>{player_name} vs {opp_name} - Previous Matchups</h1>
	</div>
</div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
<div id="H2H-container">
    <div id="table-container">
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
        <table id="H2H-table">
        <caption class="title-caption"><a href="/hockey/players/{player_id}.html" target="_blank">{player_name}</a> H2H Results</caption>
        <thead>
            <tr>
                <th>Date</th>
                <th>Team</th>
                <th></th>
                <th>Opp</th>
                <th>G</th>
                <th>A</th>
                <th>PTS</th>
                <th>SOG</th>
                <th>HIT</th>
                <th>BLK</th>
                <th>TOI</th>
                <th>PIM</th>
            </tr>
        </thead>
        <tbody>
        '''

        # Add rows for each game
        for _, row in group.iterrows():
            # Convert date to MM/DD/YYYY format
            date_obj = datetime.strptime(str(row['Date']), "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%m/%d/%Y")
            game_id = row['GameID']  # Assumes 'GameID' column is present in your data
            
            # Create a hyperlink for the date
            date_link = f'<a href="/hockey/boxscores/{game_id}.html" target="_blank">{formatted_date}</a>'

            # Other row data
            team = row['Team']
            opp = row['Opp']
            g = row['G']
            a = row['A']
            pts = row['PTS']
            sog = row['SOG']
            hit = row['HIT']
            blk = row['BLK']
            toi = f"{row['TOI']:.2f}"
            pim = row['PIM']
            

            html_content += f'''
            <tr>
                <td>{date_link}</td>
                <td><a href="/hockey/teams/{team}.html" target="_blank">{team}</a></td>
                <td>{'vs' if row['Is_Home'] == 1 else '@'}</td>
                <td><a href="/hockey/teams/{opp}.html" target="_blank">{opp}</a></td>
                <td>{g}</td>
                <td>{a}</td>
                <td>{pts}</td>
                <td>{sog}</td>
                <td>{hit}</td>
                <td>{blk}</td>
                <td>{toi}</td>
                <td>{pim}</td>
            </tr>
            '''

        # Close HTML content
        html_content += '''
        </tbody>
        </table>
    </div>
    </div>
</body>
</html>
        '''

        # Write the HTML content to file
        with open(filename, 'w') as f:
            f.write(html_content)

    print("H2H pages created successfully.")

# Call the function to generate H2H pages
generate_h2h_pages(metrics_data, h2h_pairs, os.path.dirname(output_file_path))

# Convert results to HTML format with specified JavaScript functionality
with open(output_file_path, 'w') as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Hockey!</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel=Stylesheet href=stylesheet.css>
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <script src="players.json"></script>
    <script src="teams.json"></script>

<script>

document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("data-table");
    const headerRow = table.querySelector("thead tr:first-child");
    const rows = Array.from(table.querySelectorAll("tbody tr"));
    const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
    const clearAllButton = document.getElementById("clear-all-btn");
    const clearButton = document.getElementById("clear-filters-btn");
    let showSelectedOnly = false;
    let isDragging = false;

    // Explicitly set the index of the "Prob." column (adjust if necessary)
    const probColumnIndex = 8;

    // Add checkboxes to the header row
    const checkboxHeader = document.createElement("th");
    checkboxHeader.classList.add("checkboxHeader");
    checkboxHeader.textContent = "";
    headerRow.prepend(checkboxHeader);

    // Add checkboxes to each row in the table
    
    rows.forEach(row => {
        const checkboxCell = document.createElement("td");
		const checkboxDiv = document.createElement("div");
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
		checkboxDiv.classList.add("checkboxDiv");
        checkbox.classList.add("eventCheckbox");

        // Get probability from "Prob." column and store it as a data attribute
        const probText = row.cells[probColumnIndex].textContent.trim();
        const probValue = parseFloat(probText);
        checkbox.dataset.prob = probValue;

        checkboxCell.appendChild(checkboxDiv);
		checkboxDiv.appendChild(checkbox);
        row.prepend(checkboxCell);

        // Recalculate combined probability when a checkbox is checked or unchecked
        checkbox.addEventListener("change", calculateCombinedProbability);
    });

    // Calculate combined probability for selected rows
    function calculateCombinedProbability() {
        const checkboxes = document.querySelectorAll(".event-checkbox:checked");
        let combinedProbability = 1;

        checkboxes.forEach(checkbox => {
            const prob = parseFloat(checkbox.dataset.prob);
            combinedProbability *= prob;
        });

        document.getElementById("result").textContent = `Combined Probability: ${(combinedProbability * 100).toFixed(2)}%`;
    }

    // Multi-row selection by dragging
    rows.forEach(row => {
        row.addEventListener("mousedown", function () {
            isDragging = true;
            toggleRowSelection(row);
        });

        row.addEventListener("mouseenter", function () {
            if (isDragging) toggleRowSelection(row);
        });

        row.addEventListener("mouseup", () => isDragging = false);
    });

    document.addEventListener("mouseup", () => isDragging = false);

    // Toggle selection for individual rows
    function toggleRowSelection(row) {
        row.classList.toggle("selected-row");
    }

    // Show only selected rows or all rows
    toggleSelectionBtn.addEventListener("click", () => {
        showSelectedOnly = !showSelectedOnly;
        if (showSelectedOnly) {
            rows.forEach(row => {
                row.style.display = row.classList.contains("selected-row") ? "" : "none";
            });
            toggleSelectionBtn.textContent = "Show All";
        } else {
            rows.forEach(row => (row.style.display = ""));
            toggleSelectionBtn.textContent = "Show Selected Only";
        }
    });

    // Add sorting to each header
    addSortToHeaders(table);

    function addSortToHeaders(table) {
        const headers = table.querySelectorAll("thead th");
        headers.forEach((header, index) => {
            header.style.cursor = "pointer";
            header.addEventListener("click", function () {
                sortTable(table, index);
            });
        });
    }

    // Sort the table by column
    function sortTable(table, columnIndex) {
        const rows = Array.from(table.querySelectorAll("tbody tr"));
        const isNumeric = rows.every(row => !isNaN(row.cells[columnIndex].textContent.trim()));
        const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
        table.dataset.sortDirection = direction;

        rows.sort((a, b) => {
            const cellA = a.cells[columnIndex].textContent.trim();
            const cellB = b.cells[columnIndex].textContent.trim();

            const valA = isNumeric ? parseFloat(cellA) : cellA.toLowerCase();
            const valB = isNumeric ? parseFloat(cellB) : cellB.toLowerCase();

            return direction === "asc" ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
        });

        rows.forEach(row => table.querySelector("tbody").appendChild(row));
    }

    // Add filters
    addFilters(table);

    function addFilters(table) {
        const filterColumns = ["Game", "Team", "Type", "Stat"];
        const filterHeaders = Array.from(table.querySelectorAll("thead th"));
        const filterIndexes = filterColumns.map(col => filterHeaders.findIndex(header => header.textContent.trim() === col));

        filterColumns.forEach((colName, i) => {
            const index = filterIndexes[i];
            const values = Array.from(new Set(
                Array.from(table.querySelectorAll(`tbody tr td:nth-child(${index + 1})`))
                .map(cell => cell.textContent.trim())
            )).sort();

            // For each value, create a checkbox
            const filterDiv = document.getElementById(`${colName.toLowerCase()}-filters`);
            if (filterDiv) {
                filterDiv.innerHTML = "";
                const allLabel = document.createElement('label');
                const allCheckbox = document.createElement('input');
                allCheckbox.type = 'checkbox';
                allCheckbox.classList.add(`${colName.toLowerCase()}-filter-all`);
                allCheckbox.checked = true;
                allLabel.appendChild(allCheckbox);
                allLabel.appendChild(document.createTextNode("All"));
                filterDiv.appendChild(allLabel);

            // Event listener to check/uncheck all checkboxes in this category
            allCheckbox.addEventListener('change', function () {
                const isChecked = allCheckbox.checked;
                document.querySelectorAll(`.${colName.toLowerCase()}-filter`).forEach(checkbox => {
                    checkbox.checked = isChecked;
                });
                filterTable(); // Update table display based on new filter states
            });

                
                values.forEach(value => {
                    const label = document.createElement('label');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.value = value;
                    checkbox.checked = true;
                    checkbox.classList.add(`${colName.toLowerCase()}-filter`);
                    label.appendChild(checkbox);
                    label.appendChild(document.createTextNode(value));
                    filterDiv.appendChild(label);

                    // Add event listener to the checkbox
                    checkbox.addEventListener('change', () => {
                    // If any checkbox in the group is unchecked, uncheck the "All" checkbox
                    if (!checkbox.checked) {
                        allCheckbox.checked = false;
                    } else {
                        // Check if all individual boxes are selected to set "All" checkbox
                        const allSelected = Array.from(document.querySelectorAll(`.${colName.toLowerCase()}-filter`))
                            .every(cb => cb.checked);
                        allCheckbox.checked = allSelected;
                    }
                    filterTable();
                });
            });
        } else {
            console.error(`Filter div with ID ${colName.toLowerCase()}-filters not found.`);
        }
    });
}
    const minFilterIds = ["diff-filters", "2425-filters", "l5-filters", "l10-filters", "l20-filters", "2324-filters", "all-filters"];
    minFilterIds.forEach(id => {
        document.getElementById(id).addEventListener("input", filterTable);
    });    

    // Filter table based on selected filters
    function filterTable() {
        const filterColumns = ["Game", "Team", "Type", "Stat"];
        const filterClasses = ["game-filter", "team-filter", "type-filter", "stat-filter"];
        const filterHeaders = Array.from(table.querySelectorAll("thead th"));
        const filterIndexes = filterColumns.map(col => filterHeaders.findIndex(header => header.textContent.trim() === col));

        const filters = filterClasses.map(cls => {
            const checkboxes = document.querySelectorAll(`.${cls}:checked`);
            return Array.from(checkboxes).map(cb => cb.value);
        });

		const minValues = {
            "Diff.": parseFloat(document.getElementById("diff-filters").value) || -Infinity,
            "24-25": parseFloat(document.getElementById("2425-filters").value) || -Infinity,
            "L5": parseFloat(document.getElementById("l5-filters").value) || -Infinity,
            "L10": parseFloat(document.getElementById("l10-filters").value) || -Infinity,
            "L20": parseFloat(document.getElementById("l20-filters").value) || -Infinity,
            "23-24": parseFloat(document.getElementById("2324-filters").value) || -Infinity,
            "All": parseFloat(document.getElementById("all-filters").value) || -Infinity
        };
		
		const showSelectedOnly = toggleSelectionBtn.textContent === "Show All"; // Check if "Show Selected Only" mode is active

        rows.forEach(row => {
            const cells = Array.from(row.cells);
            let matchesFilter = true;
			
			for (let i = 0; i < filters.length; i++) {
				const filterValues = filters[i];
				const cellValue = cells[filterIndexes[i]].textContent.trim();

				if (filterValues.length === 0) {
                // No checkboxes checked in this category; no rows should match
					matchesFilter = false;
					break;
				} else if (!filterValues.includes(cellValue)) {
                // Cell value does not match any selected filter values
					matchesFilter = false;
					break;
            }
        }
        
		if (matchesFilter) {
                Object.entries(minValues).forEach(([colName, minValue], i) => {
                    const colIndex = filterHeaders.findIndex(header => header.textContent.trim() === colName);
                    if (colIndex >= 0) {
                        const cellValue = parseFloat(cells[colIndex].textContent.trim()) || -Infinity;
                        if (cellValue < minValue) {
                            matchesFilter = false;
                        }
                    }
                });
            }

            // Display row if it matches all filters
            row.style.display = (matchesFilter && (!showSelectedOnly || row.classList.contains("selected-row"))) ? "" : "none";
        });
    }

    // "Clear Filters" button functionality
    clearButton.addEventListener("click", () => {
        const filterClasses = ["game-filter", "team-filter", "type-filter", "stat-filter"];
        filterClasses.forEach(cls => {
            document.querySelectorAll(`.${cls}`).forEach(checkbox => checkbox.checked = true);
        });
        minFilterIds.forEach(id => {
			document.getElementById(id).value = "";
		});
        filterTable();
    });

    // "Clear All" functionality
    clearAllButton.addEventListener("click", () => {
        // Uncheck all event checkboxes
        document.querySelectorAll(".event-checkbox").forEach(checkbox => checkbox.checked = false);

        // Reset filters
        const filterClasses = ["game-filter", "team-filter", "type-filter", "stat-filter"];
        filterClasses.forEach(cls => {
            document.querySelectorAll(`.${cls}`).forEach(checkbox => checkbox.checked = true);
        });
        minFilterIds.forEach(id => {
			document.getElementById(id).value = "";
		});

        rows.forEach(row => {
            row.classList.remove("selected-row");
            row.style.display = "";
        });
        toggleSelectionBtn.textContent = "Show Selected Only";
        showSelectedOnly = false;
        
        calculateCombinedProbability();
        filterTable();
    });

    // Gradient color code...
    const gradientColumns = ["Diff.", "Prob.", "24-25", "L5", "L10", "L20", "23-24", "All"];

    // Get column indexes based on column headers
    const headers = Array.from(table.querySelectorAll("thead th"));
    const columnIndexes = gradientColumns.map(col => headers.findIndex(header => header.textContent.trim() === col));

    // Get min and max values for each column
    const minMaxValues = columnIndexes.map(index => {
        let values = Array.from(table.querySelectorAll(`tbody tr td:nth-child(${index + 1})`))
            .map(cell => parseFloat(cell.textContent))
            .filter(value => !isNaN(value));

        return {
            min: Math.min(...values),
            max: Math.max(...values)
        };
    });

    // Apply gradient color based on value
    table.querySelectorAll("tbody tr").forEach(row => {
        columnIndexes.forEach((index, i) => {
            if (index >= 0) {
                const cell = row.cells[index];
                const value = parseFloat(cell.textContent);
                const { min, max } = minMaxValues[i];

                if (!isNaN(value)) {
                    // Adjust color for each value based on column min-max range
                    const color = getGradientColor(value, min, max);
                    cell.style.backgroundColor = color;
                    cell.style.color = "#000"; // Ensures text is readable
                }
            }
        });
    });

    // Helper function to get gradient color
    function getGradientColor(value, min, max) {
        // Normalize value within the range for the column
        let normalized = (value - min) / (max - min);
        normalized = Math.max(0, Math.min(1, normalized)); // Clamps the value between 0 and 1

        // Color blend from red (low values) to green (high values)
        const red = normalized < 0.5 ? 255 : Math.floor(255 * (1 - normalized) * 2);
        const green = normalized > 0.5 ? 255 : Math.floor(255 * normalized * 2);
        const blue = 255 * (1 - Math.abs(normalized - 0.5) * 2); // Blend through white

        return `rgb(${red}, ${green}, ${blue})`;
    }
});

    document.addEventListener("DOMContentLoaded", async function () {
        const searchBar = document.getElementById("search-bar");
        const searchResults = document.getElementById("search-results");
        const searchButton = document.getElementById("search-button");

        let playerLinks = {};
        let teamLinks = {};

        // Load players and teams data from JSON files
        async function loadLinks() {
            playerLinks = await fetch('players.json').then(response => response.json());
            teamLinks = await fetch('teams.json').then(response => response.json());
        }

        await loadLinks();  // Ensure links are loaded before searching

        // Filter data and show suggestions based on input
        function updateSuggestions() {
            const query = searchBar.value.trim().toLowerCase();
            searchResults.innerHTML = ""; // Clear previous results

            if (query === "") return;

            // Combine players and teams for search
            const combinedLinks = { ...playerLinks, ...teamLinks };
            const matchingEntries = Object.entries(combinedLinks)
                .filter(([name]) => name.toLowerCase().includes(query))  // Matches on both name and ID
                .slice(0, 10); // Limit to top 10


            matchingEntries.forEach(([name, url]) => {
                const resultItem = document.createElement("div");
                resultItem.classList.add("suggestion");

                // Proper case for names
                resultItem.textContent = name;

                resultItem.addEventListener("click", () => {
                    window.open(url, "_self");
                });
                searchResults.appendChild(resultItem);
            });

        if (matchingEntries.length > 0) {
            searchResults.style.display = "block"; // Show results if matches are found
        } else {
            const noResultItem = document.createElement("div");
            noResultItem.classList.add("no-result");
            noResultItem.textContent = "No results found.";
            searchResults.appendChild(noResultItem);
            searchResults.style.display = "block";
        }
    }
    
    document.addEventListener("click", function(event) {
        if (!searchResults.contains(event.target) && event.target !== searchBar) {
            searchResults.style.display = "none";
        }
    });

    // Add event listener to search bar
    searchBar.addEventListener("input", updateSuggestions);
    
    function redirectToSearchResults() {
        const query = searchBar.value.trim().toLowerCase();;
        if (query) {
            window.location.href = `/hockey/search_results.html?query=${encodeURIComponent(query)}`;
        }
    }

    // Add event listeners for search
    searchBar.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            redirectToSearchResults();
        }
    });

    searchButton.addEventListener("click", redirectToSearchResults);
});

document.addEventListener("DOMContentLoaded", function () {
    const headers = document.querySelectorAll("thead th[data-tip]");

    headers.forEach(header => {
        const tooltip = document.createElement("span");
        tooltip.className = "tooltip inactive"; // Add both classes initially
        tooltip.textContent = header.getAttribute("data-tip");
        document.body.appendChild(tooltip);

        // Show tooltip on mouseover
        header.addEventListener("mouseover", () => {
            tooltip.classList.add("active");
            tooltip.classList.remove("inactive");

            const rect = header.getBoundingClientRect();
            tooltip.style.left = rect.left + "px"; // Align with header
            tooltip.style.top = (rect.top + window.scrollY - tooltip.offsetHeight + 6) + "px"; // Above header, add a small gap
        });

        // Hide tooltip on mouseout
        header.addEventListener("mouseout", () => {
            tooltip.classList.remove("active");
            tooltip.classList.add("inactive");
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    var glossaryModal = document.getElementById("glossaryModal");
    var glossaryModalButton = document.getElementById("glossaryButton");
    var glossaryModalContent = document.getElementById("glossary-modal-content");
    var closeGlossaryModal = document.getElementsByClassName("closeGlossary")[0];

    glossaryModalButton.onclick = function() {
        glossaryModal.classList.add("open");
        glossaryModal.style.display = "block";
    }

    closeGlossaryModal.onclick = function() {
        glossaryModal.classList.remove("open");
        glossaryModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === glossaryModal) {
            glossaryModal.style.display = "none";
        }
    }
})
        
document.addEventListener("DOMContentLoaded", function () {
    const container = document.querySelector(".button-container");

    const glossaryButton = document.createElement("button");
    glossaryButton.id = "glossaryButton";
    glossaryButton.innerText = "Glossary";
    container.appendChild(glossaryButton);

    function setupModal(modalId, buttonId, closeClass) {
        const modal = document.getElementById(modalId);
        const button = document.getElementById(buttonId);
        const closeButton = modal.querySelector(`.${closeClass}`);

        // Toggle modal visibility when button is clicked
        button.onclick = function () {
            const isOpen = modal.classList.contains("open");
            modal.style.display = isOpen ? "none" : "block";
            modal.classList.toggle("open", !isOpen);
        };

        // Close modal when the close button is clicked
        closeButton.onclick = function () {
            modal.style.display = "none";
            modal.classList.remove("open");
        };

        // Close modal when clicking outside the modal content
        window.onclick = function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
                modal.classList.remove("open");
            }
        };
    }

    setupModal("glossaryModal", "glossaryButton", "closeGlossary");
});

    </script>
</head>
<body>

<div class="mobile">
	<a class="activeMobile" href="/hockey/" target="_blank">Home</a>
	<div id="myLinks">
		<a href="/hockey/players/" target="_blank">Players</a>
        <a href="/hockey/teams/" target="_blank">Teams</a>
        <a href="/hockey/leaders/" target="_blank">Leaders</a>
        <a href="/hockey/leaders/standings.html" target="_blank">Standings</a>
        <a href="/hockey/boxscores/" target="_blank">Scores</a>
        <a href="https://ashlauren1.github.io/basketball/" target="_blank">Basketball</a>
        <a href="https://ashlauren1.github.io/ufc/" target="_blank">UFC</a>
	</div>
	<a href="javascript:void(0);" class="icon" onclick="myFunction()">
		<i class="fa fa-bars"></i>
	</a>

<script>
function myFunction() {
  var x = document.getElementById("myLinks");
  if (x.style.display === "block") {
    x.style.display = "none";
  } else {
    x.style.display = "block";
  }
}
</script>
</div>

<div id="page-heading">
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
		<h1>Today's Probabilities and Projections</h1>
	</div>
</div>
	<button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>
    
    <div id="multi-filters">
        <table class="multi-filters">
            <tr><td class="multiFilterLabel">Games:</td><td><div id="game-filters"></div></td></tr>
            <tr><td class="multiFilterLabel">Teams:</td><td><div id="team-filters"></div></td></tr>
            <tr><td class="multiFilterLabel">Types:</td><td><div id="type-filters"></div></td></tr>
            <tr><td class="multiFilterLabel">Stats:</td><td><div id="stat-filters"></div></td></tr>
        </table>
        
        <div class="min-filters">
			<span>Set Minimum Values:</span>
            <div>
                <span class="minFilterLabel">Diff:</span><span><input id="diff-filters" type="number" step="0.1"></span>
                <span class="minFilterLabel">24-25:</span><span><input id="2425-filters" type="number" step="0.1"></span>
                <span class="minFilterLabel">L5:</span><span><input id="l5-filters" type="number" step="0.1"></span>
                <span class="minFilterLabel">L10:</span><span><input id="l10-filters" type="number" step="0.1"></span>
                <span class="minFilterLabel">L20:</span><span><input id="l20-filters" type="number" step="0.1"></span>
                <span class="minFilterLabel">23-24:</span><span><input id="2324-filters" type="number" step="0.1"></span>
                <span class="minFilterLabel">All:</span><span><input id="all-filters" type="number" step="0.1"></span>
			</div>
        </div>
        
    </div>
    <div class="groupedProbAndButtons" style="width:95%"><span class="combinedProbLabel">Click the Checkboxes Below to Calculate the Combined Probability</span><span class="secret"><a href="https://ashlauren1.github.io/rings/" target="_blank">rings</a></span>
        <div id="result-container">
            <div id="result">Combined Probability:</div>
        </div>
        <div class="button-container">
            <button id="toggle-selection-btn">Show Selected Only</button>
            <button id="clear-filters-btn">Remove Filters</button>
            <button id="clear-all-btn">Clear All</button>
        </div>
    </div>
    
    
    <div id="data-table-container">
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
        <table id="data-table">
        <thead>
            <tr>
                <th>Game</th>
                <th>Team</th>
                <th>Player</th>
                <th>Type</th>
                <th>Stat</th>
                <th>Line</th>
                <th data-tip="Projection">Proj.</th>
                <th data-tip="Difference (Projection - Line)">Diff.</th>
                <th data-tip="Probability of Going Over">Prob.</th>
                <th data-tip="Percentage of games this season where the player went over the line">24-25</th>
                <th data-tip="Percentage of games against the opposing team where the player went over the line">H2H</th>
                <th data-tip="Percentage of this player's last 5 games where they went over the line">L5</th>
                <th data-tip="Percentage of this player's last 10 games where they went over the line">L10</th>
                <th data-tip="Percentage of this player's last 20 games where they went over the line">L20</th>
                <th data-tip="Percentage of games in the 2023-24 season where the player went over the line">23-24</th>
                <th data-tip="Percentage of all games since 2022 where the player went over the line">All</th>
            </tr>
        </thead>
        <tbody>
    """)

    # Adjust your code to loop through final_results as dictionaries
    for row in final_results:
        projected_value = f"{row['Proj.']:.2f}"
        difference = f"{row['Diff.']:.2f}"
        weighted_prob = f"{row['Prob.']:.2f}"
        
        # Create links
        player_link = f'<a href="/hockey/players/{row["PlayerID"]}.html" target="_blank">{row["Player"]}</a>'
        team_link = f'<a href="/hockey/teams/{row["Team"]}.html" target="_blank">{row["Team"]}</a>'
        h2h_link = f'<a href="/hockey/h2h/{row["PlayerID"]}_vs_{row["Opp"]}.html" target="_blank">'
        h2h_cell = f'{h2h_link}{row["H2H"]}</a>'
        
        # Write the row
        f.write("<tr>")
        f.write(f"<td>{row['Game']}</td>")
        f.write(f"<td>{team_link}</td>")
        f.write(f"<td>{player_link}</td>")
        f.write(f"<td>{row['Type']}</td>")
        f.write(f"<td>{row['Stat']}</td>")
        f.write(f"<td>{row['Line']}</td>")
        f.write(f"<td>{projected_value}</td>")
        f.write(f"<td>{difference}</td>")
        f.write(f"<td>{weighted_prob}</td>")
        f.write(f"<td>{row['24-25']}</td>")
        f.write(f"<td>{h2h_cell}</td>")
        f.write(f"<td>{row['L5']}</td>")
        f.write(f"<td>{row['L10']}</td>")
        f.write(f"<td>{row['L20']}</td>")
        f.write(f"<td>{row['23-24']}</td>")
        f.write(f"<td>{row['All']}</td>")
        f.write("</tr>")
    
    f.write("""
        </tbody>
        </table>
    </div>
    <div class="footer"></div>
</body>
</html>
        """)

    print(f"HTML output saved to: {output_file_path}")
