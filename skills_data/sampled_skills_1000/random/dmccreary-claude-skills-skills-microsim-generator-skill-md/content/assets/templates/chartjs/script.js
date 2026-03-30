// Chart.js MicroSim Template Script
// Load data from external JSON file or use inline data

// Chart data configuration
// Replace this with your actual data or load from data.json
const chartData = {
    labels: ['Category A', 'Category B', 'Category C', 'Category D'],
    values: [40, 30, 20, 10],
    colors: [
        'rgba(74, 144, 226, 0.85)',
        'rgba(80, 200, 120, 0.85)',
        'rgba(255, 193, 7, 0.85)',
        'rgba(220, 53, 69, 0.85)'
    ],
    borderColors: [
        'rgba(74, 144, 226, 1)',
        'rgba(80, 200, 120, 1)',
        'rgba(255, 193, 7, 1)',
        'rgba(220, 53, 69, 1)'
    ],
    categoryLabel: 'Category',
    valueLabel: 'Value (%)',
    valueUnit: '%',
    showTotal: true
};

// Tab switching functionality
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabId = button.dataset.tab;

        // Update active states
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));

        button.classList.add('active');
        document.getElementById(tabId).classList.add('active');
    });
});

// Pie Chart
const pieCtx = document.getElementById('pieChart').getContext('2d');
const pieChart = new Chart(pieCtx, {
    type: 'pie',
    data: {
        labels: chartData.labels,
        datasets: [{
            data: chartData.values,
            backgroundColor: chartData.colors,
            borderColor: chartData.borderColors,
            borderWidth: 2
        }]
    },
    plugins: [ChartDataLabels],
    options: {
        responsive: true,
        maintainAspectRatio: true,
        layout: {
            padding: {
                top: -35,
                bottom: 35,
                left: 5,
                right: 5
            }
        },
        radius: '75%',
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return context.label + ': ' + context.parsed.toFixed(1) + chartData.valueUnit;
                    }
                }
            },
            datalabels: {
                formatter: function(value, context) {
                    return context.chart.data.labels[context.dataIndex] + '\n' + value.toFixed(1) + chartData.valueUnit;
                },
                color: '#fff',
                font: {
                    weight: 'bold',
                    size: 12
                },
                textAlign: 'center',
                anchor: function(context) {
                    // Place small slices outside
                    return chartData.values[context.dataIndex] < 15 ? 'end' : 'center';
                },
                align: function(context) {
                    return chartData.values[context.dataIndex] < 15 ? 'end' : 'center';
                },
                offset: function(context) {
                    return chartData.values[context.dataIndex] < 15 ? 10 : 0;
                }
            }
        }
    }
});

// Bar Chart
const barCtx = document.getElementById('barChart').getContext('2d');
const barChart = new Chart(barCtx, {
    type: 'bar',
    data: {
        labels: chartData.labels,
        datasets: [{
            label: chartData.valueLabel,
            data: chartData.values,
            backgroundColor: chartData.colors,
            borderColor: chartData.borderColors,
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
            y: {
                beginAtZero: true,
                max: Math.max(...chartData.values) * 1.2,
                title: {
                    display: true,
                    text: chartData.valueLabel,
                    font: {
                        size: 14
                    }
                },
                ticks: {
                    callback: function(value) {
                        return value + chartData.valueUnit;
                    }
                }
            },
            x: {
                title: {
                    display: true,
                    text: chartData.categoryLabel,
                    font: {
                        size: 14
                    }
                }
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return context.parsed.y.toFixed(1) + chartData.valueUnit;
                    }
                }
            }
        }
    }
});

// Populate Table
const tableBody = document.getElementById('tableBody');
chartData.labels.forEach((label, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>
            <span class="color-indicator" style="background-color: ${chartData.colors[index]}"></span>
            ${label}
        </td>
        <td>${chartData.values[index].toFixed(1)}${chartData.valueUnit}</td>
    `;
    tableBody.appendChild(row);
});

// Add total row if configured
if (chartData.showTotal) {
    const total = chartData.values.reduce((sum, val) => sum + val, 0);
    const totalRow = document.createElement('tr');
    totalRow.classList.add('total-row');
    totalRow.innerHTML = `
        <td><strong>Total</strong></td>
        <td><strong>${total.toFixed(1)}${chartData.valueUnit}</strong></td>
    `;
    tableBody.appendChild(totalRow);
}
