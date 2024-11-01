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
</head>
<body>
    <h1 style="text-align: center;">Player Directory</h1>
    <table id="player-table">
"""

# Generate table rows grouped by team
current_team = None
for _, row in roster_data.iterrows():
    team = row["Team"]
    player_id = row["PlayerID"]
    player_name = row["Player"]
    position = row["Position"]

    # Add a new team header if the team changes
    if team != current_team:
        html_content += f"""
        <tr class="team-header">
            <th colspan="3"><a href="/hockey/teams/{team}.html">{team}</a></th>
        </tr>
        <tr>
            <th>Player</th>
            <th>Team</th>
            <th>Position</th>
        </tr>
        """
        current_team = team

    # Add player row
    html_content += f"""
        <tr class="player-row">
            <td><a href="/hockey/players/{player_id}.html">{player_name}</a></td>
            <td><a href="/hockey/teams/{team}.html">{team}</a></td>
            <td>{position}</td>
        </tr>
    """

# Close the table and HTML tags
html_content += """
    </table>
</body>
</html>
"""

# Write the HTML content to a file
with open(output_file_path, "w") as file:
    file.write(html_content)

print(f"Player directory created at {output_file_path}")
