let originalData = [];
let chartInstance;

$(document).ready(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const playerName = urlParams.get('name');
    const playerID = urlParams.get('id');
    $('#player-name').text(playerName);

    // Load historic data
    loadCSV('data/historic.csv').then(function(historicData) {
        // Filter data for the player
        originalData = historicData.filter(item => item.PlayerID === playerID);

        // Initialize opponent filter
        initializeOpponentFilter(originalData);

        // Initialize chart
        initializeChart();

        // Event handlers
        $('#stat-select, #home-filter, #away-filter, #opponent-filter, #period-filter').on('change', function() {
            updateChart();
        });
    });
});

// Function to load CSV files
function loadCSV(filePath) {
    return new Promise(function(resolve, reject) {
        Papa.parse(filePath, {
            download: true,
            header: true,
            skipEmptyLines: true,
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
                backgroundColor: 'rgba(54, 162, 235, 0.7)'
            }]
        },
        options: {
            scales: {
                x: {
                    title: { display: true, text: 'Date' }
                },
                y: {
                    title: { display: true, text: 'Value' }
                }
            }
        }
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
        filteredData = filteredData.filter(item => item.Is_Home !== '1');
    }
    if (!awayFilter) {
        filteredData = filteredData.filter(item => item.Is_Home !== '0');
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

    chartInstance.data.labels = labels;
    chartInstance.data.datasets[0].label = stat;
    chartInstance.data.datasets[0].data = data;
    chartInstance.update();
}
