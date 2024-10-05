// Initialize Google Sign-Up
function initializeGoogleSignUp() {
    alert(googleClientId);
    google.accounts.id.initialize({
        client_id: googleClientId,  // Ensure googleClientId is defined
        callback: handleGoogleSignup
    });

    google.accounts.id.renderButton(
        document.getElementById("google-signup-btn"), // Button where Google signup will appear
        { theme: "outline", size: "large" }  // Customize button appearance
    );
}

// Handle Google sign-up response
function handleGoogleSignup(response) {
    // Send the token received from Google to the backend for validation
    $.ajax({
        url: googleSignupUrl, // Make sure googleSignupUrl is defined (API route for Google signup)
        method: "POST",
        data: JSON.stringify({ token: response.credential }),
        contentType: "application/json",
        dataType: "json"
    }).done(function (data) {
        if (data.success) {
            // Redirect to the clothes page after successful Google sign-up
            window.location.href = data.redirect_url;
        } else {
            $("#signup-error-message").text(data.message); // Display error message
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        console.log("jqXHR:", jqXHR);
        console.log("textStatus:", textStatus);
        console.log("errorThrown:", errorThrown);
        $("#signup-error-message").text("Sorry, an error occurred with Google signup. Please try again.");
    });
}
