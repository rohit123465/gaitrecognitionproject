document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("uploadForm");
    const videoInput = document.getElementById("videoInput");
    const uploadBtn = document.getElementById("uploadBtn");
    const progressBar = document.getElementById("progressBar");
    const progressContainer = document.querySelector(".progress-container");
    const uploadStatus = document.getElementById("uploadStatus");

    // Enable upload button when a file is selected
    videoInput.addEventListener("change", function () {
        uploadBtn.disabled = !videoInput.files.length;
    });

    uploadForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const file = videoInput.files[0];
        if (!file || file.type !== "video/mp4") {
            alert("Please upload a valid MP4 video file.");
            return;
        }

        const formData = new FormData();
        formData.append("video", file);

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/upload", true);

        // Update progress bar
        xhr.upload.onprogress = function (event) {
            if (event.lengthComputable) {
                const percentComplete = (event.loaded / event.total) * 100;
                progressBar.style.width = percentComplete + "%";
            }
        };

        // Show progress bar
        progressContainer.style.display = "block";

        xhr.onload = function () {
            if (xhr.status === 201) {
                uploadStatus.innerText = "Upload successful!";
                progressBar.style.backgroundColor = "#28a745";
            } else {
                uploadStatus.innerText = "Upload failed. Please try again.";
                progressBar.style.backgroundColor = "red";
            }
        };

        xhr.send(formData);
    });
});
