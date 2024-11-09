import pandas as pd
from bs4 import BeautifulSoup
import os

# Paths to CSV files and directory containing HTML files
gamelogs_path = r'C:\Users\ashle\Documents\Projects\hockey\data\gamelogs.csv'
html_dir = r'C:\Users\ashle\Documents\Projects\hockey\players'

# Load the data
gamelogs_df = pd.read_csv(gamelogs_path)
gamelogs_df['Date'] = pd.to_datetime(gamelogs_df['Date'])  # Ensure Date is a datetime type
gamelogs_df = gamelogs_df.sort_values(by='Date')  # Sort by Date in ascending order

# List of all stats to generate charts for
all_stats = ["G", "A", "PTS", "SOG", "HIT", "BLK", "TOI"]

# Default betting line and stat
default_betting_line = 0.5
default_stat = "G"

# Chart.js template for a single bar chart with dropdown to change stats
chart_script_template = """
<div class="player-chart-container">
    <!-- Stat Selection Dropdown -->
    <div class="barChart-filters">
        <div class="barChartFilter">
            <label for="statSelector_{player_id}">Stat:</label>
            <select id="statSelector_{player_id}" onchange="updateStat_{player_id}(this.value)">
                {stat_options}
            </select>
        </div>  
        <div class="barChartFilter">
            <label for="teamFilter_{player_id}">Opponent:</label>
            <select id="teamFilter_{player_id}" onchange="applyFilters_{player_id}()">
                <option value="all">All</option>
                {team_options}
            </select>
        </div>
        <div class="barChartFilter">
            <label for="homeAwayFilter_{player_id}">Home/Away:</label>
            <select id="homeAwayFilter_{player_id}" onchange="applyFilters_{player_id}()">
                <option value="all">All</option>
                <option value="home">Home</option>
                <option value="away">Away</option>
            </select>
        </div>
        <div class="barChartFilter">
            <label for="startDate_{player_id}">Start:</label>
            <input type="date" id="startDate_{player_id}" onchange="applyFilters_{player_id}()">
        </div>
        <div class="barChartFilter">
            <label for="endDate_{player_id}">End:</label>
            <input type="date" id="endDate_{player_id}" onchange="applyFilters_{player_id}()">
        </div>
    </div>
    <canvas id="chart_{player_id}" class="player-barChart"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@1.1.0"></script>
    <div class="slider-container">
        <div id="line-slider">
            <label for="lineSlider_{player_id}">Change Line:</label>
            <input type="range" id="lineSlider_{player_id}" min="0" max="30" step="0.5" value="{betting_line}" oninput="updateLine_{player_id}(this.value)">
            <span id="lineValue_{player_id}">{betting_line}</span>
        </div>
        <div class="chartButtons">
            <button id="reset-line-btn_{player_id}" onclick="resetLine_{player_id}()" class="reset-line-btn">Reset Line</button>
            <button id="clearFiltersBtn_{player_id}" onclick="clearFilters_{player_id}()" class="clear-chart-filters">Clear Filters</button>
        </div>
    </div>
</div>


    <script>
    const allData_{player_id} = {chart_data};  // Full data for player
    let currentStat_{player_id} = "{default_stat}";
    let Line_{player_id} = {betting_line};  // Default betting line
    let chart_{player_id};

    function initChart_{player_id}() {{
        const ctx = document.getElementById('chart_{player_id}').getContext('2d');
        chart_{player_id} = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: allData_{player_id}.map(d => `${{d.location === 'home' ? 'vs' : '@'}} ${{d.opponent}}\\n${{new Date(d.date).toLocaleDateString('en-US', {{ year: '2-digit', month: 'numeric', day: 'numeric' }})}}`),
                datasets: [{{
                    label: currentStat_{player_id},
                    data: allData_{player_id}.map(d => d[currentStat_{player_id}] || 0.0),
                    backgroundColor: allData_{player_id}.map(d => d[currentStat_{player_id}] === 0 ? '#c01616' : (d[currentStat_{player_id}] >= Line_{player_id} ? '#16c049' : '#c01616')),
                    borderColor: allData_{player_id}.map(d => d[currentStat_{player_id}] === 0 ? '#421f1f' : (d[currentStat_{player_id}] >= Line_{player_id} ? '#304f3a' : '#421f1f')),
                    borderWidth: 0.25,
                    barPercentage: 1.0,
                    categoryPercentage: 1.0
                }}]
            }},
            options: {{
                plugins: {{
                    legend: {{ display: false }},
                    title: {{
                        display: true,
                        text: currentStat_{player_id},
                        font: {{ size: 16 }}
                    }},
                    annotation: {{
                        annotations: {{
                            line1: {{
                                type: 'line',
                                yMin: Line_{player_id},
                                yMax: Line_{player_id},
                                borderColor: '#ffffff',
                                borderWidth: 2
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{ 
                        beginAtZero: true, 
                        ticks: {{ color: '#222831', font: {{ size: 10 }} }},
                        grid: {{ display: false }},
                        stepSize: 1.0
                    }},
                    x: {{
                        ticks: {{ 
                            color: '#222831',
                            font: {{ size: 10 }},
                        }},
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
    }}

    function updateStat_{player_id}(selectedStat) {{
        currentStat_{player_id} = selectedStat;
        chart_{player_id}.data.datasets[0].data = allData_{player_id}.map(d => d[selectedStat] || 0.0);
        chart_{player_id}.data.datasets[0].label = selectedStat;
        chart_{player_id}.options.plugins.title.text = selectedStat;

        chart_{player_id}.data.datasets[0].backgroundColor = allData_{player_id}.map(d => d[selectedStat] === 0 ? '#c01616' : (d[selectedStat] >= Line_{player_id} ? '#16c049' : '#c01616'));
        chart_{player_id}.update();
    }}

    function updateLine_{player_id}(newLine) {{
        Line_{player_id} = parseFloat(newLine);
        document.getElementById('lineValue_{player_id}').innerText = newLine;

        chart_{player_id}.options.plugins.annotation.annotations.line1.yMin = Line_{player_id};
        chart_{player_id}.options.plugins.annotation.annotations.line1.yMax = Line_{player_id};

        chart_{player_id}.data.datasets[0].backgroundColor = allData_{player_id}.map(d => d[currentStat_{player_id}] === 0 ? '#c01616' : (d[currentStat_{player_id}] >= Line_{player_id} ? '#16c049' : '#c01616'));
        chart_{player_id}.update();
    }}

    function applyFilters_{player_id}() {{
        const teamFilter = document.getElementById('teamFilter_{player_id}').value;
        const homeAwayFilter = document.getElementById('homeAwayFilter_{player_id}').value;
        const startDate = document.getElementById('startDate_{player_id}').value;
        const endDate = document.getElementById('endDate_{player_id}').value;

        const filteredData = allData_{player_id}.filter(d => {{
            const isTeamMatch = (teamFilter === 'all') || (d.opponent === teamFilter);
            const isLocationMatch = (homeAwayFilter === 'all') || 
                                    (homeAwayFilter === 'home' && d.location === 'home') || 
                                    (homeAwayFilter === 'away' && d.location === 'away');
            const isDateInRange = (!startDate || new Date(d.date) >= new Date(startDate)) &&
                                  (!endDate || new Date(d.date) <= new Date(endDate));
            return isTeamMatch && isLocationMatch && isDateInRange;
        }});

        chart_{player_id}.data.labels = filteredData.map(d => `${{d.date}} ${{d.location === 'home' ? 'vs' : '@'}} ${{d.opponent}}`);
        chart_{player_id}.data.datasets[0].data = filteredData.map(d => d[currentStat_{player_id}] || 0.0);
        chart_{player_id}.update();
    }}

    function clearFilters_{player_id}() {{
        document.getElementById('teamFilter_{player_id}').value = "all";
        document.getElementById('homeAwayFilter_{player_id}').value = "all";
        document.getElementById('startDate_{player_id}').value = "";
        document.getElementById('endDate_{player_id}').value = "";
        applyFilters_{player_id}();
        updateLine_{player_id}({betting_line});
    }}

    initChart_{player_id}();
    </script>
"""

