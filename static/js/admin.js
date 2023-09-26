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

function remove_item(itemType, itemId) {
    if (!confirm('Правда удаляем?')) {
        location.reload();
        return
    } else {
        const path = '/' + itemType + '/' + itemId + '/delete';
        console.log('Deleting item: ' + path);
        console.log(fetch(path, {method: "DELETE"}));
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
        location.reload();
    }
}

function submitForm(itemId) {
    document.getElementById('order_' + orderId).submit();
}

