var parsed_data = monteCarloStressData;

var parsed_data = JSON.parse(parsed_data);

var data = parsed_data["data"];
var columns = parsed_data["columns"];
var timestamps = data["index"];

var meanIndex = columns.indexOf('Mean');
var upperSDIndex = columns.indexOf('UpperSD');
var lowerSDIndex = columns.indexOf('LowerSD');
    
var meanData = data.map(function(row){
    return row[meanIndex];
});
   
var upperSDData= data.map(function(row){
    return row[upperSDIndex];
});

var lowerSDData = data.map(function(row){
    return row[lowerSDIndex];
});


const ctx6 = document.getElementById('monte-carlo-stress').getContext('2d');
new Chart(ctx6, {
    type: 'line',
    data: {
        labels: parsed_data['index'],
        datasets: [{
            label: 'Mean Simulated Performance',
            data: meanData,
            borderColor: '#10263b',
            backgroundColor: '#10263b',
            cubicInterpolationMode: 'monotone',
            tension: 0.4,
            pointRadius: 0 // Set pointRadius to 0 to hide the points
        },{
            label: '+1 Standard Deviation',
            data: upperSDData,
            borderColor: 'rgba(80, 203, 203, 0.2)',
            backgroundColor: 'rgba(94, 239, 239, 0.2)',
            fill: false,
            cubicInterpolationMode: 'monotone',
            tension: 0.4,
            pointRadius: 0 // Set pointRadius to 0 to hide the points
        },{
            label: '-1 Standard Deviation',
            data: lowerSDData,
            borderColor: 'rgba(80, 203, 203, 0.2)',
            backgroundColor: 'rgba(94, 239, 239, 0.2)',
            fill: '-1',
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
                text: 'Monte Carlo Simulated Portfolio Value',
                color: '#2f4f4f',
                font:{
                    weight: 'bold'
                }
            },

            legend: {
                labels: {
                    color: '#2f4f4f', // Color for the legend text
                }
            },
            tooltip: {
                enabled: true, // Enable tooltips
                intersect: false, // Allow tooltips to be triggered even when not on a point
                mode: 'nearest', // Show tooltip for the nearest point
                callbacks: {
                    label: function(tooltipItem) {
                        return tooltipItem.raw.toFixed(2); // Format tooltip data as percentage
                    }
                }
            }
        },
        scales: {
            y: {
                ticks: {
                    color: '#2f4f4f', // Color for Y-axis ticks
                },
                grid: {
                    color: "rgba(47,79,79,0.1)"
                }
            },
            x: {
                ticks: {
                    color: "#2f4f4f", // Color for X-axis ticks
                },
                grid: {
                    color: "rgba(47,79,79,0.1)"
                }
            }
        },
        animation: {
            duration: 500,  // Reduce animation duration (default is 1000ms)
            easing: 'linear', // Use a linear easing function for less complex animation
            animateScale: true,  // Optionally reduce scale animations
            animateRotate: true  // Optionally reduce rotate animations
        }
    }
});