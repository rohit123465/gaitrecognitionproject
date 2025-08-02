document.addEventListener("DOMContentLoaded", function () {
    const downloadBtn = document.getElementById("downloadVideoBtn");
    const downloadGaitAnimationBtn = document.getElementById("downloadAnimationBtn");
    if (downloadBtn) {
        downloadBtn.addEventListener("click", function () {
            const videoUrl = "https://drive.google.com/uc?export=download&id=1AiB0ugpPvz_g8WTS09pdg4LHcdu-v10x"; 

            // Create an anchor element to trigger download
            const a = document.createElement("a");
            a.href = videoUrl;
            a.download = "Gait_Visualization.mp4"; // File name when downloaded

            // Temporarily add the anchor to the body, trigger click, then remove
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    } else {
        console.log("Download button not found");
    }

    if (downloadGaitAnimationBtn) {
        downloadGaitAnimationBtn.addEventListener("click", function () {
            const animationUrl = "https://drive.google.com/uc?export=download&id=19SuWjstLLZPxUOhDeB8539owvGrpISG7";

            const a = document.createElement("a");
            a.href = animationUrl;
            a.download = "Gait_Animation.mp4"; // File name when downloaded

            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    } else {
        console.log("Download button for gait animation not found");
    } 
});

// JavaScript code to fetch and display identification results
document.addEventListener("DOMContentLoaded", function () {
    // Fetch the human identification results from the backend
    fetch('/get_identification_results')
        .then(response => response.json())
        .then(data => {
            const metricsContainer = document.getElementById("metrics");
            metricsContainer.innerHTML = `<p><strong>Human Identification Result:</strong> ${data.identification}</p>`;
        })
        .catch(error => {
            console.error("Error fetching identification result:", error);
        });
});




// Example function to load performance metrics
function loadPerformanceMetrics() {
    const metricsContainer = document.getElementById("metrics");
    metricsContainer.innerHTML = "<p>Loading performance metrics...</p>";

    const metricsData = `
        <p><strong>Accuracy:</strong> 92%</p>
        <p><strong>Precision:</strong> 90%</p>
        <p><strong>Recall:</strong> 89%</p>
    `;
    metricsContainer.innerHTML = metricsData;
}


document.addEventListener("DOMContentLoaded", function() {
    //loadGait3DModel();
    //loadGaitAnalysisGraph();
    loadPerformanceMetrics();
});
