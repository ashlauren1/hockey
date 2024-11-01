import pandas as pd

# File paths
team_game_log_csv = r"C:\Users\ashle\Documents\Projects\hockey\data\gameindex.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\hockey\games\index.html"

# Load data and filter for unique GameID rows
team_game_data = pd.read_csv(team_game_log_csv)

# Start the HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Boxscore Directory</title>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    
<script>
document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("game-index");
    const headerRow = table.querySelector("thead tr:first-child");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    // Add sorting to each header
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

    // Sort the table by column
    function sortTable(table, columnIndex) {
        const rows = Array.from(table.querySelectorAll("tbody tr"));
        const isNumeric = rows.every(row => !isNaN(row.cells[columnIndex].textContent.trim()));
        const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
        table.dataset.sortDirection = direction;

        rows.sort((a, b) => {
            const cellA = a.cells[columnIndex].textContent.trim();
            const cellB = b.cells[columnIndex].textContent.trim();

            const valA = isNumeric ? parseFloat(cellA) : cellA.toLowerCase();
            const valB = isNumeric ? parseFloat(cellB) : cellB.toLowerCase();

            return direction === "asc" ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
        });

        rows.forEach(row => table.querySelector("tbody").appendChild(row));
    }
});
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
    <div><button class="arrowUp"><a href="#page-title">Top</a></button></div>
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
