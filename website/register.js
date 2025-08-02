// Enable the submit button when the terms checkbox is checked
document.getElementById("terms").addEventListener("change", function() {
    document.getElementById("submitBtn").disabled = !this.checked;
});

// Handle form submission
document.getElementById("registerForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    console.log("Form submitted");

    // Get the form values
    const name = document.getElementById("name").value;
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // Prepare the data to be sent to the backend
    const data = {
        name: name,
        username: username,
        email: email,
        password: password
    };

    // Log the data to check if it's correct
    console.log("Sending data:", data);

    // Send the data to the Flask backend via a POST request
    try {
        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        // Handle the response
        const result = await response.json();
        
        console.log("Response received:", result);

        if (response.status === 201) {
            // Redirect to the login page if registration is successful
            window.location.href = result.redirect_url;
        } else {
            // Show error message
            alert(result.message);
        }
    } catch (error) {
        console.error("Error during registration:", error);
    }
});
