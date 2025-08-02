// Handle form submission
document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    // Get the form values
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // Prepare the data to be sent to the backend
    const data = {
        username: username,
        password: password
    };

    // Send the data to the Flask backend via a POST request
    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        // Handle the response
        const result = await response.json();

        if (response.status === 200) {
            // Redirect to the home page if login is successful
            window.location.href = result.redirect_url;
        } else {
            // Show error message if login fails
            alert(result.message);
        }
    } catch (error) {
        console.error("Error during login:", error);
        alert("An error occurred. Please try again later.");
    }
});
