import pandas as pd

# File paths
team_game_log_csv = r"C:\Users\ashle\Documents\Projects\hockey\data\gameindex.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\hockey\games\index.html"

# Load data and filter for unique GameID rows
team_game_data = pd.read_csv(team_game_log_csv)

# Start the HTML content
html_content = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Game Directory</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel=Stylesheet href=stylesheet.css>
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">

    <script>
    document.addEventListener("DOMContentLoaded", function () {{
        const table = document.getElementById("game-index");
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

            // Append sorted rows to tbody
            const tbody = table.querySelector("tbody");
            rows.forEach(row => tbody.appendChild(row));
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
        <h1>Game Directory</h1>
    </div>
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    <div class="button-container">
        <button id="toggle-selection-btn">Show Selected Only</button>
        <button id="clear-filters-btn">Remove Filters</button>
        <button id="clear-all-btn">Clear All</button>
     </div>
    <div id="index-container">
    <table id="game-index">
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
        <tr id="filter-row"></tr>
    </thead>
    <tbody>

"""

# Populate the table with each unique game
for _, row in team_game_data.iterrows():
    season = row["Season"]
    game_id = row["GameID"]
    game_name = row["Game"]
    game_date = row["Date"]
    home_id = row["HomeID"]
    home_name = row["Home"]
    away_id = row["AwayID"]
    away_name = row["Away"]
    home_goals = round(row["G"])
    away_goals = round(row["GA"])
    

    html_content += f"""
        <tr>
            <td style="text-align:center">{season}</td>
            <td style="text-align:left">{game_date}</td>
            <td style="text-align:left"><a href="/hockey/games/{game_id}.html">{game_name}</a></td>
            <td style="text-align:left"><a href="/hockey/teams/{home_id}.html">{home_name}</a></td>
            <td style="text-align:center;width:24px"><a href="/hockey/games/{game_id}.html">{home_goals}</a></td>
            <td style="text-align:left"><a href="/hockey/teams/{away_id}.html">{away_name}</a></td>
            <td style="text-align:center;width:24px"><a href="/hockey/games/{game_id}.html">{away_goals}</a></td>
        </tr>
    """

# Close the table and HTML tags
html_content += """
        </tbody>
    </table>
    <div class="footer"></div>
    </div>
</body>
</html>
"""

# Write the HTML content to a file
with open(output_file_path, "w") as file:
    file.write(html_content)

print(f"Game directory created at {output_file_path}")
