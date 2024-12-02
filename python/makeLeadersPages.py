import pandas as pd
import os

# **File Paths**
data_dir = r"C:\Users\ashle\Documents\Projects\hockey\data"
output_dir = r"C:\Users\ashle\Documents\Projects\hockey\leaders"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

oldleaders_csv = os.path.join(data_dir, "oldLeaders.csv")
oldleader_data = pd.read_csv(oldleaders_csv)

leaders_csv = os.path.join(data_dir, "leaders.csv")
leader_data = pd.read_csv(leaders_csv)
leader_data.sort_values(by=["G", "PlayerID"], ascending=[False, True], inplace=True)

team_leaders_csv = os.path.join(data_dir, "leaderTeams.csv")
team_leaders_data = pd.read_csv(team_leaders_csv)

# **Part 1: Generate Player Directory (index.html)**
def create_season_pages(oldleader_data, output_dir):
    for season, season_data in oldleader_data.groupby('Season'):
        season_data = season_data.sort_values(by=["G", "A", "PTS"], ascending=[False, False, False])
        season_filename = os.path.join(output_dir, f"{season}_skaters.html")
    
        previous_season_map = {
            "2017-18": "2017-18",
            "2018-19": "2017-18",
            "2019-20": "2018-19",
            "2020-21": "2019-20",
            "2021-22": "2020-21",
            "2022-23": "2021-22",
            "2023-24": "2022-23"
        }
        
        next_season_map = {
            "2017-18": "2018-19",
            "2018-19": "2019-20",
            "2019-20": "2020-21",
            "2020-21": "2021-22",
            "2021-22": "2022-23",
            "2022-23": "2023-24",
            "2023-24": "2024-25"
        }
        
        def get_prev_season(season):
            prev_szn = previous_season_map.get(season, season)
            return f"{prev_szn}"
        def get_next_season(season):
            next_szn = next_season_map.get(season, season)
            return f"{next_szn}"
        
        prev_season = get_prev_season(season)
        next_season = get_next_season(season)

        html_content = f'''
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
    <title>NHL Season Leaders</title>
    <script src="leaders.js"></script>
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
    <div class="header">
	</div>
</div>

    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>

<main>
<div id="pageContainer">
<p class="title-caption">{season} Skater Stats</p>
    <div class="prevnext">
        <a href="/hockey/leaders/{prev_season}_skaters.html" class="button2 prev">Previous Season</a>
        <a href="/hockey/leaders/{next_season}_skaters.html" class="button2 next">Next Season</a>
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
                    <option value="c">Centers</option>
                    <option value="w">Wingers</option>
                    <option value="lw">Left Wing</option>
                    <option value="rw">Right Wing</option>
                </select>
            </form>
        </div>
        <div class="button-container">
            <button id="toggle-selection-btn">Show Selected Only</button>
            <button id="clear-filters-btn">Remove Filters</button>
            <button id="clear-all-btn">Clear All</button>
            <button id="glossaryButton">Glossary</button>
        </div>
    </div>

    <div id="tableContainer">
        <table id="seasonLeaders" class="seasonLeadersTable">
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
        '''

        for _, row in season_data.iterrows():
            team_id = row['Team']
            player_id = row['PlayerID']
            player_name = row['Player'].replace(" ", "&nbsp;")
            award_cell = row['Awards'].replace(" ", "&nbsp;") if not pd.isna(row['Awards']) else ""
            player_cell = f'<td><a href="/hockey/players/{player_id}.html" target="_blank">{player_name}</a></td>'
            team_cell = f'<td><a href="/hockey/teams/{team_id}.html" target="_blank">{team_id}</a></td>'
            plus_minus = f"{int(row['+/-']):+d}" if not pd.isna(row['+/-']) else ""
            faceoff_pct = f"{row['FO%']:.2f}%" if not pd.isna(row['FO%']) else ""
            shot_pct = f"{row['SPCT']:.2f}%" if not pd.isna(row['SPCT']) else ""
            
            html_content += f'''
                <tr>
                    {player_cell}
                    <td>{int(row['Age']) if not pd.isna(row['Age']) else ""}</td>
                    {team_cell}
                    <td>{row['Pos'] if not pd.isna(row['Pos']) else ""}</td>
                    <td>{int(row['GP']) if not pd.isna(row['GP']) else ""}</td>
                    <td>{int(row['G']) if not pd.isna(row['G']) else ""}</td>
                    <td>{int(row['A']) if not pd.isna(row['A']) else ""}</td>
                    <td>{int(row['PTS']) if not pd.isna(row['PTS']) else ""}</td>
                    <td>{plus_minus}</td>
                    <td>{int(row['PIM']) if not pd.isna(row['PIM']) else ""}</td>
                    <td>{int(row['EVG']) if not pd.isna(row['EVG']) else ""}</td>
                    <td>{int(row['PPG']) if not pd.isna(row['PPG']) else ""}</td>
                    <td>{int(row['SHG']) if not pd.isna(row['SHG']) else ""}</td>
                    <td>{int(row['GWG']) if not pd.isna(row['GWG']) else ""}</td>
                    <td>{int(row['EV']) if not pd.isna(row['EV']) else ""}</td>
                    <td>{int(row['PP']) if not pd.isna(row['PP']) else ""}</td>
                    <td>{int(row['SH']) if not pd.isna(row['SH']) else ""}</td>
                    <td>{int(row['SOG']) if not pd.isna(row['SOG']) else ""}</td>
                    <td>{shot_pct}</td>
                    <td>{int(row['TSA']) if not pd.isna(row['TSA']) else ""}</td>
                    <td>{row['TOI']:.2f}</td>
                    <td>{row['ATOI']:.2f}</td>
                    <td>{int(row['FOW']) if not pd.isna(row['FOW']) else ""}</td>
                    <td>{int(row['FOL']) if not pd.isna(row['FOL']) else ""}</td>
                    <td>{faceoff_pct}</td>
                    <td>{int(row['BLK']) if not pd.isna(row['BLK']) else ""}</td>
                    <td>{int(row['HIT']) if not pd.isna(row['HIT']) else ""}</td>
                    <td>{int(row['TAKE']) if not pd.isna(row['TAKE']) else ""}</td>
                    <td>{int(row['GIVE']) if not pd.isna(row['GIVE']) else ""}</td>
                    <td>{award_cell}</td>
                </tr>
            '''
        
        html_content += '''
        </tbody>
    </table>
</div>
</div>
</main>
<div class="footer"></div>
</body>
</html>
        '''
            
        with open(season_filename, 'w') as file:
            file.write(html_content)

    print("Season pages created successfully.")
    

