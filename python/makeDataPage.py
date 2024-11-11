import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\hockey\data"
output_file = r"C:\Users\ashle\Documents\Projects\hockey\stats\index.html"

# Load game index data
gamelogs_csv = os.path.join(data_dir, "gamelogsNormalPlayers.csv")
gamelogs_data = pd.read_csv(gamelogs_csv)

# Start HTML content for the player's gamelog
html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
    <title>All Stats</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <script>
    document.addEventListener("DOMContentLoaded", function () {{
        const table = document.getElementById("allStats-table");
        const headerRow = table.querySelector("thead tr:first-child");
        const filterRow = document.querySelector("#filter-row");
        const rows = Array.from(table.querySelectorAll("tbody tr"));
        const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
        const clearAllButton = document.getElementById("clear-all-btn");
        const clearButton = document.getElementById("clear-filters-btn");
        let showSelectedOnly = false;
        let isDragging = false;

        const rowsPerPage = 500;
        let currentPage = 1;
        let totalPages = Math.ceil(rows.length / rowsPerPage);

        document.getElementById('total-pages').textContent = totalPages;

        function displayPage(page) {{
            const start = (page - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            rows.forEach((row, index) => {{
                row.style.display = (index >= start && index < end) ? '' : 'none';
            }});
            document.getElementById('current-page').textContent = page;
        }}

        document.getElementById('prev-page-btn').addEventListener('click', () => {{
            if (currentPage > 1) {{
                currentPage--;
                displayPage(currentPage);
            }}
        }});

        document.getElementById('next-page-btn').addEventListener('click', () => {{
            if (currentPage < totalPages) {{
                currentPage++;
                displayPage(currentPage);
            }}
        }});

        displayPage(currentPage);

        function filterTable() {{
            const filters = Array.from(document.querySelectorAll(".filter-select")).map(select => select.value);
            let visibleRows = 0;
            rows.forEach(row => {{
                const cells = Array.from(row.cells);
                const matchesFilter = filters.every((filter, i) => !filter || cells[i].textContent.trim() === filter);
                row.style.display = matchesFilter ? '' : 'none';
                if (matchesFilter) visibleRows++;
            }});
            currentPage = 1;
            totalPages = Math.ceil(visibleRows / rowsPerPage);
            document.getElementById('total-pages').textContent = totalPages;
            displayPage(currentPage);
        }}

        function sortTable(columnIndex) {{
            const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
            table.dataset.sortDirection = direction;

            let isNumeric = true;
            rows.sort((a, b) => {{
                const cellA = a.cells[columnIndex].textContent.trim();
                const cellB = b.cells[columnIndex].textContent.trim();
                if (isNumeric && (isNaN(cellA) || isNaN(cellB))) isNumeric = false;
                return isNumeric ? direction === "asc" ? cellA - cellB : cellB - cellA
                                : direction === "asc" ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            }});

            rows.forEach(row => table.querySelector("tbody").appendChild(row));
            displayPage(currentPage);
        }}

        function addFilters() {{
            Array.from(headerRow.cells).forEach((header, index) => {{
                const filterCell = document.createElement("td");
                const filterSelect = document.createElement("select");
                filterSelect.classList.add("filter-select");
                filterSelect.innerHTML = '<option value="">All</option>';
                const values = Array.from(new Set(rows.map(row => row.cells[index].textContent.trim()))).sort();
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

        addFilters();
        displayPage(currentPage);
    }});
    </script>
    </head>
    <body>
    <div class="topnav">
        <a href="/hockey/" target="_blank">Projections</a>
        <a href="/hockey/players/" target="_blank">Players</a>
        <a href="/hockey/boxscores/" target="_blank">Box Scores</a>
        <a href="/hockey/teams/" target="_blank">Teams</a>
        <a href="/hockey/stats/" target="_blank">All Stats</a>
        <a href="https://ashlauren1.github.io/basketball/" target="_blank">Basketball</a>
    </div>
    <div id="search-container">
        <input type="text" id="search-bar" placeholder="Search for a player or team...">
        <button id="search-button">Search</button>
    <div id="search-results"></div>
    <div class="header">
    <h1>All Data</h1>
    </div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>

    <div id="player-container">
    
    <div id="table-container">
    <span class="table-button-container">
    <caption class="caption">Gamelogs for all players who played at least 8 minutes since 1/1/2024. Click <a href="/hockey/data/gamelogs.csv" download="gamelogs">here</a> to download all data for all players since 2022, regardless of minutes played.</caption>
        <button id="toggle-selection-btn">Show Selected Only</button>
        <button id="clear-filters-btn">Remove Filters</button>
        <button id="clear-all-btn">Clear All</button>
    </span>
    <div id="pagination">
        <button id="prev-page-btn">Previous</button>
        <span id="page-info">Page <span id="current-page">1</span> of <span id="total-pages"></span></span>
        <button id="next-page-btn">Next</button>
    </div>
        <table id="allStats-table">
            <thead>
            <tr>
                <th>Season</th>
                <th>Date</th>
                <th>Player</th>
                <th>Team</th>
                <th></th>
                <th>Opp</th>
                <th>Goal</th>
                <th>Ast</th>
                <th>PTS</th>
                <th>SOG</th>
                <th>HIT</th>
                <th>BLK</th>
                <th>TOI</th>
                <th>PIM</th>
                <th>EV Goal</th>
                <th>PP Goal</th>
                <th>SH Goal</th>
                <th>EV Ast</th>
                <th>PP Ast</th>
                <th>SH Ast</th>   
            </tr>
            <tr id="filter-row"></tr>
        </thead>
        <tbody>
'''


for _, row in gamelogs_data.iterrows():
    html_content += f'''
        <tr>
            <td style="text-align:left">{row['Season']}</td>
            <td style="text-align:left"><a href="/hockey/boxscores/{row['GameID']}.html" target="_blank">{row['Date']}</a></td>
            <td style="text-align:left"><a href="/hockey/players/{row['PlayerID']}.html" target="_blank">{row['Player']}</a></td>
            <td><a href="/hockey/teams/{row['Team']}.html" target="_blank">{row['Team']}</a></td>
            <td>{'vs' if row['Is_Home'] == 1 else '@'}</td>
            <td><a href="/hockey/teams/{row['Opp']}.html" target="_blank">{row['Opp']}</a></td>
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
    </div>
    <div class="footer"></div>
</body>
</html>
'''

# Write to HTML file
with open(output_file, 'w') as file:
    file.write(html_content)

print("All stats HTML file created successfully.")