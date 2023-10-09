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

function excel(event){
event.preventDefault();
var raportsTable = document.getElementById('raportsTable');
var filterRaport = document.getElementById('filterRaport');
var searchRaport = document.getElementById('searchRaport');
var backRaport = document.getElementById('backRaport');
var excelRaport = document.getElementById('excelRaport');
var deleteMarked = document.getElementById('deleteMarked');

// Making buttons visible or invisible
raportsTable.style.display = 'none';
filterRaport.style.display = 'block';
searchRaport.style.display = 'none';
backRaport.style.display = 'flex';
excelRaport.style.display = 'none';
deleteMarked.style.display = 'none';
}