def create_current_leader_directory(leader_data, output_dir):
    current_leader_filename = os.path.join(output_dir, "2024-25_skaters.html")
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
    <title>NHL Season Leaders</title>
<script>
document.addEventListener("DOMContentLoaded", function () {
	const seasonTable = document.getElementById("seasonLeaders");
	const headerRow = seasonTable.querySelector("thead tr:first-child");
    const rows = Array.from(seasonTable.querySelectorAll("tbody tr"));
    const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
    const clearAllButton = document.getElementById("clear-all-btn");
    const clearButton = document.getElementById("clear-filters-btn");
    let showSelectedOnly = false;
    let isDragging = false;
	
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

    function toggleRowSelection(row) {
        row.classList.toggle("selected-row");
    }

    toggleSelectionBtn.addEventListener("click", () => {
        showSelectedOnly = !showSelectedOnly;
        if (showSelectedOnly) {
            rows.forEach(row => {
                row.style.display = row.classList.contains("selected-row") ? "" : "none";
            });
            toggleSelectionBtn.textContent = "Show All Rows";
        } else {
            rows.forEach(row => (row.style.display = ""));
            toggleSelectionBtn.textContent = "Show Selected Only";
        }
    });
	
	addSortToHeaders(seasonTable);
	
	function addSortToHeaders(seasonTable) {
		const headers = seasonTable.querySelectorAll("thead th");
		headers.forEach((header, index) => {
			header.style.cursor = "pointer";
			header.addEventListener("click", function () {
				sortTable(seasonTable, index);
			});
		});
	}
	
	function sortTable(seasonTable, columnIndex) {
		const rows = Array.from(seasonTable.querySelectorAll("tbody tr"));
		
		// TESTING DEFAULT DESC SORT DIRECTION
		let asc = false;
		const direction = seasonTable.dataset.sortDirection === "desc" ? "asc" : "desc";
		
		seasonTable.dataset.sortDirection = direction;

		rows.sort((a, b) => {
			let cellA = a.cells[columnIndex].textContent.trim();
			let cellB = b.cells[columnIndex].textContent.trim();

			let valA, valB;
			
			const isPercentage = cellA.includes('%') && cellB.includes('%');
			if (isPercentage) {
				valA = parseFloat(cellA.replace('%', ''));
				valB = parseFloat(cellB.replace('%', ''));
			} else if (!isNaN(cellA) && !isNaN(cellB)) {
				valA = parseFloat(cellA);
				valB = parseFloat(cellB);
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

		const tbody = seasonTable.querySelector("tbody");
		rows.forEach(row => tbody.appendChild(row));
	}
	
	const teamSelect = document.getElementById("teams");
    const positionSelect = document.getElementById("pos");
    const positionGroups = {
        f: ["lw", "rw", "w", "c", "f"],
        w: ["lw", "rw", "w"],
        c: ["c"],
        lw: ["lw"],
        rw: ["rw"],
        d: ["d"],
    };
    
    teamSelect.addEventListener("change", filterTable);
    positionSelect.addEventListener("change", filterTable);

    function filterTable() {
        const teamFilter = teamSelect.value.trim().toLowerCase();
        const positionFilter = positionSelect.value.trim().toLowerCase();
        const positionGroup = positionGroups[positionFilter] || []; 
        
        rows.forEach(row => {
            const cells = row.cells;
            const teamCell = cells[1]?.textContent.trim().toLowerCase();
            const positionCell = cells[2]?.textContent.trim().toLowerCase();
            
            const matchesTeam = !teamFilter || teamCell === teamFilter;
            const matchesPosition =
                !positionFilter || positionGroup.includes(positionCell);
			const isFiltered = (!positionSelect.value === "") || (!teamSelect.value === "");
			
			!showSelectedOnly ? (row.style.display = matchesTeam && matchesPosition ? "" : "none") : (row.style.display = row.classList.contains("selected-row") && matchesTeam && matchesPosition ? "" : "none")
        });
    }
	
	clearButton.addEventListener("click", () => {
		document.querySelectorAll("select").forEach(select => select.value = "");
		filterTable();
		if (showSelectedOnly) {
            rows.forEach(row => {
                row.style.display = row.classList.contains("selected-row") ? "" : "none";
            });
            toggleSelectionBtn.textContent = "Show All Rows";
        } else {
            rows.forEach(row => (row.style.display = ""));
            toggleSelectionBtn.textContent = "Show Selected Only";
        }
	});

    clearAllButton.addEventListener("click", () => {
        document.querySelectorAll("select").forEach(select => select.value = "");

        rows.forEach(row => {
            row.classList.remove("selected-row");
            row.style.display = "";
        });
        toggleSelectionBtn.textContent = "Show Selected Only";
        showSelectedOnly = false;
        
        filterTable();
    });
});
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
    <div class="header">
	</div>
</div>
<button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>
<main>
<div id="pageContainer">
<p class="title-caption">2024-25 Skater Stats</p>
    <div class="prevnext">
        <a href="/hockey/leaders/2023-24_skaters.html" class="button2 prev">Previous Season</a>
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
                    <option value="c">Centers</option>
                    <option value="w">Wingers</option>
                    <option value="lw">Left Wing</option>
                    <option value="rw">Right Wing</option>
                </select>
            </form>
        </div>
        <div class="button-container">
            <button id="toggle-selection-btn">Show Selected Only</button>
            <button id="clear-filters-btn">Remove Filters</button>
            <button id="clear-all-btn">Clear All</button>
            <button id="glossaryButton">Glossary</button>
        </div>
    </div>
    
    <div id="tableContainer">
        <table id="seasonLeaders" class="seasonLeadersTable">
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
        player_name = row['Player'].replace(" ", "&nbsp;")
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

    with open(current_leader_filename, "w") as file:
        file.write(html_content)

    print(f"Current leader pages created successfully")

def create_leader_directory(leader_data, output_file_path):
    int_columns = ["G", "A", "PTS", "SOG", "HIT", "BLK", "PIM", "EVG", "PPG", "SHG", "EVA", "PPA", "SHA"]
    decimal_columns = [col for col in leader_data.columns if col not in int_columns + ["Player", "PlayerID", "TeamID", "Position"]]

    leader_data[int_columns] = leader_data[int_columns].fillna(0).astype(int)
    leader_data[decimal_columns] = leader_data[decimal_columns].round(2)
    
    stat_columns = {
        "G": "Goals",
        "A": "Assists",
        "PTS": "Points",
        "SOG": "Shots on Goal",
        "S%": "Shooting Percentage",
        "HIT": "Hits",
        "BLK": "Blocks",
        "TOI": "Time on Ice",
        "PIM": "Penalty Minutes",
        "EVG": "Even Strength Goals",
        "PPG": "Power Play Goals",
        "SHG": "Short-Handed Goals",
        "EVA": "Even Strength Assists",
        "PPA": "Power Play Assists",
        "SHA": "Short-Handed Assists",
        "G_GP": "Goals per Game",
        "A_GP": "Assists per Game",
        "PTS_GP": "Points per Game",
        "SOG_GP": "Shots on Goal per Game",
        "HIT_GP": "Hits per Game",
        "BLK_GP": "Blocks per Game",
        "TOI_GP": "Time on Ice per Game"
    }

    leaders = {}
    
    for key, display_name in stat_columns.items():
        if key in leader_data.columns:
            if key == "S%":
                filtered_data = leader_data[leader_data["SOG"] >= 30]
                if not filtered_data.empty:
                    max_value = filtered_data[key].max()
                    tied_leaders = filtered_data[filtered_data[key] == max_value]
                else:
                    continue
            else:
                max_value = leader_data[key].max()
                tied_leaders = leader_data[leader_data[key] == max_value]
            
            leaders[key] = [
                {
                    "player": row["Player"],
                    "player_id": row["PlayerID"],
                    "value": int(row[key]) if key in int_columns else round(row[key], 2)
                }
                for _, row in tied_leaders.iterrows()
            ]

    html_content = f"""
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
    <title>Leaders Directory</title>
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
    <div class="header">
        <h1>NHL Leaders</h1>
    </div>
</div>

    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>

<main>
<div id="pageContainer">
    <div id="seasons_list_container">
        <p class="title-caption">Leaders by Season:</p>
		<ul class="seasons_list">
            <li><a href="/hockey/leaders/2024-25_skaters.html">2024-25</a></li>
			<li><a href="/hockey/leaders/2023-24_skaters.html">2023-24</a></li>
            <li><a href="/hockey/leaders/2022-23_skaters.html">2022-23</a></li>
            <li><a href="/hockey/leaders/2021-22_skaters.html">2021-22</a></li>
            <li><a href="/hockey/leaders/2020-21_skaters.html">2020-21</a></li>
            <li><a href="/hockey/leaders/2019-20_skaters.html">2019-20</a></li>
            <li><a href="/hockey/leaders/2018-19_skaters.html">2018-19</a></li>
            <li><a href="/hockey/leaders/2017-18_skaters.html">2017-18</a></li>
		</ul>
	</div>
    <p class="title-caption">Current Leaders:</p>
    <div class="tabular">
    """
    
    for key, display_name in stat_columns.items():
        if key in leaders:
            leader_entries = ""
            is_tie = len(leaders[key]) > 1  # Check if there's a tie
            display_name_with_tie = f"{display_name} (Tie)" if is_tie else display_name
            leader_entries += f'<div class="groupedTabular">'
            
            for i, player in enumerate(leaders[key]):
                if i == 0:
                    leader_entries += f"""
        <div class="tabular_row">
            <div><strong>{display_name_with_tie}</strong></div>
            <div><a href="/hockey/players/{player['player_id']}.html">{player['player']}</a> ({player['value']})</div>
        </div>
                    """
                else:
                    leader_entries += f"""
        <div class="tabular_row">
            <div></div>
            <div><a href="/hockey/players/{player['player_id']}.html">{player['player']}</a> ({player['value']})</div>
        </div>
                    """
            leader_entries += f'</div>'

            html_content += leader_entries

    html_content += """
    </div>
</div>
</main>
<div class="footer"></div>
</body>
</html>
    """

    # Write the HTML content to a file
    with open(output_file_path, "w") as file:
        file.write(html_content)

    print(f"Leaders index created at {output_file_path}")


def create_standings_page(team_leaders_data, output_dir):
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
    <title>2024-25 Standings</title>

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

        buttons[view].classList.add("active-button");
    }}

    document.getElementById("btn-league").addEventListener("click", () => showTable("league"));
    document.getElementById("btn-conference").addEventListener("click", () => showTable("conference"));
    document.getElementById("btn-division").addEventListener("click", () => showTable("division"));
}});
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
    <div class="header">
        <h1>2024-25 Standings</h1>
    </div>
