import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\hockey\data"
output_dir = r"C:\Users\ashle\Documents\Projects\hockey\leaders"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# **Load Data**
leaders_csv = os.path.join(data_dir, "oldLeaders.csv")

# Load roster data
leader_data = pd.read_csv(leaders_csv)

# **Part 1: Generate Player Directory (index.html)**
def create_leader_directory(leader_data, output_file_path):
    leader_data.sort_values(by=["G", "A", "PTS"], ascending=[False, False, False], inplace=True)
    
    unique_seasons = leader_data["Season"].unique()
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NHL Season Leaders</title>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
<script>

document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll("#season-buttons button");
    const tables = document.querySelectorAll(".season-table");
    
    function showTable(seasonId) {
        tables.forEach(table => {
            table.style.display = table.id === seasonId ? "block" : "none";
        });
        buttons.forEach(button => {
            button.classList.toggle("active-button", button.dataset.season === seasonId);
        });
    }
    
    buttons.forEach(button => {
        button.addEventListener("click", () => {
            showTable(button.dataset.season);
        });
    });
    
    showTable(buttons[0].dataset.season);
});

document.addEventListener("DOMContentLoaded", function () {
    const tables = document.querySelectorAll("table");
    tables.forEach(addSortToHeaders);

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
        const direction = table.dataset.sortDirection === "desc" ? "asc" : "desc";
        table.dataset.sortDirection = direction;

        // Detect data type for sorting
        let isNumeric = true;
        let isDate = true;

        for (let row of rows) {
            const cellText = row.cells[columnIndex].textContent.trim();
            if (cellText === '') continue; // Skip empty cells
            if (isNumeric && isNaN(cellText)) isNumeric = false;
            if (isDate && isNaN(Date.parse(cellText))) isDate = false;
            if (!isNumeric && !isDate) break;
        }

        // Sort rows based on column type
        rows.sort((a, b) => {
            const cellA = a.cells[columnIndex].textContent.trim();
            const cellB = b.cells[columnIndex].textContent.trim();

            let valA, valB;
            if (isNumeric) {
                valA = parseFloat(cellA) || 0;
                valB = parseFloat(cellB) || 0;
            } else if (isDate) {
                valA = new Date(cellA);
                valB = new Date(cellB);
            } else {
                valA = cellA.toLowerCase();
                valB = cellB.toLowerCase();
            }

            if (valA < valB) return direction === "asc" ? -1 : 1;
            if (valA > valB) return direction === "asc" ? 1 : -1;
            return 0;
        });

        // Append sorted rows to the table body
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
</script>
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
		<h1>Season Leaders</h1>
	</div>
</div>
    <button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>
<main>
<div id="leaders-container">
    <div class="standings-button-container" id="season-buttons">
"""

    # Generate buttons for each season
    for season in unique_seasons:
        season_id = f"table{season.replace('-', '')}"
        html_content += f'<button data-season="{season_id}" class="season-button">{season}</button>'

    html_content += """
    </div>
    <div id="season-tables">
"""

    for season in sorted(unique_seasons, reverse=True):
        season_data = leader_data[leader_data["Season"] == season]
        season_id = f"table{season.replace('-', '')}"
        display_style = "block" if season == unique_seasons[0] else "none"
        html_content += f'<div id="{season_id}" class="season-table" style="display: {display_style};">'
        html_content += generate_html_table(season_data, f"{season} Leaders", season_id)
        html_content += "</div>"

    # Close HTML content
    html_content += """
    </div>
</body>
</html>
"""
    with open(output_file_path, "w") as file:
        file.write(html_content)    
    print(f"Leaders page created at {output_file_path}")


def generate_html_table(data, title, table_id):
    table_html = f'<table id="{table_id}" class="leaders-table">'
    table_html += """
        <thead>
            <tr>
                <th>Player</th>
                <th>Age</th>
                <th>Team</th>
                <th>Pos</th>
                <th data-tip="Games Played">GP</th>
                <th data-tip="Goals">G</th>
                <th data-tip="Assists">A</th>
                <th data-tip="Points">PTS</th>
                <th data-tip="Plus Minus">+/-</th>
                <th data-tip="Penalty Minutes">PIM</th>
                <th data-tip="Even Strength Goals">EVG</th>
                <th data-tip="Power Play Goals">PPG</th>
                <th data-tip="Short-Handed Goals">SHG</th>
                <th data-tip="Game-Winning Goals">GWG</th>
                <th data-tip="Even Strength Assists">EVA</th>
                <th data-tip="Power Play Assists">PPA</th>
                <th data-tip="Short-Handed Assists">SHA</th>
                <th data-tip="Shots on Goal">SOG</th>
                <th data-tip="Shooting Percentage">S%</th>
                <th data-tip="Shot Attemps">SAtt</th>
                <th data-tip="Time on Ice">TOI</th>
                <th data-tip="Average Time on Ice">ATOI</th>
                <th data-tip="Faceoff Wins">FOW</th>
                <th data-tip="Faceoff Losses">FOL</th>
                <th data-tip="Faceoff Percentage">FO%</th>
                <th data-tip="Blocked Shots">BLK</th>
                <th data-tip="Hits">HIT</th>
                <th data-tip="Takeaways">TAKE</th>
                <th data-tip="Giveaways">GIVE</th>
                <th data-tip="Awards">Awards</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for _, row in data.iterrows():
        team_id = row['Team']
        player_id = row['PlayerID']
        player_name = row['Player']
        plus_minus = f"{int(row['+/-']):+d}" if not pd.isna(row['+/-']) else ""
        player_cell = f'<td><a href="/hockey/players/{player_id}.html" target="_blank">{player_name}</a></td>'
        team_cell = f'<td><a href="/hockey/teams/{team_id}.html" target="_blank">{team_id}</a></td>'
        
        table_html += f'''
            <tr>
                {player_cell}
                <td>{row['Age'] if not pd.isna(row['Age']) else ""}</td>
                {team_cell}
                <td>{row['Pos'] if not pd.isna(row['Pos']) else ""}</td>
                <td>{row['GP'] if not pd.isna(row['GP']) else ""}</td>
                <td>{row['G'] if not pd.isna(row['G']) else ""}</td>
                <td>{row['A'] if not pd.isna(row['A']) else ""}</td>
                <td>{row['PTS'] if not pd.isna(row['PTS']) else ""}</td>
                <td>{plus_minus}</td>
                <td>{row['PIM'] if not pd.isna(row['PIM']) else ""}</td>
                <td>{row['EVG'] if not pd.isna(row['EVG']) else ""}</td>
                <td>{row['PPG'] if not pd.isna(row['PPG']) else ""}</td>
                <td>{row['SHG'] if not pd.isna(row['SHG']) else ""}</td>
                <td>{row['GWG'] if not pd.isna(row['GWG']) else ""}</td>
                <td>{row['EV'] if not pd.isna(row['EV']) else ""}</td>
                <td>{row['PP'] if not pd.isna(row['PP']) else ""}</td>
                <td>{row['SH'] if not pd.isna(row['SH']) else ""}</td>
                <td>{row['SOG'] if not pd.isna(row['SOG']) else ""}</td>
                <td>{row['SPCT'] if not pd.isna(row['SPCT']) else ""}</td>
                <td>{row['TSA'] if not pd.isna(row['TSA']) else ""}</td>
                <td>{row['TOI'] if not pd.isna(row['TOI']) else ""}</td>
                <td>{row['ATOI'] if not pd.isna(row['ATOI']) else ""}</td>
                <td>{row['FOW'] if not pd.isna(row['FOW']) else ""}</td>
                <td>{row['FOL'] if not pd.isna(row['FOL']) else ""}</td>
                <td>{row['FO%'] if not pd.isna(row['FO%']) else ""}</td>
                <td>{row['BLK'] if not pd.isna(row['BLK']) else ""}</td>
                <td>{row['HIT'] if not pd.isna(row['HIT']) else ""}</td>
                <td>{row['TAKE'] if not pd.isna(row['TAKE']) else ""}</td>
                <td>{row['GIVE'] if not pd.isna(row['GIVE']) else ""}</td>
                <td>{row['Awards'] if not pd.isna(row['Awards']) else ""}</td>
            </tr>
        '''
        
    table_html += "</tbody></table>"
    
    return table_html

# Create leader directory
output_file_path = os.path.join(output_dir, "pastSeasonLeaders.html")
create_leader_directory(leader_data, output_file_path)