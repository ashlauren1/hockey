import json
import pandas as pd

# Load the JSON data from the specified path
file_path = r"C:\Users\ashle\Documents\Projects\hockey\response_1731203674231.json"
with open(file_path, 'r') as file:
    data = json.load(file)

# Extract details into a list of rows
lines_data = []
for item in data:
    line_id = item.get('line_id')
    game_id = item.get('game_id')
    market = item.get('market')
    line = item.get('line')
    league = item.get('league')
    sportsbook = item.get('sportsbook')
    game_date = item.get('game_date')
    start_time = item.get('start_time')
    grade = item.get('grade')
    
    # For each player in the "players" list, create a row
    for player in item.get('players', []):
        player_name = player.get('name', 'N/A')
        normalized_name = player.get('normalized_name', 'N/A')
        player_team = player.get('team', 'N/A')
        
        # For each line change, capture all changes
        for change in item.get('line_changes', []):
            change_value = change.get('value', 'N/A')
            change_timestamp = change.get('timestamp', 'N/A')

            # Append each change and player combination to lines_data
            lines_data.append({
                'Line ID': line_id,
                'Game ID': game_id,
                'Player Name': player_name,
                'Normalized Name': normalized_name,
                'Team': player_team,
                'Market': market,
                'Line': line,
                'League': league,
                'Sportsbook': sportsbook,
                'Game Date': game_date,
                'Start Time': start_time,
                'Grade': grade,
                'Line Change Value': change_value,
                'Line Change Timestamp': change_timestamp
            })

# Convert to DataFrame and save to CSV
csv_path = r"C:\Users\ashle\Documents\Projects\hockey\hockey_lines_converted.csv"
df = pd.DataFrame(lines_data)
df.to_csv(csv_path, index=False)
print(f"Data successfully saved to '{csv_path}'")
