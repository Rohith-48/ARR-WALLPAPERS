document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll(".forms");

    forms.forEach(form => {
        const pwShowHide = form.querySelectorAll(".eye-icon");
        
        pwShowHide.forEach(eyeIcon => {
            eyeIcon.addEventListener("click", () => {
                let pwFields = eyeIcon.parentElement.parentElement.querySelectorAll(".password");
                
                pwFields.forEach(password => {
                    if(password.type === "password"){
                        password.type = "text";
                        eyeIcon.classList.replace("bx-hide", "bx-show");
                    } else {
                        password.type = "password";
                        eyeIcon.classList.replace("bx-show", "bx-hide");
                    }
                });
            });
        });

        const fields = form.querySelectorAll('.input-field input');
        fields.forEach(field => {
            field.addEventListener('input', () => {
                const validationMessage = field.nextElementSibling;

                if (field.value.trim() === '') {
                    showErrorMessage(validationMessage, 'This field is required.');
                } else {
                    hideErrorMessage(validationMessage);
                }

                if (field.type === 'email' && !validateEmail(field.value.trim())) {
                    showErrorMessage(validationMessage, 'Please enter a valid email address.');
                }

        
                
            });
        });

        // Password strength validation
        const passwordInput = form.querySelector(".password");
        const confirmPasswordInput = form.querySelector("#password2"); // Get the confirmation password input
        const passwordStrengthMessage = form.querySelector("#password-strength-message");
        const letter = form.querySelector("#letter");
        const capital = form.querySelector("#capital");
        const number = form.querySelector("#number");
        const length = form.querySelector("#length");
        const passwordMatchMessage = document.createElement("span"); // Create a new span element
        passwordMatchMessage.classList.add("password-match-message"); // Add appropriate class
        passwordMatchMessage.style.display = 'none'; // Initially hide the message
        form.appendChild(passwordMatchMessage); // Append the message to the form

        passwordInput.addEventListener("input", function () {
            const password = passwordInput.value;

            // Validate lowercase letters
            letter.classList.toggle("valid", /[a-z]/.test(password));
            letter.classList.toggle("invalid", !/[a-z]/.test(password));

            // Validate capital letters
            capital.classList.toggle("valid", /[A-Z]/.test(password));
            capital.classList.toggle("invalid", !/[A-Z]/.test(password));

            // Validate numbers
            number.classList.toggle("valid", /[0-9]/.test(password));
            number.classList.toggle("invalid", !/[0-9]/.test(password));

            // Validate length
            length.classList.toggle("valid", password.length >= 8);
            length.classList.toggle("invalid", password.length < 8);

            // Show password strength message
            if (/[a-z]/.test(password) && /[A-Z]/.test(password) && /[0-9]/.test(password) && password.length >= 8) {
                passwordStrengthMessage.textContent = "Strong password";
                passwordStrengthMessage.style.color = "#2ecc71";
            } else {
                passwordStrengthMessage.textContent = "Password should contain lowercase and uppercase letters, numbers, and be at least 8 characters long.";
                passwordStrengthMessage.style.color = "#e74c3c";
            }
        });

    });
    function showErrorMessage(element, message) {
        element.textContent = message;
        element.style.display = 'block';
    }

    function hideErrorMessage(element) {
        element.textContent = '';
        element.style.display = 'none';
    }

    function validateEmail(email) {
        const emailPattern = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
        return emailPattern.test(email);
    }

    function validatePassword(password) {
        const passwordPattern = /^(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,}$/;
        return passwordPattern.test(password);
    }

    function passwordValidate() {
        const pass = document.getElementById("password").value;
        const re = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
        if (!re.test(pass)) {
            document.getElementById("pass-error").textContent =
                "Minimum eight characters, at least one letter, one number and one special character";
        } else {
            document.getElementById("pass-error").textContent = "";
        }
    }
})