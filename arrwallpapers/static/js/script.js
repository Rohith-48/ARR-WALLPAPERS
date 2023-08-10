document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll(".forms");
    pwShowHide = document.querySelectorAll(".eye-icon");
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

    forms.forEach(form => {
        const validationMessages = {
            email: form.querySelector(".validation-message#email-validation"),
            password1: form.querySelector(".validation-message#password1-validation"),
            password2: form.querySelector(".validation-message#password2-validation"),
        };

        const fields = [
            { input: form.querySelector(".input[name='email']"), validationFunc: isValidEmail, fieldName: "email" },
            { input: form.querySelector(".password[name='password1']"), validationFunc: isValidPassword, fieldName: "password1" },
        ];

        fields.forEach(field => {
            const input = field.input;
            const messageElement = validationMessages[field.fieldName];

            input.addEventListener("input", () => {
                const isValid = field.validationFunc(input.value);
                updateValidationMessage(messageElement, isValid);
            });
        });

        form.addEventListener("submit", (e) => {
            let isValidForm = true;

            // Validate password match
            const password1 = form.querySelector(".password[name='password1']").value;
            const password2 = form.querySelector(".password[name='password2']").value;
            const passwordMatchMessageElement = validationMessages["password2"];
            const isPasswordMatch = password1 === password2;
            updateValidationMessage(passwordMatchMessageElement, isPasswordMatch);

            if (!isPasswordMatch) {
                isValidForm = false;
            }
            const passwordComplexityMessageElement = validationMessages["password1"];
            const isPasswordComplex = isValidPassword(password1);
            updateValidationMessage(passwordComplexityMessageElement, isPasswordComplex);

            if (!isPasswordComplex) {
                isValidForm = false;
            }

            // Validate other fields
            fields.forEach(field => {
                const input = field.input;
                const messageElement = validationMessages[field.fieldName];
                const isValidField = field.validationFunc(input.value);
                updateValidationMessage(messageElement, isValidField);

                if (!isValidField) {
                    isValidForm = false;
                }
            });

            if (!isValidForm) {
                e.preventDefault();
            }
        });
    });

    function updateValidationMessage(messageElement, isValid) {
        if (isValid) {
            messageElement.textContent = "";
        } else {
            messageElement.textContent = "Invalid input.";
        }
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function isValidPassword(password) {
        return password.length >= 8 &&
               /[A-Z]/.test(password) &&
               /[a-z]/.test(password) &&
               /\d/.test(password) &&
               /[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]/.test(password);
    }
});
