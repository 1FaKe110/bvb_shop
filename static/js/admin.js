function searchTable(tableId, searchInputId) {

    console.log(tableId)
    let table = document.getElementById(tableId);
    let searchInput = document.getElementById(searchInputId);
    let filter = searchInput.value.toUpperCase();
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        let rowData = rows[i].getElementsByTagName("td");
        let foundMatch = false;

        for (let j = 0; j < rowData.length; j++) {
            console.log('rowData[j] = ' + rowData[j]);
            if (!rowData[j]) {
                continue;
            }

            input_tag = rowData[j].getElementsByClassName('name_column');
            console.log(input_tag);
            if (input_tag.length < 1) {
                continue;
            }
            var cellData = input_tag[0].value;


            console.log('cellData = ' + cellData)
            if (cellData.toUpperCase().indexOf(filter) > -1) {
//            if (cellData.toUpperCase() == filter.toUpperCase()) {
                foundMatch = true;
                break;
            }
        }

        rows[i].style.display = foundMatch ? "" : "none";
    }
}

function delay(time) {
  return new Promise(resolve => setTimeout(resolve, time));
}


function remove_item(itemType, itemId) {
    if (!confirm('Правда удаляем?')) {
        // location.reload();
        return
    } else {
        const path = '/' + itemType + '/' + itemId + '/delete';
        console.log('Deleting item: ' + path);
        console.log(fetch(path, {method: "DELETE"}));
        delay(1000).then(() => console.log('waited 1 sec'))
        location.reload();
    }

}

function remove_subItem(itemType, itemId, subItemId) {
    if (!confirm('Правда удаляем?')) {
        location.reload();
        return
    } else {
        const path = '/' + itemType + '/' + itemId + '/delete/' + subItemId;
        console.log('Deleting item: ' + path);
        console.log(fetch(path, {method: "DELETE"}));
        delay(1000).then(() => console.log('waited 1 sec'))
        location.reload();
    }
}

function submitForm(orderId) {
    document.getElementById('order_' + orderId).submit();
}

async function postData(url = "", data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    mode: "cors", // no-cors, *cors, same-origin
    cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
    credentials: "same-origin", // include, *same-origin, omit
    headers: {
      "Content-Type": "application/json",
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: "follow", // manual, *follow, error
    referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data), // body data type must match "Content-Type" header
  });
  return response.json(); // parses JSON response into native JavaScript objects
}


function submitOrderForm(orderId) {
    let order_info = document.getElementsByClassName('order_info')[0].querySelectorAll('input');
    let user_data = {
        "fio": order_info[0].value,
        'phone': order_info[1].value,
        'email': order_info[2].value,
        'address': order_info[3].value,
        'datetime': order_info[4].value
    };

    let status_data = {
        'id': document.querySelector('#orderStatus').value
    }

    let positions = document.getElementsByClassName('position');
    let positions_data = [];
    let tags;
    let row_map;

    for (let i = 1; i < positions.length; i++) {
        tags = positions[i].querySelectorAll('input');
        row_map = {}
        for (let t = 0; t < tags.length - 1; t++) {
            console.log(tags[t].name + ': ' + tags[t].value);
            row_map[tags[t].name] = tags[t].value;
        }
        positions_data.push(row_map);
    }
    console.log(positions_data);

    let data = {}
    data['user'] = user_data
    data['positions'] = positions_data
    data['order'] = status_data

    postData('/order/' + orderId + '/update', data=data)
}