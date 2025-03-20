document.addEventListener("DOMContentLoaded", function() {
  const indicatorSelect = document.getElementById("indicator");
  const chartBox = document.getElementById("chart-box");
  const resetButton = document.getElementById("resetButton");

  // Helper function to draw the chart
  function drawChart(indicator) {
    // Clear the chart container
    chartBox.innerHTML = "";
    
    // For demonstration, we are using sample data.
    // Replace this with your actual technical analysis data and logic.
    const sampleData = [
      {x: "Jan", value: 100},
      {x: "Feb", value: 120},
      {x: "Mar", value: 90},
      {x: "Apr", value: 140},
      {x: "May", value: 110},
      {x: "Jun", value: 130},
      {x: "Jul", value: 125},
      {x: "Aug", value: 135},
      {x: "Sep", value: 95},
      {x: "Oct", value: 105},
      {x: "Nov", value: 115},
      {x: "Dec", value: 125}
    ];

    // Create a line chart instance using AnyChart
    anychart.onDocumentReady(function() {
      let chart = anychart.line();
      chart.data(sampleData);
      chart.title(indicator + " Chart");
      chart.container(chartBox);
      chart.draw();
    });
  }

  // When the indicator changes, draw the corresponding chart
  indicatorSelect.addEventListener("change", function() {
    const selectedIndicator = indicatorSelect.value;
    console.log("Selected indicator:", selectedIndicator); // Debug log
    if (selectedIndicator === "NONE") {
      chartBox.innerHTML = "";
      return;
    }
    drawChart(selectedIndicator);
  });

  // Reset button clears the chart and resets the dropdown
  resetButton.addEventListener("click", function() {
    indicatorSelect.value = "NONE";
    chartBox.innerHTML = "";
    console.log("Chart reset."); // Debug log
  });
});
