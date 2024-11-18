document.addEventListener('DOMContentLoaded', function () {

    const togglePassword = document.querySelector('#togglePassword');
    const password = document.querySelector('#password');
    const passwordConfirm = document.querySelector('#password_confirm');
    const new_password1 = document.querySelector('#new_password1');
    const new_password2 = document.querySelector('#new_password2');

    function togglePasswordVisibility(inputField) {
        const type = inputField.getAttribute('type') === 'password' ? 'text' : 'password';
        inputField.setAttribute('type', type);

        if (inputField.getAttribute('type') === 'password') {
            togglePassword.classList.remove('fa-eye-slash');
            togglePassword.classList.add('fa-eye');
        } else {
            togglePassword.classList.remove('fa-eye');
            togglePassword.classList.add('fa-eye-slash');
        }
    }

    togglePassword.addEventListener('click', function (e) {
        togglePasswordVisibility(password);
        togglePasswordVisibility(passwordConfirm);
    });

    togglePassword.addEventListener('click', function (e) {
        togglePasswordVisibility(new_password1);
        togglePasswordVisibility(new_password2);
    });
});