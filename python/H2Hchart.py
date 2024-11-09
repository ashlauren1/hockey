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
    <!-- Filter Controls -->
    <div class="barChart-filters">
        <div class="barChartFilter">
        <label for="{stat}_{game_id}_{betting_line_id}_teamFilter">Opponent:</label>
        <select id="{stat}_{game_id}_{betting_line_id}_teamFilter" onchange="applyFilters_{stat}_{game_id}_{betting_line_id}()">
            <option value="all">All</option>
            {team_options}
        </select>
        </div>
        
        <div class="barChartFilter">
        <label for="{stat}_{game_id}_{betting_line_id}_homeAwayFilter">Home/Away:</label>
        <select id="{stat}_{game_id}_{betting_line_id}_homeAwayFilter" onchange="applyFilters_{stat}_{game_id}_{betting_line_id}()">
            <option value="all">All</option>
            <option value="home">Home</option>
            <option value="away">Away</option>
        </select>
        </div>
        
        <div class="barChartFilter">
        <label for="{stat}_{game_id}_{betting_line_id}_startDate">Start Date:</label>
        <input type="date" id="{stat}_{game_id}_{betting_line_id}_startDate" onchange="applyFilters_{stat}_{game_id}_{betting_line_id}()">
        </div>
        
        <div class="barChartFilter">
        <label for="{stat}_{game_id}_{betting_line_id}_endDate">End Date:</label>
        <input type="date" id="{stat}_{game_id}_{betting_line_id}_endDate" onchange="applyFilters_{stat}_{game_id}_{betting_line_id}()">
        </div>
    </div>
    
    <canvas id="{stat}_{game_id}_{betting_line_id}_chart" class="barChart"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@1.1.0"></script>
    
    <div class="slider-container">
    <div class="line-slider">
        <label for="{stat}_{game_id}_{betting_line_id}_lineSlider">Change Line:</label>
        <input type="range" id="{stat}_{game_id}_{betting_line_id}_lineSlider" min="0" max="30" step="0.5" value="{betting_line}" oninput="updateLine_{stat}_{game_id}_{betting_line_id}(this.value)" class="line-slider">
        <span id="{stat}_{game_id}_{betting_line_id}_lineValue">{betting_line}</span>
    </div>
    <div class="chartButtons">
    <button id="reset-line-btn-{stat}_{game_id}_{betting_line_id}" onclick="resetLine_{stat}_{game_id}_{betting_line_id}_lineSlider()" class="reset-line-btn">Reset Line</button>
    <button id="clear-filters-btn-{stat}_{game_id}_{betting_line_id}" onclick="clearFilters_{stat}_{game_id}_{betting_line_id}()" class="clear-chart-filters">Clear Filters</button>
    </div>
    </div>
