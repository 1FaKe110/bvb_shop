function addNewReview(userId, productId) {
    var rating = document.querySelector('input[name="rating"]:checked').value;
    var reviewText = document.getElementById('reviewText').value;

    var data = {
        "user_id": userId,
        "review_text": reviewText,
        "rating": rating,
        "product_id": productId
    };

    fetch('/add_review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(responseData => {
            console.log("ответ на добавление отзыва: " + responseData['code'])
            showNotification(responseData);
            document.getElementById('reviewForm').reset();
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showNotification("Произошла ошибка. Пожалуйста, повторите попытку позже");
        });
}

function showNotification(responseData) {
    var notification = document.getElementById('notification');
    notification.classList.add(responseData['code'])
    notification.innerText = responseData['message'];
    notification.style.display = "block";
    setTimeout(function () {
        notification.style.display = "none";
    }, 3000);
}

document.addEventListener("DOMContentLoaded", function () {
    fetchReviews();
});

function fetchReviews() {

    fetch('/get_reviews/' + location.href.split('/').slice(-1)[0])  // замените на ваш реальный эндпоинт для получения отзывов
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(reviews => {
            renderReviews(reviews);
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
}

function renderReviews(reviews) {
    const reviewsContainer = document.getElementById('reviewsContainer');
    reviews.slice(0, 20).forEach(review => {
        const reviewDiv = document.createElement('div');
        reviewDiv.classList.add('review');
        reviewDiv.innerHTML = "<p><strong>" + review.full_name + "</strong>" +
            " - Оценка: " + review.rating +
            " Дата: " + review.review_date +
            "</p><p>" + review.review_text + "</p>";
        reviewsContainer.appendChild(reviewDiv);
    });
}