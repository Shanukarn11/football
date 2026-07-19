document.addEventListener("DOMContentLoaded", function () {
  function toggleReadMore(button) {
    const testimonialText = button.parentElement;
    const shortText = testimonialText.querySelector(".short-text");
    const fullText = testimonialText.querySelector(".full-text");
    const readMoreBtn = testimonialText.querySelector(".read-more-btn");
    const readLessBtn = testimonialText.querySelector(".read-less-btn");

    if (shortText.style.display === "none") {
      shortText.style.display = "block";
      fullText.style.display = "none";
      readMoreBtn.style.display = "inline-block";
      readLessBtn.style.display = "none";
    } else {
      shortText.style.display = "none";
      fullText.style.display = "block";
      readMoreBtn.style.display = "none";
      readLessBtn.style.display = "inline-block";
    }
  }

  // Attach event listeners to the buttons
  const readMoreButtons = document.querySelectorAll(".read-more-btn");
  readMoreButtons.forEach((button) => {
    button.addEventListener("click", function () {
      toggleReadMore(this);
    });
  });

  const readLessButtons = document.querySelectorAll(".read-less-btn");
  readLessButtons.forEach((button) => {
    button.addEventListener("click", function () {
      toggleReadMore(this);
    });
  });
});
