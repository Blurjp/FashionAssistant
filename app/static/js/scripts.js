$(document).ready(function () {
  
  $(".clothes-item").hover(
      function() { // Mouse over
        $(this).find('.carousel').carousel({
          interval: 2000
        }).carousel('cycle');
      },
      function() { // Mouse out
        $(this).find('.carousel').carousel('pause');
      }
    );

    document.getElementById('google-login-button').addEventListener('click', function () {
        window.location.href = '/google_login';
    });

  $(".chat-button").click(function(e) {
    e.preventDefault();
    if (isUserAuthenticated) {
      // User is authenticated, open the chat box
      //alert("isUserAuthenticated");
      $(".chat-box").show();
    } else {
      //alert("not isUserAuthenticated");
      // User is not authenticated, open the signup modal
      $("#login-modal").show();
    }
  });

  $(".login-link").click(function(e) {
    e.preventDefault();
    $("#login-modal").show();
    $("#signup-modal").hide();
    $(".search-results").hide();
    $("#chat-box").hide();
  });

  $(".signup-link").click(function(e) {
    e.preventDefault();
    $("#signup-modal").show();
    $("#login-modal").hide();
    $(".search-results").hide();
    $("#chat-box").hide();
  });

  // Show the profile modal
  $(".profile-link").click(function(e) {
    e.preventDefault();
    openProfileModal();
  });

  // Close the profile modal when the close button is clicked
  $(".modal-content .close").click(function() {
    closeProfileModal();
  });

  if(hasUploadedProfileImage!="none") {
    $('.tagline').hide();
    $('#websiteImage').hide();
    $('.upload-portrait-btn').hide();
    $('.clothes-grid').addClass('active');
  }

  $(".upload-portrait-btn").click(function(e) {
    e.preventDefault();
    if (isUserAuthenticated) {
      $("#portrait-file").click();
      console.log("portrait-file click")
    } else {
      // If the user is not authenticated, show the login modal to prompt login
      $("#login-modal").show();
    }
  });

  $("#portrait-file").change(function() {
    const file = this.files[0];
    if (!file) {
      return;
    }

    const formData = new FormData();
    formData.append("profile-image", file);

    // Send the file data to the server using an AJAX request
    $.ajax({
      url: fileUploadUrl,
      method: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function(response) {
        // Handle the server response, if needed
        console.log("Upload successful:", response);
        // You can show a success message or trigger further actions based on the server response
        showUploadSuccessMessage();
      },
      error: function(xhr, status, error) {
        // Handle errors, if any
        console.error("Error uploading file:", error);
      }
    });
  });

  $("#signup-modal .close").click(function(e) {
    e.preventDefault();
    $(this).closest("#signup-modal").hide();
  });

  $("#login-modal .close").click(function(e) {
    e.preventDefault();
    $(this).closest("#login-modal").hide();
  });

  $("#login-form").submit(function(event) {
    event.preventDefault();
    let email = $("#login-email").val();
    let password = $("#login-password").val();

    if (email.trim() === "" || password.trim() === "") {
      return;
    }

    $.ajax({
      url: loginUrl,
      method: "POST",
      data: JSON.stringify({ "email": email, "password": password }),
      contentType: "application/json",
      dataType: "json"
    }).done(function(data) {
      if (data.success) {
          // Redirect to the clothes page after successful login
          window.location.href = data.redirect_url;
      } else {
        $("#login-error-message").text(data.message);
      }
    }).fail(function(jqXHR, textStatus, errorThrown) {
      console.log("jqXHR:", jqXHR);
      console.log("textStatus:", textStatus);
      console.log("errorThrown:", errorThrown);
      $("#login-error-message").text("Sorry, an error occurred. Please try again.");
    });
  });

    // Handle signup form submission
    $("#signup-form").submit(function (event) {
        event.preventDefault();

        let username = $("#signup-username").val();
        let email = $("#signup-email").val();
        let password = $("#signup-password").val();

        // Basic form validation
        if (username.trim() === "" || email.trim() === "" || password.trim() === "") {
            $("#signup-error-message").text("Username, email, and password are required.");
            return;
        }

        // Check if signupUrl is defined
        if (typeof signupUrl === "undefined") {
            console.error("signupUrl is not defined.");
            $("#signup-error-message").text("Signup URL is not defined.");
            return;
        }

        $.ajax({
            url: signupUrl, // Make sure signupUrl is defined
            method: "POST",
            data: JSON.stringify({ "username": username, "email": email, "password": password }),
            contentType: "application/json",
            dataType: "json"
        }).done(function (data) {
            if (data.success) {
                // Redirect to index or clothes page after successful signup
                if (typeof indexUrl !== "undefined") {
                    window.location.href = indexUrl;
                } else {
                    console.error("indexUrl is not defined.");
                    $("#signup-error-message").text("Redirect URL is not defined.");
                }
            } else {
                $("#signup-error-message").text(data.message); // Display error message
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log("jqXHR:", jqXHR);
            console.log("textStatus:", textStatus);
            console.log("errorThrown:", errorThrown);
            $("#signup-error-message").text("Sorry, an error occurred. Please try again.");
        });
    });

    // Function to initialize Google Sign-Up
    function initializeGoogleSignUp(googleClientId) {
        google.accounts.id.initialize({
            client_id: googleClientId,  // Use the fetched Google Client ID
            callback: handleGoogleSignup,  // Handle the sign-in response
        });

        alert(googleClientId);

        google.accounts.id.renderButton(
            document.getElementById("google-signup-btn"),  // The container for the Google Sign-In button
            { theme: "outline", size: "large" }  // Customize the button's appearance
        );
    }

    // Handle Google Sign-Up response
    // Handle Google Sign-Up response
    function handleGoogleSignup(response) {
        console.log("Google sign-up token:", response.credential);

        // Send the token to the backend for verification and login
        fetch("/verify-token", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ token: response.credential }),  // Send the JWT token to the backend
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Redirect the user on successful signup
                    window.location.href = data.redirect_url;
                } else {
                    alert(data.message);  // Display any errors
                }
            })
            .catch(err => {
                console.error("Error during token verification:", err);
            });
    }

    document.getElementById("google-signup-btn").onclick = function () {
        // Fetch the Google Client ID from the Flask backend
        fetch("/get-google-client-id")
            .then(response => response.json())
            .then(data => {
                if (data.google_client_id) {
                    // Initialize Google Sign-Up with the fetched client ID
                    initializeGoogleSignUp(data.google_client_id);
                } else {
                    console.error("Failed to get Google Client ID");
                }
            })
            .catch(error => {
                console.error("Error fetching Google Client ID:", error);
            });
    };



  // Handle profile form submission
  $("#profile-form").submit(e => handleProfileFormSubmission(e));

  function handleProfileFormSubmission(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    uploadProfileImage(formData);
  }

  function handleProfileFormSubmission(e) {
      e.preventDefault();

      if (cropper) {
          // Get the cropped image as a Blob
          cropper.getCroppedCanvas().toBlob(function (blob) {
              // Create a new FormData object
              const formData = new FormData();

              // Append the cropped image Blob to the FormData object
              formData.append('profile-image', blob, 'profile-image.png');

              // Show the spinner
              const spinner = document.getElementById('spinner');
              spinner.style.display = 'block';

              // Upload the profile image
              uploadProfileImage(formData);
          });
      } else {

          const formData = new FormData(e.target);
          //uploadProfileImage(formData);
          // Show the spinner
          const spinner = document.getElementById('spinner');
          spinner.style.display = 'block';
          //alert('block')

          uploadProfileImage(formData, () => {
          });
      }
  }

  function uploadProfileImage(formData) {
    $.ajax({
      url: fileUploadUrl,
      type: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function(data) {
          if (data && data.image_url) {
            if (cropper) {
              cropper.destroy();
              cropper = null; // Reset the cropper instance
            }

           // Update the previewed section with the new uploaded image URL
           $("#profile_image_url").attr("src", data.image_url);

          // Fetch a fresh presigned URL after a successful upload
          $.ajax({
            url: '/get-presigned-url', // Endpoint to generate presigned URL
            type: "GET",
            success: function(presignedData) {
              if (presignedData && presignedData.success) {
                // Update the profile image URL with the new presigned URL
                  //alert('profile_image_url ' + presignedData.presigned_url);
                  $("#profile_image_url").attr("src", presignedData.presigned_url);
              } else {
                // Handle any issues with fetching the presigned URL
                $("#profile-error-message").text("There was an issue fetching the presigned URL.");
              }
            },
            error: handleUploadError
          });
        } else {
          // Handle the case where the image URL might be missing in the response
          $("#profile-error-message").text("There was an issue updating the profile image.");
        }
      },
      error: handleUploadError,
      complete: function () {
          // Call the callback function once the AJAX call is complete
          const spinner = document.getElementById('spinner');
          spinner.style.display = 'none';
        }
    });
  }

  function handleUploadError(xhr, status, error) {
    displayMessage("Error uploading profile image");
  }

  function displayMessage(message) {
    $("#profile-error-message").text(message);
  }

  $("#chat-form").submit(function (event) {
    event.preventDefault();
    let message = $("#chat-input").val();

    if (message.trim() === "") {
      return;
    }

    addMessageToChat("User", message);
    $("#chat-input").val("");

    $.ajax({
      url: processChatUrl,
      method: "POST",
      data: JSON.stringify({ "message": message }),
      contentType: "application/json",
      dataType: "json"
    }).done(function (data) {
      addMessageToChat("Assistant", data.chatgpt_response);
      updateSearchResults(data.search_results);

      // Hide the "Let's Chat Now" button when chat box is shown
      $(".chat-button").hide();
    }).fail(function () {
      addMessageToChat("Assistant", "Sorry, I couldn't process your message. Please try again.");
    });
  });
});

