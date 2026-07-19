document
  .getElementById("desportz-contact-form")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    var formData = new FormData(event.target);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/ikf-center-of-excellence/desportz", true);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");

    xhr.onload = function () {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        if (response.success) {
          document.getElementById("response-message").innerHTML =
            '<p style="color: green;">' + response.success_message + "</p>";
          document.getElementById("desportz-contact-form").reset();
        } else {
          // Display error message
          document.getElementById("response-message").innerHTML =
            '<p style="color: red;">' + response.error_message + "</p>";

          // Display individual field errors
          if (response.errors) {
            Object.keys(response.errors).forEach(function (key) {
              var errorElement = document.querySelector(`#id_${key} + p`);
              if (errorElement) {
                errorElement.innerHTML = response.errors[key][0];
              }
            });
          }
        }
      } else {
        console.error("Error:", xhr.statusText);
        document.getElementById("response-message").innerHTML =
          '<p style="color: red;">An error occurred. Please try again.</p>';
      }
    };

    xhr.send(formData);
  });
