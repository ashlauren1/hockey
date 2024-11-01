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
</head>
<body>
    <h1 style="text-align: center;">Team Directory</h1>
    <table id="player-table">
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
            <td><a href="/hockey/teams/{team_id}.html">{team_name}</a></td>
        </tr>
    """

# Close the table and HTML tags
html_content += """
        </tbody>
    </table>
</body>
</html>
"""

# Write the HTML content to a file
with open(output_file_path, "w") as file:
    file.write(html_content)

print(f"Team directory created at {output_file_path}")
