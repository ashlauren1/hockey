import pandas as pd

# File paths
team_csv = r"C:\Users\ashle\Documents\Projects\hockey\data\teamgamelogs.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\hockey\teams\index.html"

# Load data and keep only unique teams
team_data = pd.read_csv(team_csv)
unique_teams = team_data.drop_duplicates(subset=["Team", "TeamID"]).sort_values(by="Team")

# Start the HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Directory</title>
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="icon" type="image/x-icon" href="/hockey/images/favicon.ico">
</head>
<body>
 <div class="topnav">
        <a href="/hockey/">Projections</a>
        <a href="/hockey/players/">Players</a>
        <a href="/hockey/games/">Scores</a>
        <a href="/hockey/teams/">Teams</a>
    </div>    
    <div id="page-title" class="header">
    <h1>Team Directory</h1>
    </div>
    <div><button class="arrowUp"><a href="#page-title">Top</a></button></div>
    <div id="index-container">
    <table id="team-index">
        <thead>
            <tr>
                <th>Team</th>
            </tr>
        </thead>
        <tbody>
"""

# Populate the table with each unique team and link
for _, row in unique_teams.iterrows():
    team_name = row["Team"]
    team_id = row["TeamID"]

    html_content += f"""
        <tr>
            <td style="text-align:left"><a href="/hockey/teams/{team_id}.html">{team_name}</a></td>
        </tr>
    """

# Close the table and HTML tags
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

print(f"Team directory created at {output_file_path}")
