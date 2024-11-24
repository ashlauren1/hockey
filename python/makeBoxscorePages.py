import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\hockey\data"
output_dir_games = r"C:\Users\ashle\Documents\Projects\hockey\boxscores"

# Ensure output directory exists
os.makedirs(output_dir_games, exist_ok=True)

# **Load Data**
# Load game index data
game_index_csv = os.path.join(data_dir, "gameindex.csv")
game_index_data = pd.read_csv(game_index_csv)

# Load game logs data
gamelogs_csv = os.path.join(data_dir, "gamelogs.csv")
gamelogs_data = pd.read_csv(gamelogs_csv)

# **Part 1: Generate Game Directory (index.html)**
def create_game_directory(game_data, output_file_path):
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Game Directory</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <script>
        document.addEventListener("DOMContentLoaded", function () {
            const table = document.getElementById("boxscore-index");
            const headerRow = table.querySelector("thead tr:first-child");
            const filterRow = document.querySelector("#filter-row");
            const rows = Array.from(table.querySelectorAll("tbody tr"));

            // Add filters and sorting
            addFilters(table);
            addSortToHeaders(table);

            function addFilters(table) {
                const headerRow = table.querySelector("thead tr:first-child");
                const filterRow = document.createElement("tr");
                filterRow.id = "filter-row";
                Array.from(headerRow.cells).forEach((header, index) => {
                    const filterCell = document.createElement("td");
                    const filterSelect = document.createElement("select");
                    filterSelect.classList.add("filter-select");

                    filterSelect.innerHTML = '<option value="">All</option>';
                    const values = Array.from(new Set(
                        Array.from(table.querySelectorAll("tbody tr td:nth-child(" + (index + 1) + ")"))
                        .map(cell => cell.textContent.trim())
                    )).sort();

                    values.forEach(value => {
                        const option = document.createElement("option");
                        option.value = value;
                        option.textContent = value;
                        filterSelect.appendChild(option);
                    });

                    filterSelect.addEventListener("change", filterTable);
                    filterCell.appendChild(filterSelect);
                    filterRow.appendChild(filterCell);
                });
                table.querySelector("thead").appendChild(filterRow);
            }

            function filterTable() {
                const filters = Array.from(document.querySelectorAll(".filter-select")).map(select => select.value);
                rows.forEach(row => {
                    const cells = Array.from(row.cells);
                    const matchesFilter = filters.every((filter, i) => !filter || cells[i].textContent.trim() === filter);
                    row.style.display = matchesFilter ? "" : "none";
                });
            }

            function addSortToHeaders(table) {
                const headers = table.querySelectorAll("thead th");
                headers.forEach((header, index) => {
                    header.style.cursor = "pointer";
                    header.addEventListener("click", function () {
                        sortTable(table, index);
                    });
                });
            }

            function sortTable(table, columnIndex) {
                const rows = Array.from(table.querySelectorAll("tbody tr"));
                const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
                table.dataset.sortDirection = direction;

                // Detect data type
                let isNumeric = true;
                let isDate = true;
                for (let row of rows) {
                    const cellText = row.cells[columnIndex].textContent.trim();
                    if (cellText === '') continue; // Skip empty cells
                    if (isNumeric && isNaN(cellText)) {
                        isNumeric = false;
                    }
                    if (isDate && isNaN(Date.parse(cellText))) {
                        isDate = false;
                    }
                    if (!isNumeric && !isDate) break;
                }

                rows.sort((a, b) => {
                    const cellA = a.cells[columnIndex].textContent.trim();
                    const cellB = b.cells[columnIndex].textContent.trim();

                    let valA, valB;

                    if (isNumeric) {
                        valA = parseFloat(cellA);
                        valB = parseFloat(cellB);
                    } else if (isDate) {
                        valA = new Date(cellA);
                        valB = new Date(cellB);
                    } else {
                        valA = cellA.toLowerCase();
                        valB = cellB.toLowerCase();
                    }

                    if (valA < valB) {
                        return direction === "asc" ? -1 : 1;
                    } else if (valA > valB) {
                        return direction === "asc" ? 1 : -1;
                    } else {
                        return 0;
                    }
                });

                const tbody = table.querySelector("tbody");
                rows.forEach(row => tbody.appendChild(row));
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
        </script>
    </head>
    <body>
<div id="page-heading">
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
        <h1>Game Directory</h1>
    </div>
</div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    <div id="index-container">
        <table id="boxscore-index">
            <thead>
                <tr>
                    <th>Season</th>
                    <th>Date</th>
                    <th>Game</th>
                    <th>Home</th>
                    <th>Goals</th>
                    <th>Away</th>
                    <th>Goals</th>
                </tr>
            </thead>
            <tbody>
    """

    # Populate the table with each unique game
    for _, row in game_data.iterrows():
        season = row["Season"]
        game_id = row["GameID"]
        game_name = row["Game"]
        game_date = row["Date"]
        home_id = row["HomeID"]
        home_name = row["Home"]
        away_id = row["AwayID"]
        away_name = row["Away"]
        home_goals = int(round(row["G"]))
        away_goals = int(round(row["GA"]))

        html_content += f"""
                <tr>
                    <td style="text-align:center">{season}</td>
                    <td style="text-align:left">{game_date}</td>
                    <td style="text-align:left"><a href="/hockey/boxscores/{game_id}.html">{game_name}</a></td>
                    <td style="text-align:left"><a href="/hockey/teams/{home_id}.html">{home_name}</a></td>
                    <td style="text-align:center;width:24px"><a href="/hockey/boxscores/{game_id}.html">{home_goals}</a></td>
                    <td style="text-align:left"><a href="/hockey/teams/{away_id}.html">{away_name}</a></td>
                    <td style="text-align:center;width:24px"><a href="/hockey/boxscores/{game_id}.html">{away_goals}</a></td>
                </tr>
        """

    # Close the table and HTML tags
    html_content += """
            </tbody>
        </table>
    </div>
<div class="footer"></div>
</body>
</html>
    """

    # Write the HTML content to a file
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Game directory created at {output_file_path}")

# **Part 2: Generate Individual Game Boxscore Pages**
def create_game_boxscores(gamelogs_data, output_dir):
    grouped_data = gamelogs_data.groupby('GameID')

    for game_id, game_data in grouped_data:
        game_name = game_data.iloc[0]['Game']
        date = game_data.iloc[0]['Date']
        team_name = game_data.iloc[0]['TeamName']
        home_data = game_data[game_data['Is_Home'] == 1]
        away_data = game_data[game_data['Is_Home'] == 0]
        game_filename = f'{output_dir}/{game_id}.html'

        def calculate_totals(data):
            totals = data[['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK', 'PIM', 'EVG', 'PPG', 'SHG', 'EVA', 'PPA', 'SHA']].sum()
            return totals

        home_totals = calculate_totals(home_data)
        away_totals = calculate_totals(away_data)

        # Start HTML content for the game boxscore
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{game_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="stylesheet.css">
    <script src="boxscoreScript.js"></script>
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
</head>
<body>
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
	</div>
	<div class="header">
        <h1>{game_name} - {date}</h1>
    </div>
</div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    
<div id="boxscore-container">

    <div class="groupedProbAndButtons">
        <div class="button-container">
            <button id="toggle-selection-btn">Show Selected Only</button>
            <button id="clear-filters-btn">Remove Filters</button>
            <button id="clear-all-btn">Clear All</button>
        </div>
    </div>
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
    
        '''

        def create_team_table(team_data, team_name, totals, table_id):
            team_table = f'''
        <span class="caption">{team_name}</span>
        <table id="{table_id}">
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Team</th>
                    <th>G</th>
                    <th>A</th>
                    <th>PTS</th>
                    <th>SOG</th>
                    <th>HIT</th>
                    <th>BLK</th>
                    <th>TOI</th>
                    <th>PIM</th>
                    <th>EVG</th>
                    <th>PPG</th>
                    <th>SHG</th>
                    <th>EVA</th>
                    <th>PPA</th>
                    <th>SHA</th>
                </tr>
            </thead>
            <tbody>
            '''
            # Add rows for each player in the team data
            for _, row in team_data.iterrows():
                team_table += f'''
                <tr>
                    <td style="text-align:left"><a href="/hockey/players/{row['PlayerID']}.html" target="_blank">{row['Player']}</a></td>
                    <td style="text-align:left"><a href="/hockey/teams/{row['Team']}.html" target="_blank">{row['Team']}</a></td>
                    <td>{row['G']}</td>
                    <td>{row['A']}</td>
                    <td>{row['PTS']}</td>
                    <td>{row['SOG']}</td>
                    <td>{row['HIT']}</td>
                    <td>{row['BLK']}</td>
                    <td>{row['TOI']:.2f}</td>
                    <td>{row['PIM']}</td>
                    <td>{row['EVG']}</td>
                    <td>{row['PPG']}</td>
                    <td>{row['SHG']}</td>
                    <td>{row['EVA']}</td>
                    <td>{row['PPA']}</td>
                    <td>{row['SHA']}</td>
                </tr>
                '''
            # Add totals row in tfoot
            team_table += f'''
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="2"><strong>Total</strong></td>
                    <td>{int(totals['G'])}</td>
                    <td>{int(totals['A'])}</td>
                    <td>{int(totals['PTS'])}</td>
                    <td>{int(totals['SOG'])}</td>
                    <td>{int(totals['HIT'])}</td>
                    <td>{int(totals['BLK'])}</td>
                    <td></td>
                    <td>{int(totals['PIM'])}</td>
                    <td>{int(totals['EVG'])}</td>
                    <td>{int(totals['PPG'])}</td>
                    <td>{int(totals['SHG'])}</td>
                    <td>{int(totals['EVA'])}</td>
                    <td>{int(totals['PPA'])}</td>
                    <td>{int(totals['SHA'])}</td>
                </tr>
            </tfoot>
        </table>
            '''
            return team_table

        html_content += create_team_table(home_data, home_data.iloc[0]['TeamName'] + " - Home", home_totals, "home-boxscore")
        html_content += create_team_table(away_data, away_data.iloc[0]['TeamName'] + " - Away", away_totals, "away-boxscore")

        # Close HTML content
        html_content += '''
            </div>
            </div>
        <div class="footer"></div>
        </body>
        </html>
        '''

        with open(game_filename, 'w') as file:
            file.write(html_content)

    print("Game boxscore pages created successfully.")

# Create game directory
output_file_path = os.path.join(output_dir_games, "index.html")
create_game_directory(game_index_data, output_file_path)

# Create individual game boxscore pages
create_game_boxscores(gamelogs_data, output_dir_games)
