var parsed_data = JSON.parse(portfolio_rolling_vol);

var rolling30 = parsed_data.data.map(row => row[0] * 100);
var rolling60 = parsed_data.data.map(row => row[1] * 100);
var rolling125 = parsed_data.data.map(row => row[2] * 100);

const ctx5 = document.getElementById('rolling-volatility-chart').getContext('2d');
new Chart(ctx5, {
    type: 'line',
    data: {
        labels: parsed_data['index'],
        datasets: [{
            label: 'Rolling 30',
            data: rolling30,
            borderColor: 'rgba(75, 192, 192, 1)', // Vivid light blue
            backgroundColor: 'rgba(75, 192, 192, 0.3)', // Slightly more opaque light blue
            cubicInterpolationMode: 'monotone',
            tension: 0.4,
            pointRadius: 0 // Set pointRadius to 0 to hide the points
        },{
            label: 'Rolling 60',
            data: rolling60,
            borderColor: 'rgba(54, 162, 235, 1)', // Slightly deeper blue
            backgroundColor: 'rgba(54, 162, 235, 0.3)', // Slightly more opaque blue
            cubicInterpolationMode: 'monotone',
            tension: 0.4,
            pointRadius: 0 // Set pointRadius to 0 to hide the points
        },{
            label: 'Rolling 125',
            data: rolling125,
            borderColor: 'rgba(255, 159, 64, 1)', // Orange
            backgroundColor: 'rgba(255, 159, 64, 0.3)', // Slightly more opaque orange
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
                        return value.toFixed(1) + '%'; // Round to 1 decimal place and append '%'
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