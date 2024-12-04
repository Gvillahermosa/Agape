document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('container');
    const registerBtn = document.getElementById('register');
    const loginBtn = document.getElementById('login');

    // Check the data-show-signup attribute
    const showSignup = container.getAttribute('data-show-signup') === 'True';

    if (showSignup) {
        container.classList.add('active');
    } else {
        container.classList.remove('active');
    }

    // Event listeners for toggling forms
    registerBtn.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent default action
        container.classList.add("active");
    });

    loginBtn.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent default action
        container.classList.remove("active");
    });
});