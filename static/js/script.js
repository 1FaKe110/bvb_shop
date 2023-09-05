
function getCookie(name) {
    var matches = document.cookie.match(new RegExp("(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

// Если есть сохраненные данные формы, заполнить форму при загрузке страницы
window.onload = function() {
    var form = document.querySelector('.card');
    var formDataCookie = getCookie('formData');
    if (!formDataCookie) {
        return
    }
    var formData = JSON.parse(formDataCookie);
}

function clearCookies() {
    var formDataCookie = getCookie('formData');
    if (!formDataCookie) {
        return
    }
    var formData = JSON.parse(formDataCookie);
    for (let [key, value] of Object.entries(formData)) {
        delete formData[key]
    }
}

function alert_confirm() {
    alert('Заказ успешно создан! Вам скоро перезвонят :)')
}

window.addEventListener('load', function () {
    document.body.classList.add('loaded');
});