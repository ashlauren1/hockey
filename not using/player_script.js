let originalData = [];
let chartInstance;
let lineValue = 0.5; // Default line value

$(document).ready(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const playerName = urlParams.get('name');
    const playerID = urlParams.get('id');
    $('#player-name').text(playerName);

    // Load historic data
    loadCSV('data/historic.csv').then(function(historicData) {
        // Filter data for the player
        originalData = historicData.filter(item => item.PlayerID === playerID);

        // Convert date strings to Date objects
        originalData.forEach(item => {
            item.Date = formatDate(item.Date);
        });

        // Initialize opponent filter
        initializeOpponentFilter(originalData);

        // Initialize chart
        initializeChart();

        // Event handlers
        $('#stat-select, #home-filter, #away-filter, #opponent-filter, #period-filter').on('change', function() {
            updateChart();
        });

        // Event handler for line slider
        $('#line-slider').on('input', function() {
            lineValue = parseFloat($(this).val());
            $('#line-value-display').text(lineValue);
            updateChart();
        });

        // Adjust slider range based on selected stat
        $('#stat-select').on('change', function() {
            adjustSliderRange($(this).val());
            updateChart();
        });

        // Trigger initial chart update
        $('#stat-select').trigger('change');
    });
});

// Function to load CSV files
function loadCSV(filePath) {
    return new Promise(function(resolve, reject) {
        Papa.parse(filePath, {
            download: true,
            header: true,
            skipEmptyLines: true,
            dynamicTyping: true,
            complete: function(results) {
                resolve(results.data);
            },
            error: function(error) {
                reject(error);
            }
        });
    });
}

function initializeOpponentFilter(data) {
    const opponentsSet = new Set(data.map(item => item.Opp));
    const opponents = Array.from(opponentsSet).sort();
    const opponentFilter = $('#opponent-filter');

    opponentFilter.empty(); // Clear existing options
    opponentFilter.append(`<option value="">All Opponents</option>`);

    opponents.forEach(opp => {
        opponentFilter.append(`<option value="${opp}">${opp}</option>`);
    });
}

function initializeChart() {
    const ctx = document.getElementById('player-chart').getContext('2d');
    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: $('#stat-select').val(),
                data: [],
                backgroundColor: [],
                borderColor: 'rgba(0, 0, 0, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: {
                    title: { display: true, text: 'Date' }
                },
                y: {
                    title: { display: true, text: 'Value' },
                    beginAtZero: true
                }
            },
            plugins: {
                annotation: {
                    annotations: {
                        line: {
                            type: 'line',
                            yMin: lineValue,
                            yMax: lineValue,
                            borderColor: 'white',
                            borderWidth: 2,
                            label: {
                                enabled: true,
                                content: `Line: ${lineValue}`,
                                position: 'start',
                                backgroundColor: 'rgba(0,0,0,0.7)',
                                color: 'white'
                            }
                        }
                    }
                }
            }
        },
        plugins: [Chart.registry.getPlugin('annotation')]
    });

    updateChart();
}

function updateChart() {
    const stat = $('#stat-select').val();
    const homeFilter = $('#home-filter').is(':checked');
    const awayFilter = $('#away-filter').is(':checked');
    const opponent = $('#opponent-filter').val();
    const period = $('#period-filter').val();

    let filteredData = originalData.slice(); // Clone the data

    // Apply Home/Away filter
    if (!homeFilter) {
        filteredData = filteredData.filter(item => item.Is_Home !== 1);
    }
    if (!awayFilter) {
        filteredData = filteredData.filter(item => item.Is_Home !== 0);
    }

    // Apply Opponent filter
    if (opponent) {
        filteredData = filteredData.filter(item => item.Opp === opponent);
    }

    // Apply Period filter
    if (period === 'Season') {
        filteredData = filteredData.filter(item => item.Season === '2024-25');
    } else if (period.startsWith('L')) {
        const numGames = parseInt(period.slice(1));
        filteredData.sort((a, b) => new Date(b.Date) - new Date(a.Date)); // Most recent first
        filteredData = filteredData.slice(0, numGames);
        filteredData.sort((a, b) => new Date(a.Date) - new Date(b.Date)); // Sort back to oldest first
    }

    // Update chart data
    const labels = filteredData.map(item => item.Date);
    const data = filteredData.map(item => parseFloat(item[stat]));

    // Determine bar colors based on lineValue
    const backgroundColors = data.map(value => {
        if (value > lineValue) {
            return 'rgba(0, 255, 0, 0.7)'; // Green
        } else if (value < lineValue) {
            return 'rgba(255, 0, 0, 0.7)'; // Red
        } else {
            return 'rgba(255, 255, 0, 0.7)'; // Yellow
        }
    });

    chartInstance.data.labels = labels;
    chartInstance.data.datasets[0].label = stat;
    chartInstance.data.datasets[0].data = data;
    chartInstance.data.datasets[0].backgroundColor = backgroundColors;

    // Update the horizontal line
    chartInstance.options.plugins.annotation.annotations.line.yMin = lineValue;
    chartInstance.options.plugins.annotation.annotations.line.yMax = lineValue;
    chartInstance.options.plugins.annotation.annotations.line.label.content = `Line: ${lineValue}`;

    chartInstance.update();
}

function adjustSliderRange(stat) {
    let maxRange;
    switch (stat) {
        case 'G':
        case 'A':
        case 'PTS':
            maxRange = 5;
            break;
        case 'SOG':
            maxRange = 15;
            break;
        case 'HIT':
        case 'BLK':
            maxRange = 10;
            break;
        default:
            maxRange = 10;
    }
    $('#line-slider').attr('max', maxRange);
    $('#line-slider').val(lineValue);
    $('#line-value-display').text(lineValue);
}

// Helper function to format date to YYYY-MM-DD
function formatDate(dateStr) {
    const [month, day, year] = dateStr.split('/');
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
}
