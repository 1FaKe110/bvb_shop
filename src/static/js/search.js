function searchHelper() {
    var search = document.getElementById('search-text');
    if (event.key === 'Escape') {
        return;
    }
    fetch("/search-helper?q=" + search.value)
        .then(response => response.json())
        .then(data => {
            var resultsDataList = document.getElementById("searchResults");
            resultsDataList.classList.add("fadeOutAnimation"); // Добавляем класс с анимацией
            resultsDataList.innerHTML = '';
            if (data.length == 0) {
                resultsDataList.style.zIndex = "-1";
            } else {
                resultsDataList.style.zIndex = "19";
            }

            data.forEach(function (item) {
                var option = document.createElement('a');
                option.classList.add('searchCategory')
                option.classList.add("fadeInAnimation"); // Добавляем класс с анимацией
                option.href = '/category/' + item['c_name']
                option.text = '• ' + item['c_name'];
                option.style = item['c_name'];
                resultsDataList.appendChild(option);
            });
        });
};

document.addEventListener('DOMContentLoaded', function () {
    // Обработчик события клика мыши на теге с id="search-text"
    document.getElementById('search-text').addEventListener('click', function () {
        searchHelper(); // Вызываем функцию searchHelper при клике на тег
    });
});


document.addEventListener('DOMContentLoaded', function () {
    // Функция, которая удаляет содержимое из блока с id="searchResults"
    function clearSearchResults() {
        document.getElementById('searchResults').innerHTML = '';
    }

    // Обработчик события клика мыши
    document.addEventListener('click', function (event) {
        // Проверяем, был ли клик вне блока с id="searchResults" и id="search-text"
        if (!event.target.closest('#searchResults') && !event.target.closest('#search-text')) {
            clearSearchResults(); // Вызываем функцию для удаления содержимого
        }
    });

    // Обработчик события нажатия клавиши escape
    document.addEventListener('keyup', function (event) {
        if (event.key === 'Escape') {
            clearSearchResults(); // Вызываем функцию для удаления содержимого
        }
    });
});

