function validateFio() {
    const fioInput = document.querySelector('input[name="fio"]');
    const fioError = document.getElementById('fioError');

    if (fioInput.validity.valid) {
        fioError.style.display = 'none';
        fioInput.classList.remove('invalid-input');
    } else {
        fioError.innerHTML = "ФИО должно содержать минимум 1 пробел";
        fioError.style.display = 'block';
        fioInput.classList.add('invalid-input');
    }
}

function validatePhone() {
    const phoneInput = document.querySelector('input[name="phone"]');
    const phoneError = document.getElementById('phoneError');

    if (phoneInput.validity.valid) {
        phoneError.style.display = 'none';
        phoneInput.classList.remove('invalid-input');
    } else {
        phoneError.innerHTML = "Номер телефона должен начинаться с +7 и содержать еще 10 цифр";
        phoneError.style.display = 'block';
        phoneInput.classList.add('invalid-input');
    }

    checkFields();
}

function validateEmail() {
    const emailInput = document.querySelector('input[name="email"]');
    const emailError = document.getElementById('emailError');

    if (emailInput.validity.valid) {
        emailError.style.display = 'none';
        emailInput.classList.remove('invalid-input');
    } else {
        emailError.innerHTML = "Введите корректный адрес электронной почты";
        emailError.style.display = 'block';
        emailInput.classList.add('invalid-input');
    }

    checkFields();
}

function validateUsername() {
    const usernameInput = document.querySelector('input[name="username"]');
    const usernameError = document.getElementById('usernameError');

    if (usernameInput.validity.valid) {
        usernameError.style.display = 'none';
        usernameInput.classList.remove('invalid-input');
    } else {
        usernameError.innerHTML = "Имя пользователя должно содержать минимум 5 символов";
        usernameError.style.display = 'block';
        usernameInput.classList.add('invalid-input');
    }

    checkFields();
}

function validatePassword() {
    const passwordInput = document.querySelector('input[name="password"]');
    const passwordError = document.getElementById('passwordError');
    const passwordStrength = document.getElementById('passwordStrength');

    if (passwordInput.validity.valid) {
        passwordError.style.display = 'none';
        passwordInput.classList.remove('invalid-input');
    } else {
        passwordError.innerHTML = "Пароль должен содержать минимум 8 символов, включая по крайней мере одну цифру, одну строчную и прописную буквы, и один специальный символ";
        passwordError.style.display = 'block';
        passwordInput.classList.add('invalid-input');
    }

    // Оценка сложности пароля
    const passwordStrengthValue = calculatePasswordStrength(passwordInput.value);
    passwordStrength.style.background = getStrengthColor(passwordStrengthValue);

    checkFields();
}

// Функция оценки сложности пароля (можно изменить по своему усмотрению)
function calculatePasswordStrength(password) {
    // Пример простой оценки сложности пароля (можно доработать)
    const length = password.length;
    return Math.min(length / 10, 1); // Простая линейная зависимость от длины пароля
}

// Функция, возвращающая цвет градиента в зависимости от сложности пароля
function getStrengthColor(strengthValue) {
    const red = 255 - 255 * strengthValue;
    const green = 255 * strengthValue;
    return "linear-gradient(to right, rgb(" + red + "," + green + ", 0), rgb(255, 255, 0))";
}

function checkFields() {
    if (fioInput.validity.valid && phoneInput.validity.valid && emailInput.validity.valid && usernameInput.validity.valid && passwordInput.validity.valid) {
        registerButton.disabled = false;
    } else {
        registerButton.disabled = true;
    }
}

// Добавление слушателей событий для полей ввода
const fioInput = document.querySelector('input[name="fio"]');
const phoneInput = document.querySelector('input[name="phone"]');
const emailInput = document.querySelector('input[name="email"]');
const usernameInput = document.querySelector('input[name="username"]');
const passwordInput = document.querySelector('input[name="password"]');
const registerButton = document.getElementById('registerButton');

fioInput.addEventListener('input', validateFio);
phoneInput.addEventListener('input', validatePhone);
emailInput.addEventListener('input', validateEmail);
usernameInput.addEventListener('input', validateUsername);
passwordInput.addEventListener('input', validatePassword);