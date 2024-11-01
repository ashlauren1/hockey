import pandas as pd

# File paths
team_game_log_csv = r"C:\Users\ashle\Documents\Projects\hockey\data\gamelogs.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\hockey\games\index.html"

# Load data and filter for unique GameID rows
team_game_data = pd.read_csv(team_game_log_csv)
unique_games = team_game_data.drop_duplicates(subset=["GameID"]).sort_values(by=["Season", "Date"])

# Start the HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Directory</title>
    <link rel="stylesheet" href="stylesheet.css">
</head>
<body>
    <h1 style="text-align: center;">Game Directory</h1>
    <table id="player-table">
        <thead>
            <tr>
                <th>Season</th>
                <th>Game</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
"""

# Populate the table with each unique game
for _, row in unique_games.iterrows():
    season = row["Season"]
    game_id = row["GameID"]
    game_name = row["Game"]
    game_date = row["Date"]

    html_content += f"""
        <tr>
            <td>{season}</td>
            <td><a href="/hockey/games/{game_id}.html">{game_name}</a></td>
            <td>{game_date}</td>
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

print(f"Game directory created at {output_file_path}")
