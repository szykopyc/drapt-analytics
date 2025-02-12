var parsedCorrelationData = JSON.parse(correlationMatrixData);

function processCorrelationMatrix(matrix) {
    const labels = Object.keys(matrix);
    const data = [];

    for (let i = 0; i < labels.length; i++) {
        for (let j = 0; j < labels.length; j++) {
            data.push({
                x: labels[i],
                y: labels[j],
                v: matrix[labels[i]][labels[j]]
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
                width: ({ chart }) => {
                    if (!chart.chartArea) return 20;
                    return Math.min(chart.chartArea.width / labels.length);
                },
                height: ({ chart }) => {
                    if (!chart.chartArea) return 20;
                    return Math.min(chart.chartArea.width / labels.length, chart.chartArea.height / labels.length);
                },
                backgroundColor: ctx => {
                    const value = ctx.raw.v;

                    if (ctx.raw.x === ctx.raw.y) {
                        return 'rgb(76, 76, 76)'; // Yellow for same asset correlation (inverted)
                    }

                    if (value > 0) {
                        const opacity = Math.min(value, 1);
                        return `rgba(0, 255, 0, ${opacity})`; // Green for positive correlation (inverted red)
                    }

                    if (value < 0) {
                        const opacity = Math.min(Math.abs(value), 1);
                        return `rgba(255, 0, 0, ${opacity})`; // Red for negative correlation (inverted green)
                    }

                    return 'rgba(255, 255, 0, 0.2)'; // Yellow for near-zero correlation (inverted blue)
                }
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 0
            },
            scales: {
                x: {
                    type: 'category',
                    labels: labels,
                    position: 'top',
                    ticks: {
                        autoSkip: false,
                        maxRotation: 0,
                        minRotation: 0
                    },
                    offset: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'category',
                    labels: labels,
                    reverse: true,
                    offset: true,
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const { x, y, v } = ctx.raw;
                            return `Correlation between ${x} and ${y}: ${v.toFixed(2)}`;
                        }
                    }
                },
                legend: {
                    labels: {
                        generateLabels: chart => {
                            return [
                                {
                                    text: 'Positive Correlation',
                                    color: '#2f4f4f',
                                    fillStyle: 'rgba(0, 255, 0, 1)' // Green (inverted red)
                                },
                                {
                                    text: 'Negative Correlation',
                                    color: '#2f4f4f',
                                    fillStyle: 'rgba(255, 0, 0, 1)' // Red (inverted green)
                                },
                                {
                                    text: 'No Correlation',
                                    color: 'rgb(76, 76, 76)',
                                    fillStyle: 'black' // Yellow (inverted blue)
                                }
                            ];
                        }
                    }
                }
            }
        }
    });
});