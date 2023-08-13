// document.addEventListener('DOMContentLoaded', function () {
//         const forms = document.querySelectorAll(".forms");

//         forms.forEach(form => {
//             const pwShowHide = form.querySelectorAll(".eye-icon");
            
//             pwShowHide.forEach(eyeIcon => {
//                 eyeIcon.addEventListener("click", () => {
//                     let pwFields = eyeIcon.parentElement.parentElement.querySelectorAll(".password");
                    
//                     pwFields.forEach(password => {
//                         if(password.type === "password"){
//                             password.type = "text";
//                             eyeIcon.classList.replace("bx-hide", "bx-show");
//                         } else {
//                             password.type = "password";
//                             eyeIcon.classList.replace("bx-show", "bx-hide");
//                         }
//                     });
//                 });
//             });

//             const fields = form.querySelectorAll('.input-field input');
//             fields.forEach(field => {
//                 field.addEventListener('input', () => {
//                     const validationMessage = field.nextElementSibling;

//                     if (field.value.trim() === '') {
//                         showErrorMessage(validationMessage, 'This field is required.');
//                     } else {
//                         hideErrorMessage(validationMessage);
//                     }

//                     if (field.type === 'email' && !validateEmail(field.value.trim())) {
//                         showErrorMessage(validationMessage, 'Please enter a valid email address.');
//                     }

//                     if (field.type === 'password' && !validatePassword(field.value)) {
//                         showErrorMessage(validationMessage, 'Enter 8 character and 1 symbol');
//                     }
//                     if (field === confirmPasswordInput) {
//                         if (field.value !== passwordInput.value) {
//                             showErrorMessage(validationMessage, 'Passwords do not match.');
//                         } else {
//                             hideErrorMessage(validationMessage);
//                         }
//                     }
//                 });
//             });
//         });

//         function showErrorMessage(element, message) {
//             element.textContent = message;
//             element.style.display = 'block';
//         }

//         function hideErrorMessage(element) {
//             element.textContent = '';
//             element.style.display = 'none';
//         }

//         function validateEmail(email) {
//             const emailPattern = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
//             return emailPattern.test(email);
//         }

//         function validatePassword(password) {
//             const passwordPattern = /^(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,}$/;
//             return passwordPattern.test(password);
//         }
//     });