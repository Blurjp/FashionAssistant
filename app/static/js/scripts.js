$(document).ready(function () {

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
    formData.append("portrait", file);

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
        window.location.href = indexUrl;
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

  $("#signup-form").submit(function(event) {
    event.preventDefault();
    let username = $("#signup-username").val();
    let email = $("#signup-email").val();
    let password = $("#signup-password").val();

    if (email.trim() === "" || password.trim() === "") {
      return;
    }

    $.ajax({
      //url: "{{ url_for('signup') }}",
      url: signupUrl,
      method: "POST",
      data: JSON.stringify({ "username": username, "email": email, "password": password }),
      contentType: "application/json",
      dataType: "json"
    }).done(function (data) {
      if (data.success) {
        //window.location.href = "{{ url_for('routes.index') }}";
        window.location.href = indexUrl;
      } else {
        //alert(data.message);
      }
    });
  });


  // Handle profile form submission
  $("#profile-form").submit(e => handleProfileFormSubmission(e));

  function handleProfileFormSubmission(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    uploadProfileImage(formData);
  }

  let cropper; // Cropper instance

  $("#profile-form").submit(e => handleProfileFormSubmission(e));

  function handleProfileFormSubmission(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    uploadProfileImage(formData);
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
          // Fetch a fresh presigned URL after a successful upload
          $.ajax({
            url: '/get-presigned-url', // Endpoint to generate presigned URL
            type: "GET",
            success: function(presignedData) {
              if (presignedData && presignedData.success) {
                // Update the profile image URL with the new presigned URL
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
      error: handleUploadError
    });
  }


  function initCropper(data) {
    // Load the uploaded image into the cropping interface
    $("#crop-image").attr("src", data.image_local_url);

    // Display the cropping section
    $("#image-cropping-section").css("display", "block");  // This line makes the cropping section visible

    // Initialize Cropper.js on the image
    cropper = new Cropper($("#crop-image")[0], {
      aspectRatio: 1, // Adjust as needed
    });

    $("#confirm-crop").on("click", function() {
      // Get cropped image data
      const croppedImage = cropper.getCroppedCanvas().toDataURL();
      // Send cropped image back to the server, or proceed as needed
      finalizeUpload(croppedImage);
    });
  }

  function finalizeUpload(croppedImage) {
    // Send the cropped image to the server for final processing/storage
    // This could involve another AJAX request, using the croppedImage data
    // Or you could also just send the cropping coordinates and let the server do the cropping
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
  }

  $.ajax({
    url: url,
    type: 'GET',
    success: function(data) {
      if (data && data.url) { // Assuming the returned data has a 'url' property when successful
        callback(true);
      } else {
        console.error("URL not found in the response.");
        callback(false);
      }
    },
    error: function(jqXHR) {
      if (jqXHR.status === 403) {
        // If HTTP 403 Forbidden, then the presigned URL is likely expired
        callback(false);
      } else {
        console.error("Other error fetching the profile image.");
        callback(false); // Treat any other error as a success to avoid unnecessary calls
      }
    }
  });
}

// Function to fetch a new presigned URL for the profile image.
function fetchNewPresignedUrl(callback) {
  //alert('fetchNewPresignedUrl');
  $.ajax({
    url: '/get-presigned-url', // Endpoint to generate presigned URL
    type: "GET",
    success: function (data) {
      //alert(data.presigned_url);
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