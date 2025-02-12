// Assuming histogramData is provided or fetched before this point
var parsedData = JSON.parse(histogramData);
var data = parsedData["data"];
var columns = parsedData["columns"];

var portfolioIndex = columns.indexOf('Portfolio');

var dailyReturns = data.map(function(row) {
    return row[portfolioIndex] * 100; // Convert to percentage
});

// Function to create the histogram
function createHistogram(data, binsCount) {
    const minReturn = Math.min(...data);
    const maxReturn = Math.max(...data);
    const binSize = (maxReturn - minReturn) / binsCount;

    const bins = new Array(binsCount).fill(0);

    data.forEach(returnVal => {
        const binIndex = Math.floor((returnVal - minReturn) / binSize);
        if (binIndex >= 0 && binIndex < binsCount) {
            bins[binIndex]++;
        }
    });

    return {
        labels: Array.from({ length: binsCount }, (_, i) => {
            const binStart = (minReturn + i * binSize).toFixed(2); // Round to 2 decimal places
            const binEnd = (minReturn + (i + 1) * binSize).toFixed(2); // Round to 2 decimal places
            return `${binStart}% - ${binEnd}%`; // Add '%' symbol to bin ranges
        }),
        data: bins
    };
}

// Generate histogram data
const binsCount = parseInt(Math.sqrt(dailyReturns.length).toFixed(0), 10);
const histogramDataChart = createHistogram(dailyReturns, binsCount);

// Chart.js configuration
const ctx3 = document.getElementById('histogramChart').getContext('2d');
const histogramChart = new Chart(ctx3, {
    type: 'bar',
    data: {
        labels: histogramDataChart.labels,
        datasets: [{
            label: 'Daily Portfolio Returns',
            data: histogramDataChart.data,
            backgroundColor: 'rgba(75, 192, 192, 0.2)', // Light green
            borderColor: 'rgba(75, 192, 192, 1)', // Darker green
            borderWidth: 1
        }]
    },
    options: {
        responsive: true, // Make chart responsive
        maintainAspectRatio: false, // Allow the chart to change aspect ratio based on container width
        plugins: {
            title: {
                display: true,
                text: 'Portfolio Daily Returns Histogram',
                color: "#2f4f4f",
                font: {
                    weight: 'bold'
                }
            },
            legend: {
                labels: {
                    color: "#2f4f4f", // Color for the legend text
                }
            },
            tooltip: {
                enabled: true, // Enable tooltips
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    color: "#2f4f4f", // Color for Y-axis ticks
                },
                grid: {
                    color: "rgba(47,79,79,0.1)"
                },
                title: {
                    display: true,
                    text: 'Frequency',
                    color: "#2f4f4f"
                }
            },
            x: {
                ticks: {
                    color: "#2f4f4f", // Color for X-axis ticks
                    maxTicksLimit: 10
                    
                },
                grid: {
                    color: "rgba(47,79,79,0.1)"
                },
                title: {
                    display: true,
                    text: 'Return Ranges',
                    color: "white"
                }
            }
        },
        animation: {
            duration: 300,  // Reduce animation duration (default is 1000ms)
            easing: 'linear', // Use a linear easing function for less complex animation
            animateScale: true,  // Optionally reduce scale animations
            animateRotate: true  // Optionally reduce rotate animations
        }
    }
});