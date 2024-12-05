document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('customPortfolioTable');
    const addRowButton = document.getElementById('addRow');
    const submitPortfolioButton = document.getElementById('submitPortfolio');
    const weightSumElement = document.getElementById('weightSum');
    const portfolioName = document.getElementById('PortfolioName');
    const portfolioForDropdown = document.getElementById('portfolio_for'); // Dropdown for manager status

    function updateWeightSum() {
        let totalWeight = 0;
        const weightInputs = tableBody.querySelectorAll('input[name="allocationWeight"]');
        weightInputs.forEach(input => {
            const weight = parseFloat(input.value) || 0;
            totalWeight += weight;
        });
        weightSumElement.textContent = `(Sum: ${totalWeight.toFixed(2)})`;
    }

    function addRow() {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td><input type="text" name="ticker" placeholder="Ticker"></td>
            <td><input type="number" name="allocationWeight" placeholder="Weight" step="0.01" min="0"></td>
            <td><button type="button" class="deleteRow">Delete</button></td>
        `;
        tableBody.appendChild(newRow);

        const weightInput = newRow.querySelector('input[name="allocationWeight"]');
        weightInput.addEventListener('input', updateWeightSum);

        const deleteButton = newRow.querySelector('.deleteRow');
        deleteButton.addEventListener('click', function () {
            newRow.remove();
            updateWeightSum();
            ensureMinimumRows();
        });

        updateWeightSum();
    }

    function ensureMinimumRows() {
        while (tableBody.rows.length < 2) {
            addRow();
        }
    }

    function validatePortfolio() {
        const rows = tableBody.querySelectorAll('tr');
        if (rows.length < 2) {
            alert('Please add at least two rows.');
            return false;
        }

        let totalWeight = 0;
        let allRowsValid = true;

        rows.forEach(row => {
            const tickerInput = row.querySelector('input[name="ticker"]');
            const weightInput = row.querySelector('input[name="allocationWeight"]');
            const weight = parseFloat(weightInput.value) || 0;

            if (!tickerInput.value || weight <= 0) {
                allRowsValid = false;
            }
            totalWeight += weight;
        });

        if (!allRowsValid) {
            alert('Ensure all rows are filled with valid ticker symbols and positive weights.');
            return false;
        }

        if (Math.abs(totalWeight - 1) > 0.01) {
            alert('The total weight must add up to 1.');
            return false;
        }

        return true;
    }

    submitPortfolioButton.addEventListener('click', function () {
        if (validatePortfolio()) {
            const portfolio = [];
            const rows = tableBody.querySelectorAll('tr');
            const portfolioNameValue = portfolioName.value.trim();

            if (!portfolioNameValue) {
                alert('Please provide a name for the portfolio.');
                return;
            }

            rows.forEach(row => {
                const ticker = row.querySelector('input[name="ticker"]').value;
                const weight = parseFloat(row.querySelector('input[name="allocationWeight"]').value);
                portfolio.push({ ticker, weight });
            });

            const payload = {
                portfolioName: portfolioNameValue,
                portfolio,
            };

            // Add portfolioFor value if the dropdown exists
            if (portfolioForDropdown) {
                const portfolioForValue = portfolioForDropdown.value;
                if (!portfolioForValue) {
                    alert('Please select the portfolio type.');
                    return;
                }
                payload.portfolioFor = portfolioForValue;
            }

            fetch('/create-portfolio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            })
                .then(response => {
                    if (response.ok) {
                        return response.json().catch(() => {
                            window.location.href = '/risk';
                        });
                    } else {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                })
                .then(data => {
                    alert('Your portfolio has been successfully created!');
                    window.location.href = '/risk';
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while submitting your portfolio. Please try again.');
                });
        }
    });

    ensureMinimumRows();
    addRowButton.addEventListener('click', addRow);
});