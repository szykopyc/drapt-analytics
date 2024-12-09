var parsedCorrelationData = JSON.parse(correlationMatrixData);

function processCorrelationMatrix(matrix) {
    const labels = Object.keys(matrix); // Extract stock names as labels
    const data = [];

    // Convert matrix into a list of objects with x, y, and v properties
    for (let i = 0; i < labels.length; i++) {
        for (let j = 0; j < labels.length; j++) {
            data.push({
                x: labels[i], // x-axis: Row label (stock ticker)
                y: labels[j], // y-axis: Column label (stock ticker)
                v: matrix[labels[i]][labels[j]] // v: correlation value
            });
        }
    }

    return { labels, data };
}

const { labels, data: matrixData } = processCorrelationMatrix(parsedCorrelationData);

const ctx4 = document.getElementById('correlation-matrix-figure').getContext('2d');

document.addEventListener("DOMContentLoaded", () => {
    new Chart(ctx4, {
        type: 'matrix',
        data: {
            datasets: [{
                label: 'Correlation Matrix',
                data: matrixData,
                // Dynamically calculate cell size
                width: ({ chart }) => {
                    if (!chart.chartArea) {
                        return 20; // Fallback value if chartArea is not ready
                    }
                    // Reduce the size dynamically to fit the matrix
                    const cellSize = Math.min(chart.chartArea.width / labels.length);
                    return cellSize; // Ensure the cells fit without space between them
                },
                height: ({ chart }) => {
                    if (!chart.chartArea) {
                        return 20; // Fallback value if chartArea is not ready
                    }
                    // Ensure height is equal to width to make cells square
                    const cellSize = Math.min(chart.chartArea.width / labels.length, chart.chartArea.height / labels.length);
                    return cellSize; // Ensure cells fit without space between them
                },
                backgroundColor: ctx => {
                    const value = ctx.raw.v;

                    if (ctx.raw.x === ctx.raw.y) {
                        // Portfolio-portfolio cell (yellow color)
                        return 'rgba(255, 255, 0, 1)';
                    }

                    // For positive correlations (neon blue)
                    if (value > 0) {
                        const opacity = Math.min(value, 1); // As the correlation approaches 1, opacity increases
                        return `rgba(0, 255, 255, ${opacity})`; // Neon blue with opacity
                    }

                    // For negative correlations (neon red)
                    if (value < 0) {
                        const opacity = Math.min(Math.abs(value), 1); // As the correlation approaches -1, opacity increases
                        return `rgba(255, 0, 0, ${opacity})`; // Neon red with opacity
                    }

                    // For near zero correlations, give a light gray or semi-transparent color to indicate no strong correlation
                    return 'rgba(128, 128, 128, 0.2)'; // Light gray for near-zero correlations
                }
            }]
        },
        options: {
            responsive: true,  // Let Chart.js automatically handle resizing
            animation: {
                duration: 0  // Disable animations
            },
            scales: {
                x: {
                    type: 'category',
                    labels: labels,
                    position: 'top',
                    ticks: {
                        autoSkip: false,
                        maxRotation: 0, // Disable rotation to prevent overflow on X-axis labels
                        minRotation: 0
                    },
                    offset: true,  // Move axis to prevent overlap
                    grid: {
                        display: false // Disable gridlines for the x-axis
                    }
                },
                y: {
                    type: 'category',
                    labels: labels,
                    reverse: true,
                    offset: true, // Move axis to prevent overlap
                    grid: {
                        display: false // Disable gridlines for the x-axis
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const { x, y, v } = ctx.raw;
                            return `Correlation between ${x} and ${y}: ${v.toFixed(2)}`; // Show asset pair and correlation value
                        }
                    }
                },
                legend: {
                    labels: {
                        generateLabels: chart => {
                            return [
                                {
                                    text: 'Positive Correlation',
                                    fillStyle: 'rgba(0, 255, 255, 1)' // Neon blue for positive correlation
                                },
                                {
                                    text: 'Negative Correlation',
                                    fillStyle: 'rgba(255, 0, 0, 1)' // Neon red for negative correlation
                                },
                                {
                                    text: 'No Correlation',
                                    fillStyle: 'rgba(255, 255, 0, 1)' // Yellow for same asset correlation
                                }
                            ];
                        }
                    }
                }
            }
        }
    });
});