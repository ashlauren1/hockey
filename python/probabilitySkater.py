import pandas as pd

# File paths
metrics_file_path = r"C:\Users\ashle\Documents\Projects\hockey\skaters2022_25.csv"
upcoming_games_path = r"C:\Users\ashle\Documents\Projects\hockey\upcoming_games_skater.csv"
output_file_path = r"C:\Users\ashle\Documents\Projects\hockey\skaterprobability.csv"

# Load historical data and upcoming games data
metrics_data = pd.read_csv(
    metrics_file_path,
    dtype={
        'GameID': str,
        'PlayerID': str,
        'Team': str,
        'Is_Home': int,
        'Opp': str,
        'G': float,
        'A': float,
        'PTS': float,
        'SOG': float,
        'HIT': float,
        'BLK': float,
        'TOI': float
    },
    low_memory=False  # Reads file in one go, which can prevent type inference issues in large files
)

upcoming_games_data = pd.read_csv(
    upcoming_games_path,
    dtype={
        'GameID': str,
        'PlayerID': str,
        'Team': str,
        'Is_Home': int,
        'Opp': str
    },
    low_memory=False
)

# Define stat lines and weights
lines = {
    'G': [0.5, 1.5],
    'A': [0.5, 1.5, 2.5],
    'PTS': [0.5, 1.5, 2.5, 3.5],
    'SOG': [1.5, 2.5, 3.5, 4.5, 5.5],
    'BLK': [0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
    'HIT': [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
}
weights = {
    "opponent": 0.80,
    "home_away": 0.20
}

# Function to calculate the probability of going over a stat line
def calculate_probability(data, stat, line):
    return (data[stat] > line).mean()

# Function to calculate probabilities for a player for a specific upcoming game
def calculate_weighted_probabilities(player_data, lines, upcoming_game):
    results = []
    
    for stat, stat_lines in lines.items():
        for line in stat_lines:
            # Opponent-specific performance
            opp_data = player_data[player_data['Opp'] == upcoming_game['Opp']]
            opp_prob = calculate_probability(opp_data, stat, line) if not opp_data.empty else 0
            
            # Home/Away performance
            home_away_data = player_data[player_data['Is_Home'] == upcoming_game['Is_Home']]
            home_away_prob = calculate_probability(home_away_data, stat, line) if not home_away_data.empty else 0
            
            # Weighted probability
            weighted_prob = (
                weights["opponent"] * opp_prob +
                weights["home_away"] * home_away_prob
            )
            
            # Store result
            results.append(weighted_prob)
    
    return results

# Prepare final results list with columns
final_results = []
columns = ['GameID', 'Team', 'Is_Home', 'Opp', 'PlayerID'] + [f"{line}{stat}" for stat, stat_lines in lines.items() for line in stat_lines]

# Iterate over each upcoming game and calculate probabilities
for _, upcoming_game in upcoming_games_data.iterrows():
    player_id = upcoming_game['PlayerID']
    player_team = upcoming_game['Team']
    is_home = upcoming_game['Is_Home']
    opponent = upcoming_game['Opp']
    game_id = upcoming_game['GameID']
    
    # Filter historical data for the specific player
    player_data = metrics_data[metrics_data['PlayerID'] == player_id]
    
    if not player_data.empty:
        # Calculate probabilities for this player's upcoming game
        probabilities = calculate_weighted_probabilities(player_data, lines, upcoming_game)
        
        # Compile row of results
        result_row = [game_id, player_team, is_home, opponent, player_id] + probabilities
        final_results.append(result_row)

# Convert results to a DataFrame
probability_df = pd.DataFrame(final_results, columns=columns)

# Save to CSV
probability_df.to_csv(output_file_path, index=False)

print("Probabilities calculated and saved to:", output_file_path)
