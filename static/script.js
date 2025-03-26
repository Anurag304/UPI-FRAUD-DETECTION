document.addEventListener("DOMContentLoaded", function() {
    let steps = document.querySelectorAll(".step");
    let index = 0;

    function highlightNextStep() {
        steps.forEach(step => step.classList.remove("highlight")); // Remove highlight from all
        steps[index].classList.add("highlight"); // Apply highlight to the current step

        index = (index + 1) % steps.length; // Cycle through 0 → 1 → 2 → 0
    }

    setInterval(highlightNextStep, 2000);

    // Redirect to Login Page
    document.getElementById("loginBtn").addEventListener("click", function() {
        window.location.href = "/login";
    });

    // Redirect to Register Page
    document.getElementById("registerBtn").addEventListener("click", function() {
        window.location.href = "/register";
    });
});
