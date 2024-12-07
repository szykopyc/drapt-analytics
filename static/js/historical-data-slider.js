var slider = document.getElementById("historical-data-range");
var output = document.getElementById("lookback-days");

// Initialize the display
output.innerHTML = (slider.value >= 1 ? parseFloat(slider.value).toFixed(2) + " Years" : slider.value * 365 + " Days");

slider.oninput = function () {
    if (this.value >= 1) {
        // Display as years, always with 2 decimal places
        output.innerHTML = parseFloat(this.value).toFixed(2) + " Years";
    } else {
        // Display as days, rounded to 0 decimal places
        output.innerHTML = (this.value * 365).toFixed(0) + " Days";
    }
};