function addMessageToChat(sender, message) {
  let chatMessages = $("#chat-messages");
  let messageElem = $("<div>").text(sender + ": " + message);
  chatMessages.append(messageElem);
  chatMessages.scrollTop(chatMessages[0].scrollHeight);
}

function updateSearchResults(searchResults) {
  let searchResultsElem = $(".search-results");
  searchResultsElem.empty();
  if (!searchResultsElem.is(":visible")) {
    searchResultsElem.show();
  }

  for (let i = 0; i < searchResults.length; i++) {
    let result = searchResults[i];
    let resultElem = $("<div>").addClass("search-result");
    let resultImg = $("<img>").attr("src", result.image_url).attr("alt", result.title).attr("width", "100%");
    let resultTitle = $("<a>").attr("href", result.link).attr("target", "_blank").text(result.title);
    let resultSnippet = $("<p>").addClass("snippet").text(result.snippet);

    resultElem.append(resultImg, resultTitle, resultSnippet);
    searchResultsElem.append(resultElem);
  }
}



function openSignupPopup() {
  window.open('/signup', 'Signup', 'height=500,width=500');
}

// After the image is successfully uploaded, show the success message
function showUploadSuccessMessage() {
  const uploadSuccessDiv = document.querySelector('.upload-success');
  uploadSuccessDiv.style.display = 'block';

  // Hide the message after a few seconds
  setTimeout(() => {
    uploadSuccessDiv.style.display = 'none';
  }, 5000); // Hide after 5 seconds (adjust the time as needed)
}

