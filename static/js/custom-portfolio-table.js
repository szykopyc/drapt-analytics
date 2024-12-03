document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('customPortfolioTable');
    const addRowButton = document.getElementById('addRow');
    const submitPortfolioButton = document.getElementById('submitPortfolio');
    const weightSumElement = document.getElementById('weightSum');
    const portfolioName = document.getElementById('PortfolioName');

    // Function to calculate and update the weight sum
    function updateWeightSum() {
        let totalWeight = 0;
        const weightInputs = tableBody.querySelectorAll('input[name="allocationWeight"]');
        weightInputs.forEach(input => {
            const weight = parseFloat(input.value) || 0; // Default to 0 if input is empty or invalid
            totalWeight += weight;
        });
        weightSumElement.textContent = `(Sum: ${totalWeight.toFixed(2)})`;
    }

    // Function to add a new row
    function addRow() {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td><input type="text" name="ticker" placeholder="Ticker"></td>
            <td><input type="number" name="allocationWeight" placeholder="Weight" step="0.01" min="0"></td>
            <td><button type="button" class="deleteRow">Delete</button></td>
        `;
        tableBody.appendChild(newRow);

        // Attach event listener to the new weight input
        const weightInput = newRow.querySelector('input[name="allocationWeight"]');
        weightInput.addEventListener('input', updateWeightSum);

        // Attach event listener to the delete button
        const deleteButton = newRow.querySelector('.deleteRow');
        deleteButton.addEventListener('click', function () {
            newRow.remove();
            updateWeightSum();
            ensureMinimumRows(); // Ensure minimum rows after deletion
        });

        // Update weight sum
        updateWeightSum();
    }

    // Ensure at least two rows exist
    function ensureMinimumRows() {
        while (tableBody.rows.length < 2) {
            addRow();
        }
    }

    // Validate the portfolio before submission
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

        if (Math.abs(totalWeight - 1) > 0.01) { // Allow a small margin for floating-point errors
            alert('The total weight must add up to 1.');
            return false;
        }

        return true;
    }

    submitPortfolioButton.addEventListener('click', function () {
        if (validatePortfolio()) {
            // If valid, create the payload and submit via fetch
            const portfolio = [];
            const rows = tableBody.querySelectorAll('tr');
            const portfolioNameValue = portfolioName.value.trim(); // Get and trim portfolio name
    
            // Ensure portfolio name is provided
            if (!portfolioNameValue) {
                alert('Please provide a name for the portfolio.');
                return;
            }
    
            rows.forEach(row => {
                const ticker = row.querySelector('input[name="ticker"]').value;
                const weight = parseFloat(row.querySelector('input[name="allocationWeight"]').value);
                portfolio.push({ ticker, weight });
            });
    
            // Submit the portfolio using fetch
            fetch('/create-portfolio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    portfolioName: portfolioNameValue, // Include portfolio name
                    portfolio, 
                }),
            })
            .then(response => {
                console.log('Response:', response);
                if (response.ok) {
                    // If the response is successful, we should check for JSON or redirect
                    return response.json().catch(() => {
                        // If response is not JSON, log and handle the redirect or HTML
                        console.error('Response is not JSON. Handling redirect.');
                        window.location.href = '/risk';  // Manually handle redirect
                        throw new Error('Redirecting to risk page');
                    });
                } else {
                    // Handle errors like 404, 500, etc.
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
            })
            .then(data => {
                // If response was JSON, handle it here
                console.log('Portfolio successfully created!', data);
                alert('Your portfolio has been successfully created! Further instructions: Check your risk profile or modify your portfolio as needed.');
                window.location.href = '/risk';  // Redirect to the risk page or another page
            })
            .catch(error => {
                // Log any error and alert the user
                console.error('Error:', error);
                alert('An error occurred while submitting your portfolio. Please try again.');
            });
        }
    });
    
    // Add initial rows and attach event listener to "Add Row" button
    ensureMinimumRows();
    addRowButton.addEventListener('click', addRow);
});