# Process each HTML file
for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(html_dir, filename)
        player_id = filename.replace(".html", "")
                
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as file:  # Fallback encoding
                soup = BeautifulSoup(file, "html.parser")

        # Select where to insert the chart based on table id
        player_table = soup.select_one("#table-container")
        if not player_table:
            print(f"No player table found in {filename}. Skipping.")
            continue
        # Filter gamelogs for the player
        player_gamelogs = gamelogs_df[gamelogs_df['PlayerID'] == player_id]
        if player_gamelogs.empty:
            print(f"No gamelog data found for player {player_id} in {filename}")
            continue

        # Generate team options and chart data
        unique_teams = sorted(player_gamelogs['Opp'].unique(), key=lambda x: x.lower())  # Sort alphabetically
        team_options = "\n".join([f'<option value="{team}">{team}</option>' for team in unique_teams])
        chart_data = [
            {
                "date": row["Date"].strftime("%Y-%m-%d"),
                "opponent": row["Opp"],
                "location": "home" if row["Is_Home"] == 1 else "away",
                **{stat: row[stat] for stat in all_stats if stat in row}
            }
            for _, row in player_gamelogs.iterrows()
        ]
        chart_data.sort(key=lambda x: x["date"])

        # Mapping of short stat codes to full names
        stat_map = {
            "G": "Goals",
            "A": "Assists",
            "PTS": "Points",
            "SOG": "Shots on Goal",
            "HIT": "Hits",
            "BLK": "Blocked Shots",
            "TOI": "Time on Ice"
        }

        # Generate stat options for the dropdown
        stat_options = "\n".join([f'<option value="{stat}">{stat_map.get(stat, stat)}</option>' for stat in all_stats])

        # Generate and insert the chart script
        chart_script = chart_script_template.format(
            player_id=player_id,
            stat_options=stat_options,
            chart_data=chart_data,
            betting_line=default_betting_line,
            default_stat=default_stat,
            team_options=team_options
        )
        chart_soup = BeautifulSoup(chart_script, "html.parser")
        player_table.insert_before(chart_soup)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

print("All files have been processed.")