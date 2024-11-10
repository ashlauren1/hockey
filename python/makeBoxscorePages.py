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
                .filter(([name]) => name.includes(query))  // Matches on both name and ID
                .slice(0, 5); // Limit to top 5

            matchingEntries.forEach(([name, url]) => {
                const resultItem = document.createElement("div");
                resultItem.classList.add("suggestion");

                // Proper case for names
                resultItem.textContent = name.split(" ")
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(" ");

                resultItem.addEventListener("click", () => {
                    window.open(url, "_blank");
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
            if (!searchContainer.contains(event.target)) {
                searchResults.style.display = "none";
            }
        });

        // Add event listener to search bar
        searchBar.addEventListener("input", updateSuggestions);
    });
        </script>
    </head>
    <body>
        <div class="topnav">
            <a href="/hockey/">Projections</a>
            <a href="/hockey/players/">Players</a>
            <a href="/hockey/boxscores/">Box Scores</a>
            <a href="/hockey/teams/">Teams</a>
        </div>
        <div id="search-container">
            <input type="text" id="search-bar" placeholder="Search for a player or team...">
            <button id="search-button">Search</button>
            <div id="search-results"></div>
        </div>
        <div class="header">
            <h1>Game Directory</h1>
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
        <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">

        <script>
        document.addEventListener("DOMContentLoaded", function () {{
            setupTableInteractions("home-boxscore");
            setupTableInteractions("away-boxscore");

            function setupTableInteractions(tableId) {{
                const table = document.getElementById(tableId);
                const rows = Array.from(table.querySelectorAll("tbody tr"));
                const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
                const clearAllButton = document.getElementById("clear-all-btn");
                const clearButton = document.getElementById("clear-filters-btn");
                let showSelectedOnly = false;
                let isDragging = false;

                addFilters(table);
                addSortToHeaders(table);

                clearButton.addEventListener("click", () => {{
                    document.querySelectorAll(".filter-select").forEach(select => select.value = "");
                    filterTable(table);
                }});

                clearAllButton.addEventListener("click", () => {{
                    rows.forEach(row => row.classList.remove("selected-row"));
                    document.querySelectorAll(".filter-select").forEach(select => select.value = "");
                    toggleSelectionBtn.textContent = "Show Selected Only";
                    showSelectedOnly = false;
                    filterTable(table);
                }});

                rows.forEach(row => {{
                    row.addEventListener("mousedown", () => {{ isDragging = true; toggleRowSelection(row); }});
                    row.addEventListener("mouseenter", () => {{ if (isDragging) toggleRowSelection(row); }});
                    row.addEventListener("mouseup", () => {{ isDragging = false; }});
                }});

                document.addEventListener("mouseup", () => {{ isDragging = false; }});

                toggleSelectionBtn.addEventListener("click", () => {{
                    showSelectedOnly = !showSelectedOnly;
                    rows.forEach(row => {{
                        row.style.display = showSelectedOnly && !row.classList.contains("selected-row") ? "none" : "";
                    }});
                    toggleSelectionBtn.textContent = showSelectedOnly ? "Show All" : "Show Selected Only";
                }});

                function toggleRowSelection(row) {{ row.classList.toggle("selected-row"); }}

                function addFilters(table) {{
                    const headerRow = table.querySelector("thead tr");
                    const filterRow = document.createElement("tr");
                    Array.from(headerRow.cells).forEach((header, index) => {{
                        const filterCell = document.createElement("td");
                        const filterSelect = document.createElement("select");
                        filterSelect.classList.add("filter-select");
                        filterSelect.innerHTML = '<option value="">All</option>';
                            const values = Array.from(new Set(
                            Array.from(table.querySelectorAll("tbody tr td:nth-child(" + (index + 1) + ")"))
                            .map(cell => cell.textContent.trim())
                        )).sort();
                        values.forEach(value => {{
                            const option = document.createElement("option");
                            option.value = value;
                            option.textContent = value;
                            filterSelect.appendChild(option);
                        }});
                        filterSelect.addEventListener("change", () => filterTable(table));
                        filterCell.appendChild(filterSelect);
                        filterRow.appendChild(filterCell);
                    }});
                    table.querySelector("thead").appendChild(filterRow);
                }}

                function filterTable(table) {{
                    const filters = Array.from(table.querySelectorAll(".filter-select")).map(select => select.value);
                    rows.forEach(row => {{
                        const cells = Array.from(row.cells);
                        const matchesFilter = filters.every((filter, i) => !filter || cells[i].textContent.trim() === filter);
                        row.style.display = matchesFilter ? "" : "none";
                    }});
                }}

                function addSortToHeaders(table) {{
                    const headers = table.querySelectorAll("thead th");
                    headers.forEach((header, index) => {{
                        header.style.cursor = "pointer";
                        header.addEventListener("click", () => sortTable(table, index));
                    }});
                }}

                function sortTable(table, columnIndex) {{
                    const rows = Array.from(table.querySelectorAll("tbody tr"));
                    const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
                    table.dataset.sortDirection = direction;

                    // Detect data type
                    let isNumeric = true;
                    let isDate = true;
                    for (let row of rows) {{
                        const cellText = row.cells[columnIndex].textContent.trim();
                        if (cellText === '') continue; // Skip empty cells
                        if (isNumeric && isNaN(cellText)) {{
                            isNumeric = false;
                        }}
                        if (isDate && isNaN(Date.parse(cellText))) {{
                            isDate = false;
                        }}
                        if (!isNumeric && !isDate) break;
                    }}

                    rows.sort((a, b) => {{
                        const cellA = a.cells[columnIndex].textContent.trim();
                        const cellB = b.cells[columnIndex].textContent.trim();

                        let valA, valB;

                        if (isNumeric) {{
                            valA = parseFloat(cellA);
                            valB = parseFloat(cellB);
                        }} else if (isDate) {{
                            valA = new Date(cellA);
                            valB = new Date(cellB);
                        }} else {{
                            valA = cellA.toLowerCase();
                            valB = cellB.toLowerCase();
                        }}

                        if (valA < valB) {{
                            return direction === "asc" ? -1 : 1;
                        }} else if (valA > valB) {{
                            return direction === "asc" ? 1 : -1;
                        }} else {{
                            return 0;
                        }}
                    }});
                    rows.forEach(row => table.querySelector("tbody").appendChild(row));
                }}
            }}
        }});
            document.addEventListener("DOMContentLoaded", async function () {{
            const searchBar = document.getElementById("search-bar");
            const searchResults = document.getElementById("search-results");

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
                    .filter(([name]) => name.includes(query))  // Matches on both name and ID
                    .slice(0, 5); // Limit to top 5

                matchingEntries.forEach(([name, url]) => {{
                    const resultItem = document.createElement("div");
                    resultItem.classList.add("suggestion");

                    // Proper case for names
                    resultItem.textContent = name.split(" ")
                        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                        .join(" ");

                    resultItem.addEventListener("click", () => {{
                        window.open(url, "_blank");
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
                if (!searchContainer.contains(event.target)) {{
                    searchResults.style.display = "none";
                }}
            }});

            // Add event listener to search bar
            searchBar.addEventListener("input", updateSuggestions);
    }});
        
        </script>
        </head>
        <body>
        <div class="topnav">
            <a href="/hockey/">Projections</a>
            <a href="/hockey/players/">Players</a>
            <a href="/hockey/boxscores/">Box Scores</a>
            <a href="/hockey/teams/">Teams</a>
        </div>
        <div id="search-container">
            <input type="text" id="search-bar" placeholder="Search for a player or team...">
            <button id="search-button">Search</button>
            <div id="search-results"></div>
        </div>
        <div class="header">
        <h1>{game_name} - {date}</h1>
        </div>
        <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
        <div id="boxscore-container">
        <div id="table-container">
        '''

        def create_team_table(team_data, team_name, totals, table_id):
            team_table = f'''
            <span class="table-button-container">
                <span class="caption">{team_name}</span>
                <button id="toggle-selection-btn">Show Selected Only</button>
                <button id="clear-filters-btn">Remove Filters</button>
                <button id="clear-all-btn">Clear All</button>
            </span>
            <table id="{table_id}">
            <colgroup>
                <col style="width:136px">
                <col span="15" style="width:48px">
            </colgroup>
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
