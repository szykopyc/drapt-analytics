var parsed_data = performanceData;
var parsed_data = JSON.parse(parsed_data);

var data = parsed_data["data"];
var columns = parsed_data["columns"];
var portfolioIndex = columns.indexOf('Portfolio');

// Multiply portfolio data by 100
var portfolioData = data.map(function(row) {
    return row[portfolioIndex] * 100; // Convert to percentage
});

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
        }]
    },
    options: {
        responsive: true, // Make chart responsive
        maintainAspectRatio: false, // Allow the chart to change aspect ratio based on container width
        plugins: {
            title: {
                display: true,
                text: 'Past Cumulative Performance',
                color: "white",
                font:{
                    weight: 'bold'
                }
            },
            legend: {
                labels: {
                    color: "white", // Color for the legend text
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
                    color: "white", // Color for Y-axis ticks
                    callback: function(value) {
                        return value + '%'; // Append '%' to each tick label
                    }
                }
            },
            x: {
                ticks: {
                    color: "white", // Color for X-axis ticks
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