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
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    <script src="modalsMobileNavAndSearch.js"></script>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="stylesheet" href="commonStylesheet.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Roboto+Slab:wght@100..900&display=swap" rel="stylesheet">
    <title>2024-25 Leaders</title>
<script>
document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("leader-index");
    const rows = Array.from(table.querySelectorAll("tbody tr"));
	const clearButton = document.getElementById("leaders-clear-filters-btn");
	
	const teamSelect = document.getElementById("teams");
    const positionSelect = document.getElementById("pos");

    teamSelect.addEventListener("change", filterTable);
    positionSelect.addEventListener("change", filterTable);

    function filterTable() {
        const teamFilter = teamSelect.value;
        const positionFilter = positionSelect.value;

        rows.forEach(row => {
            const cells = row.cells;

            const matchesTeam = !teamFilter || cells[1].textContent.trim().toLowerCase() === teamFilter;
            const matchesPosition = !positionFilter || cells[2].textContent.trim().toLowerCase() === positionFilter;

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
    
	clearButton.addEventListener("click", () => {
		document.querySelectorAll("select").forEach(select => select.value = "");
		filterTable();
	});
});
    const teamSelect = document.getElementById("teams");
    const positionSelect = document.getElementById("pos");
</script>
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
    <div class="header">2024-25 Leaders</div>
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
            <button id="glossaryButton">Glossary</button>
        </div>
    </div>
    
<div id="tableContainer">
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
            </tr>
        """

    # Close the single <tbody>, table, and HTML tags
    html_content += """
        </tbody>
    </table>
</div>
</div>
<div class="footer"></div>
</body>
</html>
    """

    # Write the HTML content to a file
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Leaders directory created at {output_file_path}")

# Create leader directory
output_file_path = os.path.join(output_dir, "index.html")
create_leader_directory(leader_data, output_file_path)
