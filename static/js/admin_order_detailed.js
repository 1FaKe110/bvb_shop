function submitOrderForm() {
    let order_info = document.getElementsByClassName('order_info')[0].querySelectorAll('input');

    let user_data = {
        "fio": order_info[0].value,
        'phone': order_info[1].value,
        'email': order_info[2].value,
        'address': order_info[3].value,
        'datetime': order_info[4].value
    };

//    let positions = document.getElementsByClassName('position');
//    let positions_data = [];
//    for (var p = 1, p =< position.length, p++) {
//        let data = {};
//        let tags = positions[p].querySelectorAll('input');
//        tags.forEach((element) => data[element.name] = element.value);
//    }

}
