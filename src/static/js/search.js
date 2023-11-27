function searchHelper() {
    var search = document.getElementById('search-text');
    fetch("/search-helper?q=" + search.value)
        .then(response => response.json())
        .then(data => {
            var resultsDataList = document.getElementById("searchResults");
            resultsDataList.classList.add("fadeOutAnimation"); // Добавляем класс с анимацией
            resultsDataList.innerHTML = '';


            resultsDataList.style
            data.forEach(function(item) {
                var option = document.createElement('a');
                console.log(item['c_name']);
                option.classList.add('searchCategory')
                option.href = '/category/' + item['c_name']
                option.text = item['c_name'];
                option.classList.add("fadeInAnimation"); // Добавляем класс с анимацией
                resultsDataList.appendChild(option);
            });
        });
    };
