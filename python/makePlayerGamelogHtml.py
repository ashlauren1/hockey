import pandas as pd
import os

# Load the CSV file
file_path = r"C:\Users\ashle\Documents\Projects\hockey\data\gamelogs.csv"
data = pd.read_csv(file_path)

# Ensure output directory exists
output_dir = r"C:\Users\ashle\Documents\Projects\hockey\players"
os.makedirs(output_dir, exist_ok=True)

# Group data by PlayerID
grouped_data = data.groupby('PlayerID')

# Generate a separate HTML file for each player
for player_id, player_data in grouped_data:
    # Get player name from the data
    player_name = player_data.iloc[0]['Player']  # Assuming 'Player' column holds the name
    
    # File name based on PlayerID
    player_filename = f'{output_dir}/{player_id}.html'
    
    # Start HTML content for the player's gamelog
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
    <title>Gamelog for {player_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel=Stylesheet href=stylesheet.css>

    <script>
    document.addEventListener("DOMContentLoaded", function () {{
        const table = document.getElementById("gamelog-table");
        const headerRow = table.querySelector("thead tr:first-child");
        const filterRow = document.querySelector("#filter-row");
        const rows = Array.from(table.querySelectorAll("tbody tr"));
        const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
        const clearAllButton = document.getElementById("clear-all-btn");
        const clearButton = document.getElementById("clear-filters-btn");
        let showSelectedOnly = false;
        let isDragging = false;

        // Add filters and sorting
        addFilters(table);
        addSortToHeaders(table);

        // "Clear Filters" button functionality
        clearButton.addEventListener("click", () => {{
            document.querySelectorAll(".filter-select").forEach(select => select.value = "");
            filterTable();
        }});

        // "Clear All" functionality
        clearAllButton.addEventListener("click", () => {{
            document.querySelectorAll(".event-checkbox").forEach(checkbox => checkbox.checked = false);
            rows.forEach(row => {{
                row.classList.remove("selected-row");
                row.style.display = "";
            }});
            document.querySelectorAll(".filter-select").forEach(select => select.value = "");
            toggleSelectionBtn.textContent = "Show Selected Only";
            showSelectedOnly = false;
            filterTable();
        }});

        rows.forEach(row => {{
            row.addEventListener("mousedown", function () {{
                isDragging = true;
                toggleRowSelection(row);
            }});
            row.addEventListener("mouseenter", function () {{
                if (isDragging) toggleRowSelection(row);
            }});
            row.addEventListener("mouseup", () => isDragging = false);
        }});

        document.addEventListener("mouseup", () => isDragging = false);

        function toggleRowSelection(row) {{
            row.classList.toggle("selected-row");
        }}

        toggleSelectionBtn.addEventListener("click", () => {{
            showSelectedOnly = !showSelectedOnly;
            if (showSelectedOnly) {{
                rows.forEach(row => {{
                    row.style.display = row.classList.contains("selected-row") ? "" : "none";
                }});
                toggleSelectionBtn.textContent = "Show All";
            }} else {{
                rows.forEach(row => (row.style.display = ""));
                toggleSelectionBtn.textContent = "Show Selected Only";
            }}
        }});

        function addFilters(table) {{
            const headerRow = table.querySelector("thead tr:first-child");
            const filterRow = document.querySelector("#filter-row");

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

                filterSelect.addEventListener("change", filterTable);
                filterCell.appendChild(filterSelect);
                filterRow.appendChild(filterCell);
            }});
        }}

        function filterTable() {{
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
                header.addEventListener("click", function () {{
                    sortTable(table, index);
                }});
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
    }});
    </script>
    </head>
    <body>
    <div class="topnav">
        <a href="/">Projections</a>
        <a href="/players/">Players</a>
        <a href="/games/">Scores</a>
        <a href="/teams/">Teams</a>
    </div>    
    <div class="header">
    <h1>GAMELOG FOR {player_name}</h1>
    </div>
    <div class="button-container">
        <button id="toggle-selection-btn">Show Selected Only</button>
        <button id="clear-filters-btn">Remove Filters</button>
        <button id="clear-all-btn">Clear All</button>
    </div>
    <div id="gamelog-container">
        <table id="gamelog-table">
        <colgroup>
        <col style="width:70px">
        <col style="width:94px">
        <col span="17" style="width:48px"
        </colgroup>
            <thead>
                <tr>
                    <th>Season</th>
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
                    <th>EVG</th>
                    <th>PPG</th>
                    <th>SHG</th>
                    <th>EVA</th>
                    <th>PPA</th>
                    <th>SHA</th>
                </tr>
            <tr id="filter-row">
            </tr>
        </thead>
        <tbody>
    '''
    
    # Add rows for each game in the player's gamelog
    for _, row in player_data.iterrows():
        html_content += f'''
            <tr>
                <td style="text-align:left">{row['Season']}</td>
                <td style="text-align:left"><a href="/games/{row['GameID']}.html" target="_blank">{row['Date']}</a></td>
                <td><a href="/teams/{row['Team']}.html" target="_blank">{row['Team']}</a></td>
                <td>{'vs' if row['Is_Home'] == 1 else '@'}</td>
                <td><a href="/teams/{row['Opp']}.html" target="_blank">{row['Opp']}</a></td>
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
    
    # Close HTML content
    html_content += '''
            </tbody>
        </table>
        </div>
    </body>
    </html>
    '''
    
    # Write to HTML file
    with open(player_filename, 'w') as file:
        file.write(html_content)

print("Player gamelog pages created successfully.")
