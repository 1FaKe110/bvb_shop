// Сохранение данных формы в cookies при отправке
function addToCart(product_id, product_price, product_amount) {
    var form = document.querySelector('.card-' + product_id);
    console.log('форма найдена' + (form));
    console.log(form);
    var formDataCookie = getCookie('formData');
    if (formDataCookie) {
        var formData = JSON.parse(formDataCookie);
        if (product_id in formData) {
            console.log('product_id [' + product_id + '] in formData:' + (product_id in formData))
            formData[product_id.toString()] += 1;
            console.log('Данные для ' + form.querySelector('.amount-in-cart'));
            form.querySelector('.amount-in-cart').text = formData[product_id.toString()];


            if (formData[product_id.toString()] >= product_amount ) {
                formData[product_id.toString()] = product_amount
            }

            let product_sum = parseInt(formData[product_id.toString()]) * parseInt(product_price)
            console.log('Общая сумма в для товара [' + product_id + ']: ' + product_sum);
            form.querySelector('.sum-item-price').text = product_sum;
        }
    } else {
        var formData = {};
        formData[product_id.toString()] = 1;
    }

    document.cookie = 'formData=' + JSON.stringify(formData) + '; path=/';
    console.log(document.cookie)

    check_buttons(formData, product_id, product_price)
    location.reload();
}

// удаление данных формы в cookies при отправке
function removeFromCard(product_id) {
    console.log('.card-' + product_id);
    var form = document.querySelector('.card-' + product_id);
    var button = form.querySelector('.remove-from-card-button');
    var formDataCookie = getCookie('formData');
    if (formDataCookie) {
        var formData = JSON.parse(formDataCookie);
        console.log("ID product_id продукта в cookie? " + (product_id in formData));
        console.log(formData);
        if (product_id in formData) {
            addButton = form.querySelector('.add-to-card');
            if (formData[product_id.toString()] <= 1) {

                var result = window.confirm("Подтвердить удаление из корзины");

                if (result) {
                    // Код, который исполняется при нажатии "Подтвердить"
                    delete formData[product_id.toString()];
                    location.reload();
                }

            } else {
                console.log('удаляю 1 товар с id ' + product_id + ' из корзины');
                formData[product_id.toString()] -= 1;
            }
        }
        document.cookie = 'formData=' + JSON.stringify(formData) + '; path=/';
        console.log(document.cookie);
    }
    location.reload();
}

function check_buttons(formData, product_id, product_price) {
    var form = document.querySelector('.card-' + product_id);
    var buttons = form.querySelector('.product-price-block');

    if (document.querySelector('.remove-from-card-button') == null) {
        // Create a new input element of type 'input' with type button
        var inputButton = document.createElement("input");

        // set params to button
        inputButton.type = "button";
        inputButton.value = "-";
        inputButton.className = "remove-from-card-button";
        inputButton.addEventListener("click", removeFromCard);

        buttons.appendChild(inputButton);
    }
    addButton = form.querySelector('.add-to-card');
    let product_sum = parseInt(formData[product_id.toString()]) * parseInt(product_price)
    console.log('Общая сумма в для товара c id = [' + product_id + ']: ' + product_sum);
    form.querySelector('p.sum-item-price').text = product_sum;

}