</div>
    
    <button class="arrowUp" onclick="window.scrollTo({{top: 0}})">Top</button>

<main>

<div id="pageContainer">
    <div class="standings-button-container">
        <button id="btn-league">League</button>
        <button id="btn-conference">Conference</button>
        <button id="btn-division">Division</button>
    </div>
    <button id="tiebreakerInfoButton">Tiebreakers</button>
    <button id="glossaryButton">Glossary</button>
    
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
                <li>OTL:&nbsp;&nbsp;Overtime and Shootout Losses</li>
                <li>Points %:&nbsp;&nbsp;Points / Possible Points</li>
                <li>RW:&nbsp;&nbsp;Regulation Wins</li>
                <li>ROW:&nbsp;&nbsp;Regulation and Overtime Wins (Excluding Shootouts)</li>
                <li>GF:&nbsp;&nbsp;Goals For</li>
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
    <div id="tableContainer">
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
</main>
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
                <th data-tip="Regulation and Overtime Wins (Excluding Shootouts)">ROW</th>
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
                <th data-tip="Penalty Minutes">PIM</th>
                <th data-tip="Penalty Minutes Drawn">PIMA</th>
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
                <td>{row['PtsPct']:.2f}</td>
                <td>{row['RW']}</td>
                <td>{row['ROW']}</td>
                <td>{row['GF']}</td>
                <td>{row['GA']}</td>
                <td>{gdiff}</td>
                <td>{row['SOG']}</td>
                <td>{row['SPct']:.2f}</td>
                <td>{row['SOGA']}</td>
                <td>{row['SVPct']:.2f}</td>
                <td>{row['PPG']}</td>
                <td>{row['PPO']}</td>
                <td>{row['PPpct']:.2f}</td>
                <td>{row['PPGA']}</td>
                <td>{row['PPOA']}</td>
                <td>{row['PKpct']:.2f}</td>
                <td>{row['PIM']}</td>
                <td>{row['PIMA']}</td>
            </tr>
        '''
        
    table_html += '''
        </tbody>
    </table>
    '''
    return table_html

output_file_path = os.path.join(output_dir, "index.html")
create_leader_directory(leader_data, output_file_path)

create_season_pages(oldleader_data, output_dir)
create_current_leader_directory(leader_data, output_dir)
create_standings_page(team_leaders_data, output_dir)
