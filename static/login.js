document.addEventListener("DOMContentLoaded", function () {
    // Toggle Password Visibility
    document.querySelector(".toggle-password").addEventListener("click", function () {
        const passwordField = document.getElementById("password");
        if (passwordField.type === "password") {
            passwordField.type = "text";
            this.classList.remove("fa-eye");
            this.classList.add("fa-eye-slash");
        } else {
            passwordField.type = "password";
            this.classList.remove("fa-eye-slash");
            this.classList.add("fa-eye");
        }
    });

    // Input Animations
    const inputFields = document.querySelectorAll("input");
    inputFields.forEach((field) => {
        field.addEventListener("focus", function () {
            this.style.boxShadow = "0 0 10px rgba(27, 255, 255, 0.5)";
        });
        field.addEventListener("blur", function () {
            this.style.boxShadow = "none";
        });
    });
});
