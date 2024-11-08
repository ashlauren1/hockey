import pandas as pd
from bs4 import BeautifulSoup
import os

# Paths to CSV files and directory containing HTML files
lines_path = r'C:\Users\ashle\Documents\Projects\hockey\data\todayLines.csv'
gamelogs_path = r'C:\Users\ashle\Documents\Projects\hockey\data\gamelogs.csv'
html_dir = r"C:\Users\ashle\Documents\Projects\hockey\h2h"

# Load the data
lines_df = pd.read_csv(lines_path)
gamelogs_df = pd.read_csv(gamelogs_path)

# Chart.js template for bar chart with betting line overlay and filter controls
chart_script_template = """
<div class="chart-container">
    <canvas id="{stat}_{game_id}_chart" class="barChart"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@1.1.0"></script>

    <!-- Filter Controls -->
    <div class="barChart-filters">
        <label for="{stat}_{game_id}_teamFilter">Opponent:</label>
        <select id="{stat}_{game_id}_teamFilter" onchange="applyFilters_{stat}_{game_id}()">
            <option value="all">All</option>
            {team_options}
        </select>

        <label for="{stat}_{game_id}_homeAwayFilter">Home/Away:</label>
        <select id="{stat}_{game_id}_homeAwayFilter" onchange="applyFilters_{stat}_{game_id}()">
            <option value="all">All</option>
            <option value="home">Home</option>
            <option value="away">Away</option>
        </select>

        <label for="{stat}_{game_id}_startDate">Start Date:</label>
        <input type="date" id="{stat}_{game_id}_startDate" onchange="applyFilters_{stat}_{game_id}()">

        <label for="{stat}_{game_id}_endDate">End Date:</label>
        <input type="date" id="{stat}_{game_id}_endDate" onchange="applyFilters_{stat}_{game_id}()">
    </div>

    <script>
    const allData_{stat}_{game_id} = {chart_data};  // Full data for player
    const Line_{stat}_{game_id} = {betting_line};  // Betting line for this stat
    let chart_{stat}_{game_id};

    function initChart_{stat}_{game_id}() {{
        const ctx = document.getElementById('{stat}_{game_id}_chart').getContext('2d');
        const barBackgroundColor = getComputedStyle(ctx.canvas).getPropertyValue('--bar-background-color').trim();
        const barBorderColor = getComputedStyle(ctx.canvas).getPropertyValue('--bar-border-color').trim();

        chart_{stat}_{game_id} = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: allData_{stat}_{game_id}.map(d => `${{d.date}} ${{d.location === 'home' ? 'vs' : '@'}} ${{d.opponent}}`),
                datasets: [{{
                    label: '{stat}',
                    data: allData_{stat}_{game_id}.map(d => d.stat),
                    backgroundColor: barBackgroundColor,
                    borderColor: barBorderColor,
                    borderWidth: 1
                }}]
            }},
            options: {{
                scales: {{
                    y: {{ 
                        beginAtZero: true, 
                        ticks: {{
                            color: '#222831',  // Color for y-axis labels
                            font: {{ size: 11 }}  // Font size for y-axis labels
                        }},
                        grid: {{
                            display: false
                        }},
                        stepSize: 0.5
                    }},
                    x: {{
                        ticks: {{
                            color: '#222831',  // Color for x-axis labels
                            font: {{ size: 11 }}  // Font size for x-axis labels
                        }},
                        grid: {{
                            display: false
                        }}
                    }}
                }},
                plugins: {{
                    annotation: {{
                        annotations: {{
                            line1: {{
                                type: 'line',
                                yMin: Line_{stat}_{game_id},
                                yMax: Line_{stat}_{game_id},
                                borderColor: '#73b089',
                                borderWidth: 2,
                                label: {{ content: '', enabled: true, position: 'end' }}
                            }}
                        }}
                    }}
                }}
            }}
        }});
    }}

    function applyFilters_{stat}_{game_id}() {{
        const teamFilter = document.getElementById('{stat}_{game_id}_teamFilter').value;
        const homeAwayFilter = document.getElementById('{stat}_{game_id}_homeAwayFilter').value;
        const startDate = document.getElementById('{stat}_{game_id}_startDate').value;
        const endDate = document.getElementById('{stat}_{game_id}_endDate').value;

        const filteredData = allData_{stat}_{game_id}.filter(d => {{
            const isTeamMatch = (teamFilter === 'all') || (d.opponent === teamFilter);
            const isLocationMatch = (homeAwayFilter === 'all') || 
                                    (homeAwayFilter === 'home' && d.location === 'home') || 
                                    (homeAwayFilter === 'away' && d.location === 'away');
            const isDateInRange = (!startDate || new Date(d.date) >= new Date(startDate)) &&
                                  (!endDate || new Date(d.date) <= new Date(endDate));

            return isTeamMatch && isLocationMatch && isDateInRange;
        }});

        chart_{stat}_{game_id}.data.labels = filteredData.map(d => `${{d.date}} ${{d.location === 'home' ? 'vs' : '@'}} ${{d.opponent}}`);
        chart_{stat}_{game_id}.data.datasets[0].data = filteredData.map(d => d.stat);
        chart_{stat}_{game_id}.update();
    }}

    // Initialize the chart immediately
    initChart_{stat}_{game_id}();
    </script>
</div>
"""

# Rest of the script remains the same...


# Process each HTML file
for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(html_dir, filename)
        
        # Extract player ID from filename
        player_id = filename.split("_")[0]
        
        # Read and parse HTML file
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        
        # Filter gamelogs for the player
        player_gamelogs = gamelogs_df[gamelogs_df['PlayerID'] == player_id]
        
        # Check if we have any games for this player
        if player_gamelogs.empty:
            print(f"No gamelog data found for player {player_id} in {filename}")
            continue
        
        # Get unique stats for this player in the betting lines
        player_lines = lines_df[lines_df['PlayerID'] == player_id]
        
        # Add chart for each stat in the player's betting lines
        for _, line_row in player_lines.iterrows():
            game_id = line_row['GameID']
            stat = line_row['Stat']
            betting_line = line_row['Line']
            
            # Filter past game data for this stat
            stat_data = player_gamelogs[['Date', 'Opp', 'Is_Home', stat]].dropna()
            
            # Format x-axis labels and values for JavaScript
            chart_data = [
                {"date": row["Date"], "opponent": row["Opp"], "location": "home" if row["Is_Home"] == 1 else "away", "stat": row[stat]}
                for _, row in stat_data.iterrows()
            ]
            
            # Generate unique team options for the dropdown
            unique_teams = stat_data['Opp'].unique()
            team_options = "\n".join([f'<option value="{team}">{team}</option>' for team in unique_teams])
            
            # Generate the chart script
            chart_script = chart_script_template.format(
                stat=stat,
                game_id=game_id,
                chart_data=chart_data,
                betting_line=betting_line,
                team_options=team_options
            )
            
            # Append the chart script to the HTML body
            soup.body.append(BeautifulSoup(chart_script, "html.parser"))

        # Save modified HTML file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

print("All files have been processed.")