// Function to show the profile modal
function openProfileModal() {
  // Try to fetch the profile image
  fetchProfileImage(profileImageUrl, function(success) {
    if (!success) {
      // If fetching failed, get a new presigned URL
      fetchNewPresignedUrl(function(newUrl) {
        profileImageUrl = newUrl;
        //alert(profileImageUrl);
        showProfileModalWithImage(newUrl);
      });
    } else {
      showProfileModalWithImage(profileImageUrl);
    }
  });
}

// Try to fetch the profile image and call the callback with a success flag
function fetchProfileImage(url, callback) {
    if (!url) {
        console.error("URL is null or undefined.");
        callback(false);
        return;
    } else {
        console.log("Fetching image from URL:", url);
    }

    $.ajax({
        url: url,
        type: 'GET',
        success: function (data) {
            callback(true); // If the request is successful, assume the image exists
        },
        error: function (jqXHR) {
            console.log("Profile Image URL:", url);
            if (jqXHR.status === 404) {
                console.error("Error fetching the profile image: 404 Not Found. The URL may be incorrect or the file may not exist.");
            } else if (jqXHR.status === 403) {
                console.warn("HTTP 403 Forbidden: The presigned URL may have expired.");
            } else {
                console.error(`Other error fetching the profile image: Status ${jqXHR.status}, Status Text: ${jqXHR.statusText}`);
            }
            callback(false); // Handle as a failure
        }
    });
}


