import pandas as pd

# Paths to the files
upcoming_games_path = r'C:\Users\ashle\Documents\Projects\ashlauren1.github.io\playervsteamupcominggames.csv'
probability_path = r'C:\Users\ashle\Documents\Projects\ashlauren1.github.io\playervsteamprobability.csv'

# Read the CSV files into pandas DataFrames
upcoming_games_df = pd.read_csv(upcoming_games_path)
probability_df = pd.read_csv(probability_path)

# Iterate over each row of upcoming_games_df
for index, game_row in upcoming_games_df.iterrows():
    player_id = game_row['PlayerID']
    opp = game_row['Opp']
    
    # Filter the probability_df based on PlayerID and Opp
    relevant_probs = probability_df[(probability_df['PlayerID'] == player_id) & (probability_df['Opp'] == opp)]
    
    # Iterate over the columns in upcoming_games_df that match with the 'Line' values from probability_df
    for column in upcoming_games_df.columns[5:]:  # Skip first 5 columns (Game ID, Location, etc.)
        if column in relevant_probs['Line'].values:
            # Get the probability from probability_df
            probability_value = relevant_probs[relevant_probs['Line'] == column]['P'].values
            if len(probability_value) > 0:
                # Update the upcoming_games_df with the probability value
                upcoming_games_df.at[index, column] = probability_value[0]

# Save the updated upcoming_games_df back to a CSV file
updated_csv_path = r'C:\Users\ashle\Documents\Projects\ashlauren1.github.io\updated_playervsteamupcominggames.csv'
upcoming_games_df.to_csv(updated_csv_path, index=False)

print(f"Updated file saved to: {updated_csv_path}")
