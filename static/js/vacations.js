// The vacations variable must be assigned here 
// to be called in header.html with js function
var vacations = document.getElementById('vacations_filter_cont')

function submitFormUsers() {
  var form = document.getElementById("users");
  form.submit();
}

function submitFormYears() {
  var form = document.getElementById("years");
  form.submit();
}

function checkAll() {
var checkboxes = document.querySelectorAll('input[type="checkbox"]');

    for (var i = 0; i < checkboxes.length; i++) {
        if( checkboxes[i].checked == false){
            checkboxes[i].checked = true;
        }else{
            checkboxes[i].checked = false;
        }
    }
}