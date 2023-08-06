// google-signup.js
$(document).ready(function() {
  // Google signup configuration
  google.accounts.id.initialize({
    client_id: 'YOUR_GOOGLE_CLIENT_ID',
    callback: handleGoogleSignup,
  });

  // Handle Google signup button click
  $("#google-signup-btn").click(function(e) {
    e.preventDefault();
    google.accounts.id.prompt();
  });
});

// Handle Google signup callback
function handleGoogleSignup(response) {
  if (response.credential) {
    // User successfully signed up with Google
    let googleCredential = response.credential;
    let username = $("#signup-username").val();
    let email = response.email;

    // Send the signup data to the server
    $.ajax({
      url: "{{ url_for('routes.signup') }}",
      method: "POST",
      data: JSON.stringify({
        username: username,
        email: email,
        google_credential: googleCredential,
      }),
      contentType: "application/json",
      dataType: "json"
    }).done(function(data) {
      if (data.success) {
        window.location.href = "{{ url_for('routes.index') }}";
      } else {
        alert(data.message);
      }
    }).fail(function() {
      alert("Failed to signup. Please try again.");
    });
  } else {
    // User canceled the Google signup
    console.log("Google signup canceled.");
  }
}
