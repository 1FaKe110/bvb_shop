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

    fetch('/get_reviews/' + location.href.split('/').slice(-1)[0])
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

function createStarsContainer(n) {
    const starsContainer = document.createElement('div');
    let stars = '';
    for (let i = 0; i < n; i++) {
        stars += '⭐️';  // Юникод символ звезды
    }
    starsContainer.innerHTML = stars;
    starsContainer.style.color = 'gold';  // Желтый цвет звезд
    return starsContainer;
}

function renderReviews(reviews) {
    const reviewsContainer = document.getElementById('reviewsContainer');
    reviews.slice(0, 20).forEach(review => {
        const reviewDiv = document.createElement('div');
        reviewDiv.classList.add('review');

        const reviewDivTop = document.createElement('div');
        reviewDivTop.classList.add('reviewTop');

        const reviewDivBottom = document.createElement('div');
        reviewDivBottom.classList.add('reviewBottom');

        const nameDiv = document.createElement('div');
        nameDiv.classList.add('username');
        const nameP = document.createElement('p');
        const nameStrong = document.createElement('strong');
        nameStrong.innerHTML = review.full_name;
        nameP.appendChild(nameStrong);
        nameDiv.appendChild(nameP);

        const ratingDiv = document.createElement('div');
        ratingDiv.classList.add('reviewRating');
        ratingDiv.appendChild(createStarsContainer(review.rating));

        const dateReviewDiv = document.createElement('div');
        dateReviewDiv.classList.add('dateReview');
        const dateReviewText = document.createElement('p');
        dateReviewText.innerHTML = review.review_date.toString();
        dateReviewDiv.appendChild(dateReviewText);


        const textReviewDiv = document.createElement('div');
        textReviewDiv.classList.add('textReview');
        const textReviewText = document.createElement('p');
        textReviewDiv.classList.add('textReviewСontent');
        textReviewText.innerHTML = review.review_text.replaceAll('\\\n', '\n').replaceAll('\\n', '\n');
        textReviewDiv.appendChild(textReviewText);


        reviewDivTop.appendChild(nameDiv);
        reviewDivTop.appendChild(dateReviewDiv);
        reviewDivBottom.appendChild(ratingDiv);
        reviewDivBottom.appendChild(textReviewDiv);
        reviewDiv.appendChild(reviewDivTop);
        reviewDiv.appendChild(reviewDivBottom);

        reviewsContainer.appendChild(reviewDiv);
    });
}