</div>
    

    <script>
    const allData_{stat}_{game_id}_{betting_line_id} = {chart_data};  // Full data for player
    let Line_{stat}_{game_id}_{betting_line_id} = {betting_line};  // Default betting line
    let chart_{stat}_{game_id}_{betting_line_id};

    function initChart_{stat}_{game_id}_{betting_line_id}() {{
        const ctx = document.getElementById('{stat}_{game_id}_{betting_line_id}_chart').getContext('2d');
        
        chart_{stat}_{game_id}_{betting_line_id} = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: allData_{stat}_{game_id}_{betting_line_id}.map(d => `${{d.date}} ${{d.location === 'home' ? 'vs' : '@'}} ${{d.opponent}}`),
                datasets: [{{
                    label: '{stat}',  // Label used in title only
                    data: allData_{stat}_{game_id}_{betting_line_id}.map(d => d.stat || 0.02),  // Use 0.02 for display purposes if stat is 0
                    backgroundColor: allData_{stat}_{game_id}_{betting_line_id}.map(d => d.stat === 0 ? '#c01616' : (d.stat >= Line_{stat}_{game_id}_{betting_line_id} ? '#16c049' : '#c01616')),  // Red for 0 values
                    borderColor: allData_{stat}_{game_id}_{betting_line_id}.map(d => d.stat === 0 ? '#421f1f' : (d.stat >= Line_{stat}_{game_id}_{betting_line_id} ? '#304f3a' : '#421f1f')),  // Darker red for 0 borders
                    borderWidth: 0.5,  // Thin border for a clean look
                    barPercentage: 1.0,  // No gap between bars
                    categoryPercentage: 1.0  // Fill category width
                }}]
            }},
            options: {{
                plugins: {{
                    legend: {{
                        display: false  // Remove legend entirely
                    }},
                    title: {{
                        display: true,  // Add title as a caption
                        text: '{stat}',  // Set title to stat name
                        font: {{
                            size: 16
                        }},
                        padding: {{
                            top: 10,
                            bottom: 20
                        }}
                    }},
                    annotation: {{
                        annotations: {{
                            line1: {{
                                type: 'line',
                                yMin: Line_{stat}_{game_id}_{betting_line_id},
                                yMax: Line_{stat}_{game_id}_{betting_line_id},
                                borderColor: '#fff',
                                borderWidth: 2,
                                label: {{ content: '', enabled: true, position: 'end' }}
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{ 
                        beginAtZero: true, 
                        ticks: {{
                            color: '#222831',
                            font: {{ size: 10 }}
                        }},
                        grid: {{
                            display: false
                        }},
                        stepSize: 0.5
                    }},
                    x: {{
                        ticks: {{
                            color: '#222831',
                            font: {{ size: 10 }}
                        }},
                        grid: {{
                            display: false
                        }}
                    }}
                }}
            }}
        }}); 
    }}

    function updateLine_{stat}_{game_id}_{betting_line_id}(newLine) {{
        Line_{stat}_{game_id}_{betting_line_id} = parseFloat(newLine);
        document.getElementById('{stat}_{game_id}_{betting_line_id}_lineValue').innerText = newLine;

        // Update annotation line
        chart_{stat}_{game_id}_{betting_line_id}.options.plugins.annotation.annotations.line1.yMin = Line_{stat}_{game_id}_{betting_line_id};
        chart_{stat}_{game_id}_{betting_line_id}.options.plugins.annotation.annotations.line1.yMax = Line_{stat}_{game_id}_{betting_line_id};

        // Update bar colors based on the new line
        chart_{stat}_{game_id}_{betting_line_id}.data.datasets[0].backgroundColor = allData_{stat}_{game_id}_{betting_line_id}.map(d => d.stat === 0 ? '#c01616' : (d.stat >= Line_{stat}_{game_id}_{betting_line_id} ? '#16c049' : '#c01616'));
        chart_{stat}_{game_id}_{betting_line_id}.data.datasets[0].borderColor = allData_{stat}_{game_id}_{betting_line_id}.map(d => d.stat === 0 ? '#421f1f' : (d.stat >= Line_{stat}_{game_id}_{betting_line_id} ? '#304f3a' : '#421f1f'));

        chart_{stat}_{game_id}_{betting_line_id}.update();
    }}

    function applyFilters_{stat}_{game_id}_{betting_line_id}() {{
        const teamFilter = document.getElementById('{stat}_{game_id}_{betting_line_id}_teamFilter').value;
        const homeAwayFilter = document.getElementById('{stat}_{game_id}_{betting_line_id}_homeAwayFilter').value;
        const startDate = document.getElementById('{stat}_{game_id}_{betting_line_id}_startDate').value;
        const endDate = document.getElementById('{stat}_{game_id}_{betting_line_id}_endDate').value;

        const filteredData = allData_{stat}_{game_id}_{betting_line_id}.filter(d => {{
            const isTeamMatch = (teamFilter === 'all') || (d.opponent === teamFilter);
            const isLocationMatch = (homeAwayFilter === 'all') || 
                                    (homeAwayFilter === 'home' && d.location === 'home') || 
                                    (homeAwayFilter === 'away' && d.location === 'away');
            const isDateInRange = (!startDate || new Date(d.date) >= new Date(startDate)) &&
                                  (!endDate || new Date(d.date) <= new Date(endDate));

            return isTeamMatch && isLocationMatch && isDateInRange;
        }});

        chart_{stat}_{game_id}_{betting_line_id}.data.labels = filteredData.map(d => `${{d.date}} ${{d.location === 'home' ? 'vs' : '@'}} ${{d.opponent}}`);
        chart_{stat}_{game_id}_{betting_line_id}.data.datasets[0].data = filteredData.map(d => d.stat || 0.02);  // Use 0.02 for zero values
        chart_{stat}_{game_id}_{betting_line_id}.data.datasets[0].backgroundColor = filteredData.map(d => d.stat === 0 ? '#c01616' : (d.stat >= Line_{stat}_{game_id}_{betting_line_id} ? '#16c049' : '#c01616'));
        chart_{stat}_{game_id}_{betting_line_id}.data.datasets[0].borderColor = filteredData.map(d => d.stat === 0 ? '#421f1f' : (d.stat >= Line_{stat}_{game_id}_{betting_line_id} ? '#304f3a' : '#421f1f'));
        chart_{stat}_{game_id}_{betting_line_id}.update();
    }}

    function clearFilters_{stat}_{game_id}_{betting_line_id}() {{
        // Reset filter values
        document.getElementById('{stat}_{game_id}_{betting_line_id}_teamFilter').value = "all";
        document.getElementById('{stat}_{game_id}_{betting_line_id}_homeAwayFilter').value = "all";
        document.getElementById('{stat}_{game_id}_{betting_line_id}_startDate').value = "";
        document.getElementById('{stat}_{game_id}_{betting_line_id}_endDate').value = "";

        // Reset the line slider to the default betting line
        document.getElementById('{stat}_{game_id}_{betting_line_id}_lineSlider').value = {betting_line};
        document.getElementById('{stat}_{game_id}_{betting_line_id}_lineValue').innerText = {betting_line};  // Update the displayed line value

        // Apply filters with no active filters and reset line annotation
        applyFilters_{stat}_{game_id}_{betting_line_id}();
        updateLine_{stat}_{game_id}_{betting_line_id}({betting_line});
    }}
    
    function resetLine_{stat}_{game_id}_{betting_line_id}_lineSlider () {{
        document.getElementById('{stat}_{game_id}_{betting_line_id}_lineSlider').value = {betting_line};
        document.getElementById('{stat}_{game_id}_{betting_line_id}_lineValue').innerText = {betting_line};  // Update the displayed line value
        
        updateLine_{stat}_{game_id}_{betting_line_id}({betting_line});
     }}

    // Initialize the chart immediately
    initChart_{stat}_{game_id}_{betting_line_id}();
    </script>
</div>
"""

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
            betting_line_id = str(betting_line).replace('.', '_')

            
            # Filter past game data for this stat
            stat_data = player_gamelogs[['Date', 'Opp', 'Is_Home', stat]].dropna()
            
            # Format x-axis labels and values for JavaScript
            chart_data = [
                {"date": row["Date"], "opponent": row["Opp"], "location": "home" if row["Is_Home"] == 1 else "away", "stat": row[stat]}
                for _, row in stat_data.iterrows()
            ]
            
            chart_data.sort(key=lambda x: x["date"])
            
            # Generate unique team options for the dropdown
            unique_teams = stat_data['Opp'].unique()
            team_options = "\n".join([f'<option value="{team}">{team}</option>' for team in unique_teams])
            
            # Generate the chart script
            chart_script = chart_script_template.format(
                stat=stat,
                game_id=game_id,
                betting_line_id=betting_line_id, 
                chart_data=chart_data,
                betting_line=betting_line,
                team_options=team_options
            )
            
            player_table = soup.select_one("#H2H-table")
            chart_soup = BeautifulSoup(chart_script, "html.parser")
            player_table.insert_after(chart_soup) 

        # Save modified HTML file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

print("All files have been processed.")