// Function to fetch a new presigned URL for the profile image.
function fetchNewPresignedUrl(callback) {
  $.ajax({
    url: '/get-presigned-url', // Endpoint to generate presigned URL
    type: "GET",
    success: function (data) {
      if (data && data.presigned_url) {
        callback(data.presigned_url);
      } else {
        console.error("Failed to get a new presigned URL.");
      }
    },
    error: function() {
      console.error("Error fetching the presigned URL.");
    }
  });
}

// Function to actually display the modal with the profile image.
function showProfileModalWithImage(url) {
  var profileImage = document.getElementById("profile_image_url");
  profileImage.src = url;
  $("#profile-modal").show();
  $(".modal-content").addClass("show"); // Add this class to show the modal content
}

function closeProfileModal() {
  $("#profile-modal").hide();
  $(".modal-content").removeClass("show"); // Remove the class to hide the modal content
}

let cropper;
function previewImage(event) {
    const input = event.target;
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = document.getElementById('profile_image_url');
            img.src = e.target.result;

            // Destroy the previous cropper instance, if any
            if (cropper) {
                cropper.destroy();
            }

            // Initialize Cropper.js
            cropper = new Cropper(img, {
                aspectRatio: 1, // Keep aspect ratio 1:1 for profile images
                viewMode: 2,    // Restrict the crop box to stay within the bounds of the canvas
                scalable: true, // Enable scaling
                zoomable: true, // Enable zooming
                movable: true   // Enable moving
            });
        }
        reader.readAsDataURL(file);
    }
}

function cropImage() {
    if (cropper) {
        // Get the cropped image data URL
        const canvas = cropper.getCroppedCanvas();
        const croppedImageURL = canvas.toDataURL();

        // Set the cropped image as the src of the profile image element
        const img = document.getElementById('profile_image_url');
        img.src = croppedImageURL;

        // Optional: You can also display the cropped image in a canvas element
        const croppedCanvas = document.getElementById('cropped_image_canvas');
        croppedCanvas.style.display = 'block';
        const context = croppedCanvas.getContext('2d');
        context.clearRect(0, 0, croppedCanvas.width, croppedCanvas.height);
        croppedCanvas.width = canvas.width;
        croppedCanvas.height = canvas.height;
        context.drawImage(canvas, 0, 0);
    }
}

document.addEventListener("DOMContentLoaded", function() {
  const tryonLinks = document.querySelectorAll('.tryon-hover-bar');
  const spinner = document.getElementById('spinner');
  tryonLinks.forEach(link => {
    link.addEventListener('click', function (event) {
      event.preventDefault();

      // Retrieve the data attributes from the image
        const cloth_id = this.getAttribute('data-clothes-id'); // Get the cloth ID
        const cloth_image_link = this.getAttribute('data-clothes-link');

        console.log('Clicked on:', cloth_id, cloth_image_link);

      // Show the loading bar
        spinner.style.display = 'block';

      // AJAX request to send the image information to the image processing service
      fetch(imageProcessUrl, {
        method: 'POST', headers: {
          'Content-Type': 'application/json'
        }, body: JSON.stringify({
            cloth_id: cloth_id, cloth_image_link: cloth_image_link
          // Add other data as required
        })
      })
          .then(response => {
            if (!response.ok) {  // Check if response status code is not in the 200-299 range
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(data => {
            // Hide the loading bar
              spinner.style.display = 'none';

            // Show the processed image in a popup
            const popupImage = document.querySelector('#processed-image');
            popupImage.src = data.final_image_url;

            // Show the popup overlay
            const popupOverlay = document.querySelector('.popup-overlay');
            popupOverlay.style.display = 'flex'; // Change to 'flex' to make it visible
          })
          .catch(error => {
            console.error('Error:', error);
            // Hide the loading bar
              spinner.style.display = 'none';
            // Provide feedback to the user
            const feedbackDiv = document.querySelector('#feedback');
            feedbackDiv.textContent = 'An error occurred while processing the image. Please try again later.';
            feedbackDiv.style.display = 'block';
          });
    });

      // Add event listener for the close button within the popup
      const closeButton = document.querySelector('.close-button');
      if (closeButton) {
          closeButton.addEventListener('click', function () {
              const popupOverlay = document.querySelector('.popup-overlay');
              popupOverlay.style.display = 'none'; // Hide the popup
          });
      }
  });
});

