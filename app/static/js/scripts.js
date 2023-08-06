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
        alert(data.message);
      }
    });
  });

  $("#chat-form").submit(function (event) {
    event.preventDefault();
    let message = $("#chat-input").val();

    if (message.trim() === "") {
      return;
    }

    addMessageToChat("User", message);
    $("#chat-input").val("");

    $.ajax({
      //url: "{{ url_for('routes.process_chat') }}",
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
