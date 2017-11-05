function search() {
  // Declare variables
  var input, filter, table, tr, td, i;
  input = document.getElementById("search");
  filter = input.value.toUpperCase();

  // Get active members' table rows.
  table = document.getElementById("table");
  console.log(table)
  tr = table.getElementsByTagName("tbody")[0].children;

  // Loop through all table rows, and hide those who don't match the search query
  function find(tr) {
      for (i = 0; i < tr.length; i++) {
        tr[i].style.display = "none"
        for (j = 0; j < 3; j++) {
          td = tr[i].getElementsByTagName("td")[j];
          if (td) {
            if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            }
          }
        }
      }
    }
  find(tr)
}
