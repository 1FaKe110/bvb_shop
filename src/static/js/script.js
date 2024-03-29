function runFunction(event) {
  var x = event.which || event.keyCode;
  if (x === 13) {   // Код клавиши 13 соответствует клавише "Enter"
    userSearch();
  }
}

function userSearch() {
    user_request = document.getElementById('search-text').value;
    window.location.href = '/search?q=' + user_request;
}


function getCookie(name) {
    var matches = document.cookie.match(new RegExp("(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

// Если есть сохраненные данные формы, заполнить форму при загрузке страницы
window.onload = function() {
    var form = document.querySelector('.card');
    var formDataCookie = getCookie('formData');
    if (!formDataCookie) {
        document.cookie = 'formData={}; path=/';
        return
    }
    var formData = JSON.parse(formDataCookie);
}

function clearCookies() {
    var formDataCookie = getCookie('formData');
    if (!formDataCookie) {
        document.cookie = 'formData={}; path=/';
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

function admin_alert(text) {
    alert(text)
}

window.addEventListener('load', function () {
    document.body.classList.add('loaded');
});

 //Скрипт для добавления класса "menu-open" к родительскому блоку при нажатии на кнопку "Меню"
// $(document).ready(function(){
//    $('.menu-toggle').click(function(){
//        $('.top-panel').toggleClass('menu-open');
//    });
// });

 const menu_toggle = document.querySelector('.menu-toggle')
 const menu = document.querySelector('.top-panel')

 menu_toggle.addEventListener('click', () => {
     menu.classList.toggle('menu-open')
 })

console.log(menu_toggle)
