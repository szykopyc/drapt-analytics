var parsed_data = performanceData;
var parsed_data = JSON.parse(parsed_data);

var data = parsed_data["data"];
var columns = parsed_data["columns"];
var portfolioIndex = columns.indexOf('Portfolio');

// Multiply portfolio data by 100
var portfolioData = data.map(function(row) {
    return row[portfolioIndex] * 100; // Convert to percentage
});

var portfolioDataLength = portfolioData.length;

// Function to calculate moving average
function calculateMovingAverage(data, windowSize) {
    let ma = [];
    for (let i = 0; i < data.length; i++) {
        if (i < windowSize - 1) {
            ma.push(null); // Not enough data for MA, so push null
        } else {
            const window = data.slice(i - windowSize + 1, i + 1);
            const average = window.reduce((sum, value) => sum + value, 0) / window.length;
            ma.push(average);
        }
    }
    return ma;
}

var movingAveragePeriod = (portfolioDataLength/8).toFixed(0);

const movingAverageData = calculateMovingAverage(portfolioData, movingAveragePeriod);

let movingAveragePeriodLabel = movingAveragePeriod;

const ctx = document.getElementById('cumulative-performance-chart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: parsed_data['index'],
        datasets: [{
            label: 'Portfolio Performance',
            data: portfolioData,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            cubicInterpolationMode: 'monotone',
            tension: 0.4,
            pointRadius: 0 // Set pointRadius to 0 to hide the points
        },
        {
            label: `${movingAveragePeriodLabel}-Day Moving Average`,  // Correct string interpolation with backticks
            data: movingAverageData,
            borderColor: 'rgba(255, 159, 64, 1)', // Orange color for MA line
            backgroundColor: 'rgba(255, 159, 64, 0.2)', // Light orange
            cubicInterpolationMode: 'monotone',
            tension: 0.4,
            pointRadius: 0, // Set pointRadius to 0 to hide the points
            hidden: true
        }]
    },
    options: {
        responsive: true, // Make chart responsive
        maintainAspectRatio: false, // Allow the chart to change aspect ratio based on container width
        plugins: {
            title: {
                display: true,
                text: 'Past Cumulative Performance',
                color: "#2f4f4f",
                font:{
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
                intersect: false, // Allow tooltips to be triggered even when not on a point
                mode: 'nearest', // Show tooltip for the nearest point
                callbacks: {
                    label: function(tooltipItem) {
                        return tooltipItem.raw.toFixed(2) + '%'; // Format tooltip data as percentage
                    }
                }
            }
        },
        scales: {
            y: {
                ticks: {
                    color: "#2f4f4f", // Color for Y-axis ticks
                    callback: function(value) {
                        return value + '%'; // Append '%' to each tick label
                    }
                },
                grid: {
                    color: "rgba(47,79,79,0.1)"
                }
            },
            x: {
                ticks: {
                    color: "#2f4f4f", // Color for X-axis ticks
                    maxTicksLimit: 10
                },
                grid: {
                    color: "rgba(47,79,79,0.1)"
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