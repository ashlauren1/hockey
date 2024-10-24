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
            dynamicTyping: true, // Automatically typecast data
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
    // Convert dates to YYYY-MM-DD format for consistency
    scheduleData.forEach(item => {
        item.Date = formatDate(item.Date);
    });

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
        let percentages = calculateHistoricalPercentages(historicData, entry.PlayerID);
        return { ...entry, ...percentages };
    });

    return mergedData;
}

// Function to calculate historical percentages
function calculateHistoricalPercentages(historicData, playerID) {
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
            percentages[`${period}_${stat}`] = games.length > 0 ? ((overLine / games.length) * 100).toFixed(1) : '0.0';
        });
    });

    return percentages;
}

function initializeFilters(data) {
    // Initialize Date Range Filter
    $('#date-range').on('change', function() {
        filterTable();
    });

    // Initialize Game Filters
    const gamesSet = new Set();
    data.forEach(item => {
        const gameLabel = `${item.GameID} (${item.HomeTeam} vs ${item.AwayTeam})`;
        gamesSet.add(gameLabel);
    });
    const games = Array.from(gamesSet).sort();
    const gameFiltersDiv = $('#game-filters');
    gameFiltersDiv.empty(); // Clear existing filters
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
                const value = parseFloat(data);
                return isNaN(value) ? 'N/A' : `${(value * 100).toFixed(1)}%`;
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
        // Indices for probability and historical percentage columns
        const indices = [columns.length - periods.length - 1];
        for (let i = periods.length; i > 0; i--) {
            indices.push(lastIndex - (i - 1));
        }
        statColumns[stat] = indices;
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

    // Apply initial filters
    filterTable();
}

function filterTable() {
    // Get selected date range
    const dateRange = $('#date-range').val();

    // Get selected games
    const selectedGames = $('.game-filter:checked').map(function() {
        return this.value.split(' ')[0]; // Extract GameID
    }).get();

    // Clear previous filters
    $.fn.dataTable.ext.search = [];

    // Apply filters
    $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
        const gameID = data[1]; // GameID is in column index 1
        const dateStr = data[2];   // Date is in column index 2
        const dateObj = new Date(dateStr);

        const today = new Date();
        today.setHours(0, 0, 0, 0); // Set time to midnight

        let showRow = true;

        // Date range filter
        if (dateRange === 'today') {
            const tomorrow = new Date(today);
            tomorrow.setDate(today.getDate() + 1);

            if (dateObj < today || dateObj > tomorrow) {
                showRow = false;
            }
        } else if (dateRange === 'this-week') {
            const weekStart = new Date(today);
            const weekEnd = new Date(today);
            weekEnd.setDate(today.getDate() + 7);

            if (dateObj < today || dateObj > weekEnd) {
                showRow = false;
            }
        }

        // Game filter
        if (selectedGames.length > 0 && !selectedGames.includes(gameID)) {
            showRow = false;
        }

        return showRow;
    });

    dataTable.draw();
}

// Helper function to format date to YYYY-MM-DD
function formatDate(dateStr) {
    const [month, day, year] = dateStr.split('/');
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
}
