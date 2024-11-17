// JavaScript
document.addEventListener("DOMContentLoaded", function() {
    // Example: Add functionality for handling form submission
    const form = document.getElementById("contact-form");
    form.addEventListener("submit", function(event) {
        event.preventDefault();
        alert("تم إرسال رسالتك!");
    });
});
