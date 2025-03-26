document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll(".input-field");
    const passwordInput = document.querySelector("#password");
    const togglePassword = document.querySelector("#togglePassword");

    inputs.forEach((input) => {
        input.addEventListener("focus", function () {
            this.parentElement.classList.add("focused");
        });

        input.addEventListener("blur", function () {
            if (!this.value) {
                this.parentElement.classList.remove("focused");
            }
        });
    });

    togglePassword.addEventListener("click", function () {
        const eyeIcon = togglePassword.querySelector("i");
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            eyeIcon.classList.remove("fa-eye");
            eyeIcon.classList.add("fa-eye-slash");
        } else {
            passwordInput.type = "password";
            eyeIcon.classList.remove("fa-eye-slash");
            eyeIcon.classList.add("fa-eye");
        }
    });

    const registerForm = document.querySelector("form");

    registerForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(this);
        fetch(this.action, {
            method: "POST",
            body: formData,
        })
        .then(response => response.text())
        .then(data => {
            if (data.includes("successful")) {
                alert("Registration Successful! Redirecting to login...");
                window.location.href = "/login";
            } else {
                alert("Registration failed! Username or Email may already exist.");
            }
        })
        .catch(error => console.error("Error:", error));
    });
});
