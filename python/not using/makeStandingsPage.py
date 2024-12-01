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
                <td>{row['PtsPct']:.2f}%</td>
                <td>{row['RW']}</td>
                <td>{row['ROW']}</td>
                <td>{row['GF']}</td>
                <td>{row['GA']}</td>
                <td>{gdiff}</td>
                <td>{row['SOG']}</td>
                <td>{row['SPct']:.2f}%</td>
                <td>{row['SOGA']}</td>
                <td>{row['SVPct']:.2f}%</td>
                <td>{row['PPG']}</td>
                <td>{row['PPO']}</td>
                <td>{row['PPpct']:.2f}%</td>
                <td>{row['PPGA']}</td>
                <td>{row['PPOA']}</td>
                <td>{row['PKpct']:.2f}%</td>
                <td>{row['PIM']}</td>
                <td>{row['PIMA']}</td>
            </tr>
        '''
        
    table_html += '''
        </tbody>
    </table>
    '''
    return table_html

# Create standings page
create_team_leader_directory(team_leaders_data, output_dir)