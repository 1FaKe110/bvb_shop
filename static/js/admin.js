function searchTable(tableId, searchInputId) {
    console.log(tableId)
    let table = document.getElementById(tableId);
    let searchInput = document.getElementById(searchInputId);
    let filter = searchInput.value.toUpperCase();
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        let rowData = rows[i].getElementsByTagName("td");
        let foundMatch = false;

        for (let j = 0; j < 1; j++) {
            console.log('rowData[j] = ' + rowData[j]);
            input_tag = rowData[j].getElementsByClassName('id_column');
            console.log(input_tag);
            if (input_tag) {
                var cellData = input_tag[0].value;
            }
//            } else {
//                try {
//                    var cellData = rowData[j].textContent || rowData[j].innerText || rowData[j].value;
//                } catch (TypeError) {
//                }
//            }

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