import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\hockey\data"
output_dir = r"C:\Users\ashle\Documents\Projects\hockey\leaders"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# **Load Data**
leaders_csv = os.path.join(data_dir, "leaders.csv")
team_leaders_csv = os.path.join(data_dir, "leaderTeams.csv")

# Load roster data
leader_data = pd.read_csv(leaders_csv)
leader_data.sort_values(by=["G", "PlayerID"], ascending=[False, True], inplace=True)


# Load gamelogs data
team_leaders_data = pd.read_csv(team_leaders_csv)

# **Part 1: Generate Player Directory (index.html)**
def create_leader_directory(leader_data, output_file_path):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2024-25 Leaders</title>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
<script>
document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("leader-index");
    const rows = Array.from(table.querySelectorAll("tbody tr"));
	const clearButton = document.getElementById("leaders-clear-filters-btn");
	
	const teamSelect = document.getElementById("teams");
    const positionSelect = document.getElementById("pos");

    // Attach event listeners to both select inputs
    teamSelect.addEventListener("change", filterTable);
    positionSelect.addEventListener("change", filterTable);

    function filterTable() {
        // Get the current filter values
        const teamFilter = teamSelect.value;
        const positionFilter = positionSelect.value;

        rows.forEach(row => {
            const cells = row.cells;

            // Check if the row matches both filters
            const matchesTeam = !teamFilter || cells[1].textContent.trim().toLowerCase() === teamFilter;
            const matchesPosition = !positionFilter || cells[2].textContent.trim().toLowerCase() === positionFilter;

            // Show or hide the row based on filter match
            row.style.display = matchesTeam && matchesPosition ? "" : "none";
        });
    }
	
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
	
	function sortTable(table, columnIndex) {
		const rows = Array.from(table.querySelectorAll("tbody tr"));
		const direction = table.dataset.sortDirection === "desc" ? "asc" : "desc";
		table.dataset.sortDirection = direction;

		rows.sort((a, b) => {
			let cellA = a.cells[columnIndex].textContent.trim();
			let cellB = b.cells[columnIndex].textContent.trim();

			let valA, valB;
			
			
			const isPercentage = cellA.includes('%') && cellB.includes('%');
			if (isPercentage) {
				valA = parseFloat(cellA.replace('%', '')); // Remove '%' and parse as float
				valB = parseFloat(cellB.replace('%', ''));
			} else if (!isNaN(cellA) && !isNaN(cellB)) {
				// Numeric values
				valA = parseFloat(cellA);
				valB = parseFloat(cellB);
			} else {
				// String values
				valA = cellA.toLowerCase();
				valB = cellB.toLowerCase();
			}

			// Compare values
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
	
	// "Clear Filters" button functionality
	
	clearButton.addEventListener("click", () => {
		document.querySelectorAll("select").forEach(select => select.value = "");
		filterTable();
	});
});
    const teamSelect = document.getElementById("teams");
    const positionSelect = document.getElementById("pos");

		
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
    const glossaryContainer = document.getElementById("glossary-placeholder");
    const glossaryButton = document.createElement("button");
    glossaryButton.id = "glossaryButton";
    glossaryButton.innerText = "Glossary";
    glossaryContainer.appendChild(glossaryButton);

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
	</div>
	<div class="header">
		<h1>2024-25 Leaders</h1>
	</div>
</div>
    <button class="arrowUp" onclick="window.scrollTo({top: 0})">Top</button>

<div id="leaders-container">    
    
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
    
    <div id="filter-container-div">
        <div id="filter-div">
            <form class="team-filters">
                <label for="teams">Team</label>
                <select id="teams" name="teams">
                    <option value="">All</option>
                    <option value="ana">Anaheim Ducks</option>
                    <option value="ari">Arizona Coyotes</option>
                    <option value="bos">Boston Bruins</option>
                    <option value="buf">Buffalo Sabres</option>
                    <option value="car">Carolina Hurricanes</option>
                    <option value="cbj">Columbus Blue Jackets</option>
                    <option value="cgy">Calgary Flames</option>
                    <option value="chi">Chicago Blackhawks</option>
                    <option value="col">Colorado Avalanche</option>
                    <option value="dal">Dallas Stars</option>
                    <option value="det">Detroit Red Wings</option>
                    <option value="edm">Edmonton Oilers</option>
                    <option value="fla">Florida Panthers</option>
                    <option value="lak">Los Angeles Kings</option>
                    <option value="min">Minnesota Wild</option>
                    <option value="mtl">Montreal Canadiens</option>
                    <option value="njd">New Jersey Devils</option>
                    <option value="nsh">Nashville Predators</option>
                    <option value="nyi">New York Islanders</option>
                    <option value="nyr">New York Rangers</option>
                    <option value="ott">Ottawa Senators</option>
                    <option value="phi">Philadelphia Flyers</option>
                    <option value="pit">Pittsburgh Penguins</option>
                    <option value="sea">Seattle Kraken</option>
                    <option value="sjs">San Jose Sharks</option>
                    <option value="stl">St. Louis Blues</option>
                    <option value="tbl">Tampa Bay Lightning</option>
                    <option value="tor">Toronto Maple Leafs</option>
                    <option value="van">Vancouver Canucks</option>
                    <option value="veg">Vegas Golden Knights</option>
                    <option value="wpg">Winnipeg Jets</option>
                    <option value="wsh">Washington Capitals</option>
                </select>
            </form>
            <form class="position-filters">
                <label for="position">Position</label>
                <select id="pos" name="pos">
                    <option value="">All</option>
                    <option value="d">Defensemen</option>
                    <option value="f">Forwards</option>
                </select>
            </form>
        </div>
        <div class="filter-button-container">
            <button id="leaders-clear-filters-btn">Remove Filters</button>
        </div>
        <div id="glossary-placeholder"></div>
    </div>
        
    <table id="leader-index">
        <thead>
            <tr>
                <th>Player</th>
                <th>Team</th>
                <th>Pos.</th>
                <th data-tip="Games Played">GP</th>
                <th data-tip="Goals">G</th>
                <th data-tip="Assists">A</th>
                <th data-tip="Points">PTS</th>
                <th data-tip="Shots on Goal">SOG</th>
                <th data-tip="Shooting %">S%</th>
                <th data-tip="Hits">HIT</th>
                <th data-tip="Blocks">BLK</th>
                <th data-tip="Time on Ice">TOI</th>
                <th data-tip="Shot Attempts">SAtt</th>
                <th data-tip="Penalty Minutes">PIM</th>
                <th data-tip="Even Strength Goals">EVG</th>
                <th data-tip="Power Play Goals">PPG</th>
                <th data-tip="Short-Handed Goals">SHG</th>
                <th data-tip="Even Strength Assists">EVA</th>
                <th data-tip="Power Play Assists">PPA</th>
                <th data-tip="Short-Handed Assists">SHA</th>
                <th data-tip="Goals per Game">G/GP</th>
                <th data-tip="Assists per Game">A/GP</th>
                <th data-tip="Points per Game">PTS/GP</th>
                <th data-tip="Shots on Goal per Game">SOG/GP</th>
                <th data-tip="Hits per Game">HIT/GP</th>
                <th data-tip="Blocks per Game">BLK/GP</th>
                <th data-tip="Time on Ice per Game">TOI/GP</th>
                <th data-tip="Shot Attempts per Game">SAtt/GP</th>
                <th data-tip="Penalty Minutes per Game">PIM/GP</th>
            </tr>
        </thead>
        <tbody>
    """

    # Generate table rows grouped by team
    for _, row in leader_data.iterrows():
        team_id = row["TeamID"]
        player_id = row["PlayerID"]
        player_name = row["Player"]
        position = row["Position"]
        
        # Add player row
        html_content += f"""
            <tr>
                <td style="text-align:left"><a href="/hockey/players/{player_id}.html">{player_name}</a></td>
                <td><a href="/hockey/teams/{team_id}.html">{team_id}</a></td>
                <td style="text-align:center">{position}</td>
                <td>{int(row['GP'])}</td>
                <td>{int(row['G'])}</td>
                <td>{int(row['A'])}</td>
                <td>{int(row['PTS'])}</td>
                <td>{int(row['SOG'])}</td>
                <td>{row['S%']:.2f}%</td>
                <td>{int(row['HIT'])}</td>
                <td>{int(row['BLK'])}</td>
                <td>{row['TOI']:.2f}</td>
                <td>{int(row['SAtt'])}</td>
                <td>{int(row['PIM'])}</td>
                <td>{int(row['EVG'])}</td>
                <td>{int(row['PPG'])}</td>
                <td>{int(row['SHG'])}</td>
                <td>{int(row['EVA'])}</td>
                <td>{int(row['PPA'])}</td>
                <td>{int(row['SHA'])}</td>
                <td>{row['G_GP']:.2f}</td>
                <td>{row['A_GP']:.2f}</td>
                <td>{row['PTS_GP']:.2f}</td>
                <td>{row['SOG_GP']:.2f}</td>
                <td>{row['HIT_GP']:.2f}</td>
                <td>{row['BLK_GP']:.2f}</td>
                <td>{row['TOI_GP']:.2f}</td>
                <td>{row['SAtt_GP']:.2f}</td>
                <td>{row['PIM_GP']:.2f}</td>
            </tr>
        """

    # Close the single <tbody>, table, and HTML tags
    html_content += """
        </tbody>
    </table>
</div>
<div class="footer"></div>
<script>
var topnav = document.getElementById("topnav");
var navBtns = topnav.getElementsByClassName("topnav-item");
for (var i = 0; i < navBtns.length; i++) {
    navBtns[i].addEventListener("click", function() {
        var current = document.getElementsByClassName("active");
        current[0].className = current[0].className.replace(" active", "");
        this.className += " active";
    });
};
</script>
</body>
</html>
    """

    # Write the HTML content to a file
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Leaders directory created at {output_file_path}")


def create_team_leader_directory(team_leaders_data, output_dir):
    team_leaders_data.sort_values(
        by=["Points", "PtsPct", "RW", "W", "GDiff"],
        ascending=[False, False, False, False, False],
        inplace=True,
    )
    
    league_table = team_leaders_data
    
    conference_tables = {
        "Eastern": team_leaders_data[team_leaders_data["Conference"] == "Eastern"],
        "Western": team_leaders_data[team_leaders_data["Conference"] == "Western"],
    }
    
    division_order = ["Atlantic", "Metropolitan", "Central", "Pacific"]
    conference_headers = {
        "Eastern Conference": ["Atlantic", "Metropolitan"],
        "Western Conference": ["Central", "Pacific"],
    }
    
    division_tables = {
        division: team_leaders_data[team_leaders_data["Division"] == division]
        for division in division_order
    }
    
    html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>2024-25 Standings</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">

<script>
document.addEventListener("DOMContentLoaded", function () {{
    const leagueTable = document.getElementById("league-table-container");
    const conferenceTables = document.getElementById("conference-table-container");
    const divisionTables = document.getElementById("division-table-container");
        
    const buttons = {{
        league: document.getElementById("btn-league"),
        conference: document.getElementById("btn-conference"),
        division: document.getElementById("btn-division"),
    }};	
	
    leagueTable.style.display = "none";
    conferenceTables.style.display = "none";
    divisionTables.style.display = "block";
	
	buttons.division.classList.add("active-button");

    function showTable(view) {{
        leagueTable.style.display = view === "league" ? "block" : "none";
        conferenceTables.style.display = view === "conference" ? "block" : "none";
        divisionTables.style.display = view === "division" ? "block" : "none";
		
		Object.values(buttons).forEach(button => button.classList.remove("active-button"));

        // Add "active-button" class to the corresponding button
        buttons[view].classList.add("active-button");
    }}

    document.getElementById("btn-league").addEventListener("click", () => showTable("league"));
    document.getElementById("btn-conference").addEventListener("click", () => showTable("conference"));
    document.getElementById("btn-division").addEventListener("click", () => showTable("division"));

}});


document.addEventListener("DOMContentLoaded", function () {{
    const tables = document.querySelectorAll("table");
    tables.forEach(addSortToHeaders);

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
        const direction = table.dataset.sortDirection === "desc" ? "asc" : "desc";
        table.dataset.sortDirection = direction;

        // Detect data type for sorting
        let isNumeric = true;
        let isDate = true;

        for (let row of rows) {{
            const cellText = row.cells[columnIndex].textContent.trim();
            if (cellText === '') continue; // Skip empty cells
            if (isNumeric && isNaN(cellText)) isNumeric = false;
            if (isDate && isNaN(Date.parse(cellText))) isDate = false;
            if (!isNumeric && !isDate) break;
        }}

        // Sort rows based on column type
        rows.sort((a, b) => {{
            const cellA = a.cells[columnIndex].textContent.trim();
            const cellB = b.cells[columnIndex].textContent.trim();

            let valA, valB;
            if (isNumeric) {{
                valA = parseFloat(cellA) || 0;
                valB = parseFloat(cellB) || 0;
            }} else if (isDate) {{
                valA = new Date(cellA);
                valB = new Date(cellB);
            }} else {{
                valA = cellA.toLowerCase();
                valB = cellB.toLowerCase();
            }}

            if (valA < valB) return direction === "asc" ? -1 : 1;
            if (valA > valB) return direction === "asc" ? 1 : -1;
            return 0;
        }});

        // Append sorted rows to the table body
        const tbody = table.querySelector("tbody");
        rows.forEach(row => tbody.appendChild(row));
    }}
}});

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
    const headers = document.querySelectorAll("thead th[data-tip]");

    headers.forEach(header => {{
        const tooltip = document.createElement("span");
        tooltip.className = "tooltip inactive"; // Add both classes initially
        tooltip.textContent = header.getAttribute("data-tip");
        document.body.appendChild(tooltip);

        // Show tooltip on mouseover
        header.addEventListener("mouseover", () => {{
            tooltip.classList.add("active");
            tooltip.classList.remove("inactive");

            const rect = header.getBoundingClientRect();
            tooltip.style.left = rect.left + "px"; // Align with header
            tooltip.style.top = (rect.top + window.scrollY - tooltip.offsetHeight + 6) + "px"; // Above header, add a small gap
        }});

        // Hide tooltip on mouseout
        header.addEventListener("mouseout", () => {{
            tooltip.classList.remove("active");
            tooltip.classList.add("inactive");
        }});
    }});
}});

document.addEventListener("DOMContentLoaded", function () {{
    var modal = document.getElementById("tiebreakerModal");
    var modalButton = document.getElementById("tiebreakerInfoButton");
    var modalContent = document.querySelector("modal-content");
    var closeModal = document.getElementsByClassName("close")[0];

    modalButton.onclick = function() {{
        modal.classList.add("open");
        modal.style.display = "block";
    }}

    closeModal.onclick = function() {{
        modal.classList.remove("open");
        modal.style.display = "none";
    }}
    
    window.onclick = function(event) {{
        if (event.target === modal) {{
            modal.style.display = "none";
        }}
    }}
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
    const divisionContainer = document.getElementById("division-table-container");

    const tiebreakerButton = document.createElement("button");
    tiebreakerButton.id = "tiebreakerInfoButton";
    tiebreakerButton.innerText = "Tiebreaker Info";
    divisionContainer.querySelector(".title-caption").appendChild(tiebreakerButton);

    const glossaryButton = document.createElement("button");
    glossaryButton.id = "glossaryButton";
    glossaryButton.innerText = "Glossary";
    divisionContainer.querySelector(".title-caption").appendChild(glossaryButton);

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

    // Setup Tiebreaker Modal
    setupModal("tiebreakerModal", "tiebreakerInfoButton", "close");

    // Setup Glossary Modal
    setupModal("glossaryModal", "glossaryButton", "closeGlossary");
}});
</script>
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
		<h1>2024-25 Standings</h1>
	</div>
</div>

    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
    
<div id="standingsContainer">
    <div class="standings-button-container">
        <button id="btn-league">League</button>
        <button id="btn-conference">Conference</button>
        <button id="btn-division">Division</button>
    </div>
    
    <div id="tiebreakerModal" class="modal">
        <div id="modal-content">
            <span class="close">&times;</span>
            <p class="tiebreaker-modal-content">In the event that two or more teams are tied in points, rankings are determined by the following tiebreakers:</p>
            <ul class="tiebreaker-modal-list" type="none">
                <li>1.&nbsp;&nbsp;Points percentage (Pts%)</li>
                <li>2.&nbsp;&nbsp;Regulation wins (RW)</li>
                <li>3.&nbsp;&nbsp;Regulation and overtime wins, excluding shootout wins (ROW)</li>
                <li>4.&nbsp;&nbsp;Total wins, including overtime and shootout wins (W)</li>
                <li>5.&nbsp;&nbsp;Points earned in games against the other tied teams</li>
                <li>6.&nbsp;&nbsp;Goal differential (Diff.)</li>
                <li>7.&nbsp;&nbsp;Total goals scored (GF)</li>
            </ul>
        </div>
    </div>
    
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
    
    # Add League Table
    html_content += f'<div id="league-table-container" style="display: none;">'
    html_content += generate_html_table(league_table, "League Standings", "league-standings", division_table=False)
    html_content += '''
        </div>
        '''

    # Add Division Tables with Conference Headers
    html_content += '<div id="division-table-container" style="display: block;">'
    for conference, divisions in conference_headers.items():
        html_content += f'<p class="title-caption">{conference}</p>'
        for division in divisions:
            division_table = team_leaders_data[team_leaders_data["Division"] == division]
            html_content += generate_html_table(
                division_table, f"{division} Division", f"{division.lower()}-division", division_table=True
            )
    html_content += '''
        </div>
    '''

    
    # Add Conference tables
    html_content += '<div id="conference-table-container" style="display: none;">'
    for conference, table in conference_tables.items():
        html_content += generate_html_table(table, f"{conference} Conference", f"{conference.lower()}-conference", division_table=False)
    html_content += '''
        </div>
    '''

    # Close HTML content
    html_content += '''
        </div>
        </div>
        <div class="footer"></div>
    </body>
    </html>
    '''
    
    standings_filename = os.path.join(output_dir, "standings.html")
    with open(standings_filename, "w") as file:
        file.write(html_content)
    
    print(f"Standings page created at {standings_filename}")
    
def generate_html_table(data, title, table_id, division_table=False):
    logo_id_map = {
        "LAK": "LA",
        "SJS": "SJ",
        "TBL": "tb",
        "VEG": "VGK"
    }
    
    def get_logo_url(team_id):
        logo_id = logo_id_map.get(team_id, team_id)
        return f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/nhl/500/{logo_id}.png&h=40&w=40"
    
    if not division_table:
        table_html = f'<p class="title-caption">{title}</p>'
    else:
        table_html = ''

    table_html += f'<table id="{table_id}" class="standings-table">'
    
    if division_table:
        first_header = f'<th>{title}</th><th data-tip="Rank">Rk</th>'
    else:
        first_header = '<th>Team</th>'

    table_html += f'''
        <thead>
            <tr>
                {first_header}
                <th data-tip="Games Played">GP</th>
                <th data-tip="Wins">W</th>
                <th data-tip="Losses">L</th>
                <th data-tip="OT + SO Losses">OTL</th>
                <th data-tip="Points">Pts</th>
                <th data-tip="Points % (Pts / Max Pts)">Pts%</th>
                <th data-tip="Regulation Wins">RW</th>
                <th data-tip="Goals For">GF</th>
                <th data-tip="Goals Against">GA</th>
                <th data-tip="Goal Differential">Diff.</th>
                <th data-tip="Shots on Goal">SOG</th>
                <th data-tip="Shooting % (G / SOG)">S%</th>
                <th data-tip="Shots on Goal Against">SOGA</th>
                <th data-tip="Save % (GA / SOGA)">SV%</th>
                <th data-tip="Power Play Goals">PPG</th>
                <th data-tip="Power Play Opportunities">PPO</th>
                <th data-tip="Power Play % (PPG / PPO)">PP%</th>
                <th data-tip="Power Play Goals Against">PPGA</th>
                <th data-tip="Power Play Opportunities Against">PPOA</th>
                <th data-tip="Penalty Kill %">PK%</th>
                <th data-tip="Hits">HIT</th>
                <th data-tip="Blocks">BLK</th>
                <th data-tip="Penalty Minutes">PIM</th>
                <th data-tip="Hits Against">HITA</th>
                <th data-tip="Blocks Against">BLKA</th>
                <th data-tip="Penalty Minutes Drawn">PIMA</th>
                <th data-tip="Corsi For (SOG + Misses + Blocks)">CF</th>
                <th data-tip="Corsi Against (SOGA + Misses + Blocks)">CA</th>
                <th data-tip="Corsi For %">CF%</th>
                <th data-tip="Fenwick For (SOG + Misses)">FF</th>
                <th data-tip="Fenwick Against (SOGA + Misses)">FA</th>
                <th data-tip="Fenwick For %">FF%</th>
                <th data-tip="Faceoff Wins">FOW</th>
                <th data-tip="Faceoff Losses">FOL</th>
                <th data-tip="Faceoff %">FO%</th>
                <th style="min-width:22px; max-width:22px; visibility:hidden;"></th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for _, row in data.iterrows():
        team_id = row['TeamID']
        team_name = row['Team'].replace(" ", "&nbsp;")
        logo_url = get_logo_url(team_id)
        team_name_with_logo = f'<div class="team-cell"><div class="logo-container"><a href="/hockey/teams/{team_id}.html" target="_blank"><img src="{logo_url}" alt="{team_id}" class="team-logo"></a></div><div class="team-name-container"><a href="/hockey/teams/{team_id}.html" target="_blank">{team_name}</a></div></div>'
        gdiff = f"{row['GDiff']:+d}"
        rank = row['Rk']
        
        if division_table:
            rank_td = f'<td>{rank}</td>'
        else:
            rank_td = ''
        
        table_html += f'''
            <tr>
                <td class="team-name-cell">{team_name_with_logo}</td>
                {rank_td}
                <td>{row['GP']}</td>
                <td>{row['W']}</td>
                <td>{row['L']}</td>
                <td>{row['OTL']}</td>
                <td>{row['Points']}</td>
                <td>{row['PtsPct']:.1f}%</td>
                <td>{row['RW']}</td>
                <td>{row['GF']}</td>
                <td>{row['GA']}</td>
                <td>{gdiff}</td>
                <td>{row['SOG']}</td>
                <td>{row['SPct']:.1f}%</td>
                <td>{row['SOGA']}</td>
                <td>{row['SVPct']:.1f}%</td>
                <td>{row['PPG']}</td>
                <td>{row['PPO']}</td>
                <td>{row['PPpct']:.1f}%</td>
                <td>{row['PPGA']}</td>
                <td>{row['PPOA']}</td>
                <td>{row['PKpct']:.1f}%</td>
                <td>{row['HIT']}</td>
                <td>{row['BLK']}</td>
                <td>{row['PIM']}</td>
                <td>{row['HITA']}</td>
                <td>{row['BLKA']}</td>
                <td>{row['PIMA']}</td>
                <td>{row['CF']}</td>
                <td>{row['CA']}</td>
                <td>{row['CFpct']:.1f}%</td>
                <td>{row['FF']}</td>
                <td>{row['FA']}</td>
                <td>{row['FFpct']:.1f}%</td>
                <td>{row['FOW']}</td>
                <td>{row['FOL']}</td>
                <td>{row['FOpct']:.1f}%</td>
                <td style="min-width:22px; max-width:22px; visibility:hidden;"></td>
            </tr>
        '''
        
    table_html += '''
        </tbody>
    </table>
    '''
    return table_html

# Create leader directory
output_file_path = os.path.join(output_dir, "index.html")
create_leader_directory(leader_data, output_file_path)

# Create standings page
create_team_leader_directory(team_leaders_data, output_dir)