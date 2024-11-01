import pandas as pd
import os

# Load the CSV file
file_path = r"C:\Users\ashle\Documents\Projects\hockey\data\gamelogs.csv"
data = pd.read_csv(file_path)

# Ensure output directory exists
output_dir = r"C:\Users\ashle\Documents\Projects\hockey\games"
os.makedirs(output_dir, exist_ok=True)

# Group data by GameID
grouped_data = data.groupby('GameID')

# Generate a separate HTML file for each player
for game_id, game_data in grouped_data:
    # Get player name from the data
    game_name = game_data.iloc[0]['Game']
    home_data = game_data[game_data['Is_Home'] == 1]
    away_data = game_data[game_data['Is_Home'] == 0]
    game_filename = f'{output_dir}/{game_id}.html'
    
    def calculate_totals(data):
        totals = data[['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK', 'PIM', 'EVG', 'PPG', 'SHG', 'EVA', 'PPA', 'SHA']].sum()
        return totals

    home_totals = calculate_totals(home_data)
    away_totals = calculate_totals(away_data)
    
    # Start HTML content for the player's gamelog
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
    <title>{game_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel=Stylesheet href=stylesheet.css>
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    
    <script>
    document.addEventListener("DOMContentLoaded", function () {{
        setupTableInteractions("home-boxscore");
        setupTableInteractions("away-boxscore");

        function setupTableInteractions(tableId) {{
            const table = document.getElementById(tableId);
            const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
            const clearAllButton = document.getElementById("clear-all-btn");
            const clearButton = document.getElementById("clear-filters-btn");
            const rows = Array.from(table.querySelectorAll("tbody tr"));
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
                const filters = Array.from(document.querySelectorAll(".filter-select")).map(select => select.value);
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
                const isNumeric = rows.every(row => !isNaN(row.cells[columnIndex].textContent.trim()));
                const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
                table.dataset.sortDirection = direction;
                rows.sort((a, b) => {{
                    const cellA = a.cells[columnIndex].textContent.trim();
                    const cellB = b.cells[columnIndex].textContent.trim();
                    const valA = isNumeric ? parseFloat(cellA) : cellA.toLowerCase();
                    const valB = isNumeric ? parseFloat(cellB) : cellB.toLowerCase();
                    return direction === "asc" ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
                }});
                rows.forEach(row => table.querySelector("tbody").appendChild(row));
            }}
        }}
    }});
    </script>
    </head>
    <body>
    <div class="topnav">
        <a href="/hockey/">Projections</a>
        <a href="/hockey/players/">Players</a>
        <a href="/hockey/games/">Scores</a>
        <a href="/hockey/teams/">Teams</a>
    </div>    
    <div id="page-title" class="header">
    <h1>{game_name} Boxscore</h1>
    </div>
    <div class="button-container">
        <button id="toggle-selection-btn">Show Selected Only</button>
        <button id="clear-filters-btn">Remove Filters</button>
        <button id="clear-all-btn">Clear All</button>
    </div>
    <div><button class="arrowUp"><a href="#page-title">Top</a></button></div>
    <div id="boxscore-container">
    '''
    
    def create_team_table(team_data, team_name, totals, table_id):
        team_table = f'''
        <table id="{table_id}">
        <caption>{team_name} Boxscore</caption>
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
                    <td>{totals['G']}</td>
                    <td>{totals['A']}</td>
                    <td>{totals['PTS']}</td>
                    <td>{totals['SOG']}</td>
                    <td>{totals['HIT']}</td>
                    <td>{totals['BLK']}</td>
                    <td></td>
                    <td>{totals['PIM']}</td>
                    <td>{totals['EVG']}</td>
                    <td>{totals['PPG']}</td>
                    <td>{totals['SHG']}</td>
                    <td>{totals['EVA']}</td>
                    <td>{totals['PPA']}</td>
                    <td>{totals['SHA']}</td>
                </tr>
            </tfoot>
        </table>
        '''
        return team_table
    
    html_content += create_team_table(home_data, home_data.iloc[0]['Team'] + " (Home)", home_totals, "home-boxscore")
    html_content += create_team_table(away_data, away_data.iloc[0]['Team'] + " (Away)", away_totals, "away-boxscore")
    
    # Close HTML content
    html_content += '''
        </div>
    </body>
    </html>
    '''
        
    with open(game_filename, 'w') as file:
        file.write(html_content)

print("game boxscore pages created successfully.")
