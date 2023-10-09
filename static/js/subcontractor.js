function addSubcontractor(event){
    event.preventDefault();
    var row_simple_sub = document.getElementById("row_simple_sub");
    var subcontractor = document.getElementById("subcontractor");
    var time = document.getElementById("time");
    var price = document.getElementById("price");
    var sum = document.getElementById("sum");
    console.log()

    if(row_simple_sub.style.display === 'none'){
        row_simple_sub.style.display = 'flex'
    }else{
        row_simple_sub.style.display = 'none'
    }
}

function submitSubcontractor(event){
    event.preventDefault();
    var subcontractor = document.getElementById("subcontractor").value;
    var time = parseFloat(document.getElementById("time").value);
    var price = parseFloat(document.getElementById("price").value);

    $.ajax({
        type: 'POST',
        url: addSC,
        data: {
            'subcontractor': subcontractor,
            'time': time,
            'price': price,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function(response){
            row_simple_sub.style.display = 'none'
            console.log('total', response)
            window.location.reload()
        },
        error: function(response){
              alert('Błąd:', + response.responseJSON.message)
        } 
    })
}


function deleteQuestionSubcontractor(pk){
    var deleteQuestion = document.getElementById('deleteQuestion')
    deleteQuestion.style.display = 'flex';
    var data = '<div id="questCont">'+
                    '<p>'+"Usunąć Pomocnika/Podwykonawce?"+'</p>'+
                    '<div class="row_cont_in_label">'+
                        '<button class="btn" onclick="deleteSubcontractor('+pk+')">'+
                            '<a>'+"Tak"+'</a>'+
                        '</button>'+
                        '<button class="btn" onclick="closeQuestionSubcontractorDelete()">'+
                            '<a>'+"Nie"+'</a>'+
                        '</button>'+
                    '</div>'+
                '</div>';
        $('#deleteQuestion').html(data)
            
}


function closeQuestionSubcontractorDelete(){
    deleteQuestion.style.display = 'none';
}


function deleteSubcontractor(pk){
    console.log('pk', pk)
    $.ajax({
        type: 'POST',
        url: delSC,

        success: function(response){
            window.location.reload()
        },
        data: {
            'pk': pk,
            'csrfmiddlewaretoken': csrfToken
        },
        error: function(response){
              alert('Błąd:', + response)
        } 
    })

}