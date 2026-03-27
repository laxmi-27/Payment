// Search on table using search inpute options
function searchTable() {
    let input = document.getElementById("searchBar").value.toLowerCase();
    let tables = document.querySelectorAll("table");

    tables.forEach(table => {
        let rows = table.querySelectorAll("tr");

        rows.forEach((row, index) => {
            if (index === 0) return; // header skip

            let text = row.textContent.toLowerCase();

            row.style.display = text.includes(input) ? "" : "none";
        });
    });
}



// Common Sorting Script for Tables
function sortTable(n, dir) {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById("sortableTable"); // Ensure your table has this ID
    switching = true;

    while (switching) {
        switching = false;
        rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];

            if (dir == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            }
        }

        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}

// Attach sorting functionality to all sortable tables
document.addEventListener("DOMContentLoaded", function () {
    // Find all elements with the class "sortable-header"
    var sortableHeaders = document.querySelectorAll(".sortable-header");

    sortableHeaders.forEach(function (header) {
        // Attach click event for ascending sort
        if (header.querySelector(".sort-asc")) {
            header.querySelector(".sort-asc").addEventListener("click", function () {
                var columnIndex = Array.from(header.parentNode.children).indexOf(header);
                sortTable(columnIndex, "asc");
            });
        }

        // Attach click event for descending sort
        if (header.querySelector(".sort-desc")) {
            header.querySelector(".sort-desc").addEventListener("click", function () {
                var columnIndex = Array.from(header.parentNode.children).indexOf(header);
                sortTable(columnIndex, "desc");
            });
        }
    });
});


// ADD & Dispaly screen show
document.addEventListener("DOMContentLoaded", function () {
    const addButton = document.getElementById("addButton");
    const displayButton = document.getElementById("displayButton");
    const addForm = document.getElementById("addForm");
    const addTable = document.getElementById("addTable");

    // Show "Add State" form by default
    addForm.style.display = "block";
    addButton.classList.add("active-button"); // Optional: Add styling for active button

    addButton.addEventListener("click", function () {
        addForm.style.display = "block";
        addTable.style.display = "none";
        addButton.classList.add("active-button");
        displayButton.classList.remove("active-button");
    });

    displayButton.addEventListener("click", function () {
        addForm.style.display = "none";
        addTable.style.display = "block";
        displayButton.classList.add("active-button");
        addButton.classList.remove("active-button");
    });
});

document.addEventListener("DOMContentLoaded", function () {

    let tables = document.querySelectorAll("table");

    tables.forEach(table => {
        let header = table.querySelector("tr:first-child");

        if (header) {
            header.style.position = "sticky";
            header.style.top = "0";
            header.style.background = "#fff";
            header.style.zIndex = "2";
        }

        if (!table.parentElement.classList.contains("table-wrapper")) {
            let wrapper = document.createElement("div");
            wrapper.classList.add("table-wrapper");
            wrapper.style.maxHeight = "65vh"
            wrapper.style.overflowY = "auto";

            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });

});