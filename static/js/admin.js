function searchTable(tableId, searchInputId) {
    let table = document.getElementById(tableId);
    let searchInput = document.getElementById(searchInputId);
    let filter = searchInput.value.toUpperCase();
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        let rowData = rows[i].getElementsByTagName("td");
        let foundMatch = false;

        for (let j = 0; j < rowData.length; j++) {
            let cellData = rowData[j].textContent || rowData[j].innerText || rowData[j].value;

            if (cellData.toUpperCase().indexOf(filter) > -1) {
                foundMatch = true;
                break;
            }
        }

        rows[i].style.display = foundMatch ? "" : "none";
    }
}