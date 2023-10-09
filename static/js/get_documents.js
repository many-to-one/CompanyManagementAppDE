function openImage(image) {
    if (image.requestFullscreen) {
        image.requestFullscreen();
    } else if (image.mozRequestFullScreen) { // Firefox
        image.mozRequestFullScreen();
    } else if (image.webkitRequestFullscreen) { // Chrome, Safari and Opera
        image.webkitRequestFullscreen();
    } else if (image.msRequestFullscreen) { // IE/Edge
        image.msRequestFullscreen();
    }
}


function deleteQuestion(pk){
    var deleteQuestion = document.getElementById('deleteQuestion')
    deleteQuestion.style.display = 'flex';
    var data = '<div id="questCont">'+
                    '<p>'+"Usunąć dokument"+'</p>'+
                    '<div class="row_cont_in_label">'+
                        '<button class="btn" onclick="deleteImage('+pk+')">'+
                            '<a>'+"Tak"+'</a>'+
                        '</button>'+
                        '<button class="btn" onclick="closeQuestion()">'+
                            '<a>'+"Nie"+'</a>'+
                        '</button>'+
                    '</div>'+
                '</div>';
        $('#deleteQuestion').html(data)
            
}

function closeQuestion(){
    var deleteQuestion = document.getElementById('deleteQuestion')
    deleteQuestion.style.display = 'none';
}


function deleteImage(pk){
    console.log('doc', pk)

    $.ajax({
        type: "POST",
        url: deleteDocumentUrl,
        data: {
            'pk': pk,
            'csrfmiddlewaretoken': csrfToken,
        },
        success: function(response) {
            console.log('success', response)
            closeQuestion()
            window.location.reload()
        },
        error: function(response){
              alert('Błąd:', + response)
        } 
    })
}