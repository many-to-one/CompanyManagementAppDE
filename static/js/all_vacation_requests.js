    // Question for deleting the task
    function deleteVacationRequestQuestion(){
        const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
        const checkedValues = Array.from(checkboxes).map((checkbox) => checkbox.value);
        $.ajax({
            type: 'GET',
            url: url, 
            success: function(response){
                console.log('response', response)
                if(response.message === 'ok'){
                    var deleteQuestion = document.getElementById('deleteQuestion')
                    deleteQuestion.style.display = 'flex';
                    var data = '<div id="questCont">'+
                                    '<p>'+'Usunąć wniosek?'+'</p>'+
                                    '<div class="row_cont_in_label">'+
                                        '<button class="btn" onclick="deleteVacationRequest()">'+
                                            '<a>'+"Tak"+'</a>'+
                                        '</button>'+
                                        '<button class="btn" onclick="closeQuestionDelete()">'+
                                            '<a>'+"Nie"+'</a>'+
                                        '</button>'+
                                    '</div>'+
                                '</div>';
                        $('#deleteQuestion').html(data)
                }else{
                    alert(response.message)
                }
            },
            error: function(response){
                alert('Błąd:', + response.responseJSON.message)
            }
        })
        
    }

    function deleteVacationRequest(){
        const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
        const checkedValues = Array.from(checkboxes).map((checkbox) => checkbox.value);
        console.log('checkedValues', checkedValues)
        $.ajax({
        type: 'POST',
        url: url2,
        data: JSON.stringify({ 'req': checkedValues }),
        contentType: 'application/json',
        headers: { 'X-CSRFToken': csrfToken },
        success: function(response){
            deleteQuestion.style.display = 'none';
            location.reload();
        },
        error: function(response){
              alert('Błąd:', + response.responseJSON.message)
        } 
    })

    }

    function closeQuestionDelete(){
        deleteQuestion.style.display = 'none';
    }