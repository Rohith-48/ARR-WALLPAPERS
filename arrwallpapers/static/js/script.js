// Function to validate the username
function validateUsername() {
    const usernameInput = document.getElementById("username");
    const usernameValidation = document.getElementById("username-validation");
    
    // Check for white spaces
    if (/\s/.test(usernameInput.value)) {
        usernameValidation.innerHTML = "Username cannot contain spaces.";
        usernameValidation.style.color = "red";
    } else {
        usernameValidation.innerHTML = "";
    }
    
    // Check for special characters
    const specialCharacters = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/;
    if (specialCharacters.test(usernameInput.value)) {
        usernameValidation.innerHTML = "Username cannot contain special characters.";
        usernameValidation.style.color = "red";
    }
}

// Function to validate the email
function validateEmail() {
    const emailInput = document.getElementById("email");
    const emailValidation = document.getElementById("email-validation");
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    
    if (!emailPattern.test(emailInput.value)) {
        emailValidation.innerHTML = "Invalid email address.";
        emailValidation.style.color = "red";
    } else {
        emailValidation.innerHTML = "";
    }
}

// Function to validate the phone number
function validatePhoneNo() {
    const phonenoInput = document.getElementById("phoneno");
    const phonenoValidation = document.getElementById("phoneno-validation");
    const phonenoPattern = /^\d{10}$/;
    
    if (!phonenoPattern.test(phonenoInput.value)) {
        phonenoValidation.innerHTML = "Invalid phone number (10 digits required).";
        phonenoValidation.style.color = "red";
    } else {
        phonenoValidation.innerHTML = "";
    }
}

function validatePassword() {
    const password1Input = document.getElementById("password1");
    const password1Validation = document.getElementById("password1-validation");
    const passwordPattern = /^(?=.*\d)(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    
    if (!passwordPattern.test(password1Input.value)) {
        password1Validation.innerHTML = "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.";
        password1Validation.style.color = "red";
        return false; 
    } else {
        password1Validation.innerHTML = "";
        return true; 
    }
}
function togglePasswordVisibility() {
    const password1Input = document.getElementById("password1");
    const password2Input = document.getElementById("password2");
    const togglePassword = document.getElementById("togglePassword");
    
    if (password1Input.type === "password") {
        password1Input.type = "text";
        password2Input.type = "text";
        togglePassword.classList.remove("bx-hide");
        togglePassword.classList.add("bx-show");
    } else {
        password1Input.type = "password";
        password2Input.type = "password"; 
        togglePassword.classList.remove("bx-show");
        togglePassword.classList.add("bx-hide");
    }
}

function validatePasswordMatch() {
    const password1Input = document.getElementById("password1");
    const password2Input = document.getElementById("password2");
    const password2Validation = document.getElementById("password2-validation");
    const passwordMatchMessage = document.getElementById("password-match-message");
    
    if (password1Input.value !== password2Input.value) {
        password2Validation.innerHTML = "Passwords do not match.";
        password2Validation.style.color = "red";
        passwordMatchMessage.innerHTML = "";
    } else {
        password2Validation.innerHTML = "";
        passwordMatchMessage.innerHTML = "Passwords match.";
        passwordMatchMessage.style.color = "green";
    }
}

function validateFile() {
    const portfolioInput = document.getElementById("portfolio");
    const portfolioValidation = document.getElementById("portfolio-validation");
    const allowedExtensions = /(\.pdf)$/i;
    
    if (!allowedExtensions.exec(portfolioInput.value)) {
        portfolioValidation.innerHTML = "Only PDF files are allowed.";
        portfolioValidation.style.color = "red";
    } else {
        portfolioValidation.innerHTML = "";
    }
}
function validateForm() {
    const usernameInput = document.getElementById("username");
    const emailInput = document.getElementById("email");
    const phonenoInput = document.getElementById("phoneno");
    const password1Input = document.getElementById("password1");
    const password2Input = document.getElementById("password2");
    const portfolioInput = document.getElementById("portfolio");

    // Check all validations and return true if the form is valid, otherwise return false
    const isUsernameValid = !/\s/.test(usernameInput.value) && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/.test(usernameInput.value);
    const isEmailValid = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/.test(emailInput.value);
    const isPhonenoValid = /^\d{10}$/.test(phonenoInput.value);
    const isPasswordValid = validatePassword();
    const isPasswordMatch = password2Input.value === password1Input.value;
    const isPortfolioValid = /(\.pdf)$/i.test(portfolioInput.value);

    if (
        isUsernameValid &&
        isEmailValid &&
        isPhonenoValid &&
        isPasswordValid &&
        isPasswordMatch &&
        isPortfolioValid
    ) {
        return true; 
    } else {
        alert("Registration failed. Please check the form for errors.");
        return false; 
    }
}

const form = document.getElementById("signup-form"); 
form.addEventListener("submit", function (event) {
    if (!validateForm()) {
        event.preventDefault(); 
    }
});