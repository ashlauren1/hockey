// Map of stat names to their corresponding column indices in the DataTable
let statColumns = {};

// Store original data for filtering
let originalData = [];

// Store DataTable instance
let dataTable;

$(document).ready(function() {
    // Load all CSV files
    Promise.all([
        loadCSV('data/schedule.csv'),
        loadCSV('data/projectedStats.csv'),
        loadCSV('data/probabilityByOpp.csv'),
        loadCSV('data/historic.csv')
    ]).then(function(results) {
        const [scheduleData, projectedStatsData, probabilityData, historicData] = results;

        // Process and merge data
        originalData = processData(scheduleData, projectedStatsData, probabilityData, historicData);

        // Initialize filters and table
        initializeFilters(originalData);
        initializeTable(originalData);
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

// Function to process and merge data
function processData(scheduleData, projectedStatsData, probabilityData, historicData) {
    // Merge projectedStatsData and probabilityData on GameID and PlayerID
    let mergedData = projectedStatsData.map(proj => {
        // Find matching probability entry
        let probEntry = probabilityData.find(prob => prob.GameID === proj.GameID && prob.PlayerID === proj.PlayerID);

        // If probability data is found, merge it
        if (probEntry) {
            return { ...proj, ...probEntry };
        } else {
            return proj;
        }
    });

    // Add Game information from scheduleData
    mergedData = mergedData.map(entry => {
        let gameInfo = scheduleData.find(game => game.GameID === entry.GameID);
        if (gameInfo) {
            return { ...entry, GameDate: gameInfo.Date, HomeTeam: gameInfo.Home, AwayTeam: gameInfo.Away };
        } else {
            return entry;
        }
    });

    // Calculate historical percentages
    mergedData = mergedData.map(entry => {
        let percentages = calculateHistoricalPercentages(historicData, entry.PlayerID, entry.Team, entry.Opp);
        return { ...entry, ...percentages };
    });

    return mergedData;
}

// Function to calculate historical percentages
function calculateHistoricalPercentages(historicData, playerID, team, opponent) {
    // Filter data for the player
    const playerData = historicData.filter(item => item.PlayerID === playerID);

    // Sort by date
    playerData.sort((a, b) => new Date(a.Date) - new Date(b.Date));

    const periods = ['L5', 'L10', 'L20', 'Season', 'AllTime'];
    const stats = ['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK'];
    const percentages = {};

    periods.forEach(period => {
        let games;
        if (period === 'AllTime') {
            games = playerData;
        } else if (period === 'Season') {
            games = playerData.filter(item => item.Season === '2024-25');
        } else {
            const numGames = parseInt(period.slice(1));
            games = playerData.slice(-numGames);
        }

        stats.forEach(stat => {
            const overLine = games.filter(game => parseFloat(game[stat]) > 0.5).length;
            percentages[`${period}_${stat}`] = ((overLine / games.length) * 100).toFixed(1) || '0.0';
        });
    });

    return percentages;
}

function initializeFilters(data) {
    // Initialize Game Filters
    const gamesSet = new Set();
    data.forEach(item => {
        const gameLabel = `${item.GameID} (${item.HomeTeam} vs ${item.AwayTeam})`;
        gamesSet.add(gameLabel);
    });
    const games = Array.from(gamesSet).sort();
    const gameFiltersDiv = $('#game-filters');
    games.forEach(game => {
        const checkbox = `
            <input type="checkbox" class="game-filter" value="${game}" checked>
            <label>${game}</label>
        `;
        gameFiltersDiv.append(checkbox);
    });

    // Event handler for game filters
    $('.game-filter').on('change', function() {
        filterTable();
    });

    // Event handler for stat filters
    $('.stat-filter').on('change', function() {
        // Show or hide columns based on selected stats
        const selectedStats = $('.stat-filter:checked').map(function() {
            return this.value;
        }).get();

        // Loop over statColumns
        for (const [stat, indices] of Object.entries(statColumns)) {
            indices.forEach(index => {
                const column = dataTable.column(index);
                if (selectedStats.includes(stat)) {
                    column.visible(true);
                } else {
                    column.visible(false);
                }
            });
        }
    });

    // Event handler for date filters
    $('#start-date, #end-date').on('change', function() {
        filterTable();
    });
}

function initializeTable(data) {
    // Define columns
    const columns = [
        {
            data: 'Player',
            title: 'Player',
            render: function(data, type, row) {
                return `<a href="player.html?name=${encodeURIComponent(data)}&id=${encodeURIComponent(row.PlayerID)}">${data}</a>`;
            }
        },
        { data: 'GameID', title: 'Game ID' },
        { data: 'GameDate', title: 'Date' },
        { data: 'Team', title: 'Team' },
        { data: 'Opp', title: 'Opponent' }
    ];

    // Stat columns and their indices
    const stats = ['G', 'A', 'PTS', 'SOG', 'HIT', 'BLK'];
    statColumns = {}; // Reset statColumns

    stats.forEach(stat => {
        // Probability columns
        let probCol = {
            data: `0.5+ ${stat}`,
            title: `Over 0.5 ${stat}`,
            render: function(data) {
                return `${(parseFloat(data) * 100).toFixed(1)}%`;
            }
        };
        columns.push(probCol);

        // Historical percentage columns
        const periods = ['L5', 'L10', 'L20', 'Season', 'AllTime'];
        periods.forEach(period => {
            let histCol = {
                data: `${period}_${stat}`,
                title: `${period} % Over 0.5 ${stat}`,
                render: function(data) {
                    return `${data}%`;
                }
            };
            columns.push(histCol);
        });

        // Update statColumns for filtering
        if (!statColumns[stat]) {
            statColumns[stat] = [];
        }
        const lastIndex = columns.length - 1;
        statColumns[stat].push(lastIndex - 5, lastIndex - 4, lastIndex - 3, lastIndex - 2, lastIndex - 1);
    });

    // Initialize DataTable
    dataTable = $('#data-table').DataTable({
        data: data,
        columns: columns,
        order: [[5, 'desc']], // Default sorting by first stat probability
        columnDefs: [
            { targets: '_all', visible: true },
            { targets: [0, 1, 2, 3, 4], visible: true } // Always show Player, GameID, Date, Team, Opponent
        ],
        scrollX: true // Enable horizontal scrolling if needed
    });
}

function filterTable() {
    // Get selected games
    const selectedGames = $('.game-filter:checked').map(function() {
        return this.value.split(' ')[0]; // Extract GameID
    }).get();

    // Get date range
    const startDate = $('#start-date').val();
    const endDate = $('#end-date').val();

    // Clear previous filters
    $.fn.dataTable.ext.search = [];

    // Apply filters
    $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
        const gameID = data[1]; // GameID is in column index 1
        const date = data[2];   // Date is in column index 2
        const dateObj = new Date(date);

        // Game filter
        if (selectedGames.length > 0 && !selectedGames.includes(gameID)) {
            return false;
        }

        // Date filter
        if (startDate) {
            const startDateObj = new Date(startDate);
            if (dateObj < startDateObj) {
                return false;
            }
        }
        if (endDate) {
            const endDateObj = new Date(endDate);
            if (dateObj > endDateObj) {
                return false;
            }
        }

        return true;
    });

    dataTable.draw();
}
