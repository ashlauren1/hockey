import pandas as pd

# File paths
roster_csv = r"C:\Users\ashle\Documents\Projects\hockey\data\rosters.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\hockey\players\index.html"

# Load and sort data by team
roster_data = pd.read_csv(roster_csv)
roster_data.sort_values(by=["Team", "Player"], inplace=True)

# Start the HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Player Directory</title>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
    
<script>
document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("player-index");
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
    <h1>Player Directory</h1>
    </div>
    <div><button class="arrowUp"><a href="#page-title">Top</a></button></div>
    <div id="index-container">
    <table id="player-index">
    <thead>
        <tr>
            <th>Player</th>
            <th>Team</th>
            <th>Position</th>
        </tr>
    </thead>
    <tbody>
"""

# Generate table rows grouped by team
for _, row in roster_data.iterrows():
    team_id = row["TeamID"]
    team_name = row["Team"]
    player_id = row["PlayerID"]
    player_name = row["Player"]
    position = row["Position"]

    # Add player row
    html_content += f"""
        <tr>
            <td style="text-align:left"><a href="/hockey/players/{player_id}.html">{player_name}</a></td>
            <td style="text-align:center"><a href="/hockey/teams/{team_id}.html">{team_id}</a></td>
            <td style="text-align:center">{position}</td>
        </tr>
    """

# Close the single <tbody>, table, and HTML tags
html_content += """
    </tbody>
    </table>
    <div class="footer"></div>
</body>
</html>
"""

# Write the HTML content to a file
with open(output_file_path, "w") as file:
    file.write(html_content)

print(f"Player directory created at {output_file_path}")
