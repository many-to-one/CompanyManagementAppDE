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