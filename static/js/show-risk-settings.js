document.addEventListener('DOMContentLoaded', function () {
    // Get the portfolio selector and element-form-settings div
    const portfolioSelector = document.getElementById('portfolio-selector');
    const elementFormSettings = document.getElementById('element-form-settings');
    const analyseButton = document.getElementById('analyse-button');

    // Ensure all elements are available before manipulating them
    if (portfolioSelector && elementFormSettings && analyseButton) {
        // Hide the element-form-settings by default
        elementFormSettings.style.display = 'none';

        // Add event listener to portfolio selector
        portfolioSelector.addEventListener('change', function() {
            // Check if the selected portfolio is the custom portfolio option
            if (portfolioSelector.value === 'custom_portfolio') {
                // Hide the settings if custom portfolio is selected
                elementFormSettings.style.display = 'none';
                analyseButton.value = "Create"; // Update the button text to 'Create'
            } else {
                // Show the settings for other portfolio selections
                elementFormSettings.style.display = 'flex';
                analyseButton.value = "Analyse"; // Revert the button text to 'Analyse'
            }
        });
    } else {
        console.error('One or more elements are missing.');
    }
});