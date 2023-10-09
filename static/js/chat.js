// POST
// Send the message by pressing Enter
// Add an event listener to the chat input field
const chatInput = document.getElementById('content');
chatInput.addEventListener('keypress', handleEnterKey);

// Function to handle the "Enter" key press event
function handleEnterKey(event) {
  if (event.key === 'Enter') {
    event.preventDefault(); // Prevent the default "Enter" key behavior (e.g., new line)
    const message = chatInput.value.trim(); // Get the message content

    // Check if the message is not empty
    if (message !== '') {
        sendChatMessage(event); // Call a function to send the message
    }
  }
}

function sendChatMessage(event){
    var txt = document.getElementById("content").value;
    var textarea = document.getElementById("content")
    event.preventDefault();
    $('#content').empty();
    textarea.value = '';
    shouldToBottom = true
      $.ajax({
          type: 'POST',
          url: cht,
          data: {
              'txt': txt,
              'user': user,
              'csrfmiddlewaretoken': csrfToken
          },
          success: (data) => {
            console.log('success', data)    
          },
          error: (data) => {
              console.log('error')
              $('#content').empty();
          }                
      }) 

    }


    function showMessages(){
        var Ty = 'Ty:'
        $.ajax({
                type: 'GET',
                url: cht,
                success: function(response){
                    console.log('chat', response.messages)
                    $('#chato').empty();

                    if(response.mess_count == 20){
                        var history = '<div class="chat_history">'+
                                        '<p class="nav-el" onclick="showMessageHistory()">'+'pokaż więcej'+'</p>'+
                                      '</div>'
                        $('#chato').append(history)
                    }
                    
                    for (var key in response.messages){
                        if(response.messages[key].is_read == true){
                            var isRead = '<img src="'+is_read_icon+'" width="20" height="15">'
                        }else{
                            var isRead = '<img src="'+un_read_icon+'" width="20" height="15">'
                        }
                       if(response.user === response.messages[key].name){
                            var data= '<p class="r">'+Ty+'</p>'+
                                    '<div class="chat_label_r">'+
                                        '<p class="chat_content">'+response.messages[key].content+'</p>'+
                                        '<p class="chat_time">'+response.messages[key].day+response.messages[key].time+" "+isRead+'</p>'+
                                        '<img style="cursor: pointer;" src="'+del_mess_icon+'" width="20" height="20" onclick="deleteMess('+response.messages[key].id+')">'+
                                    '</div>'
                        }else{
                            var data='<p class="l">'+response.messages[key].name+'</p>'+
                                    '<div class="chat_label_l">'+
                                        '<p class="chat_content">'+response.messages[key].content+'</p>'+
                                        '<p class="chat_time">'+response.messages[key].day+response.messages[key].time+" "+isRead+'</p>'+
                                    '</div>'
                        }
                                
                        $('#chato').append(data)
                        // chat_down_quantity.textContent = response.count
                    }
                    scrollBottom()
                    },
                error: function(response){
                    alert('Error')
                }
            })
        }


        function showMessageHistory(){
            var Ty = 'Ty:'
            $.ajax({
                    type: 'GET',
                    url: mess_history,
                    success: function(response){
                        $('#chato').empty();
    
                        for (var key in response.messages){
                            if(response.messages[key].is_read == true){
                                var isRead = '<img src="'+is_read_icon+'" width="20" height="20">'
                            }else{
                                var isRead = '<img src="{% static "'+un_read_icon+'" %}" width="20" height="20">'
                            }
                           if(response.user === response.messages[key].name){
                                var data= '<p class="r">'+Ty+'</p>'+
                                        '<div class="chat_label_r">'+
                                            '<p class="chat_content">'+response.messages[key].content+'</p>'+
                                            '<p class="chat_time">'+response.messages[key].day+response.messages[key].time+" "+isRead+'</p>'+
                                            '<img style="cursor: pointer;" src="'+del_mess_icon+'" width="20" height="20" onclick="deleteMess('+response.messages[key].id+')">'+
                                        '</div>'
                            }else{
                                var data='<p class="l">'+response.messages[key].name+'</p>'+
                                        '<div class="chat_label_l">'+
                                            '<p class="chat_content">'+response.messages[key].content+'</p>'+
                                            '<p class="chat_time">'+response.messages[key].day+response.messages[key].time+" "+isRead+'</p>'+
                                        '</div>'
                            }
                                    
                            $('#chato').append(data)
                            // chat_down_quantity.textContent = response.count
                        }
                        scrollBottom()
                        },
                    error: function(response){
                        alert('Error')
                    }
                })
            }



            $(document).ready(function(){

                showMessages()
        
                function getMessages(){
                var Ty = 'Ty:'
                $.ajax({
                        type: 'GET',
                        url: cht, 
                        success: function(response){
        
                            $('#chato').empty();
        
                            if(response.mess_count == 20){
                                var history = '<div class="chat_history">'+
                                                '<p class="nav-el" onclick="showMessageHistory()">'+'pokaż więcej'+'</p>'+
                                              '</div>'
                                $('#chato').append(history)
                            }
        
                            for (var key in response.messages){
                                if(response.messages[key].is_read == true){
                                    var isRead = '<img src="'+is_read_icon+'" width="20" height="15">'
                                }else{
                                    var isRead = '<img src="'+un_read_icon+'" width="20" height="15">'
                                }
                               if(response.user === response.messages[key].name){
                                    var data= '<p class="r">'+Ty+'</p>'+
                                            '<div class="chat_label_r">'+
                                                '<p class="chat_content">'+response.messages[key].content+'</p>'+
                                                '<p class="chat_time">'+response.messages[key].day+response.messages[key].time+" "+isRead+'</p>'+
                                                '<img style="cursor: pointer;" src="'+del_mess_icon+'" width="20" height="20" onclick="deleteMess('+response.messages[key].id+')">'+
                                            '</div>'
                                }else{
                                    var data='<p class="l">'+response.messages[key].name+'</p>'+
                                            '<div class="chat_label_l">'+
                                                '<p class="chat_content">'+response.messages[key].content+'</p>'+
                                                '<p class="chat_time">'+response.messages[key].day+response.messages[key].time+" "+isRead+'</p>'+
                                            '</div>'
                                }
                                        
                                $('#chato').append(data)
                                // chat_down_quantity.textContent = response.count
        
                            }
                            scrollBottom()
                            if(response.messages){
                                intervalID = setInterval(checkMessages, 1000);
                            }else{
                                    alert('Error')
                                    clearInterval(intervalID); // Stop the interval
                                }
                            },
                        error: function(response){
                            alert('Error')
                        }
                    })
                }
        
        
        
                let intervalID;
        
                // Function to send the AJAX request and handle the response
                function checkMessages() {
                    $.ajax({
                        type: 'GET',
                        url: check_mess,
                        success: function(response) {
                            if (response.message === true) {
                                console.log('response.message', response.message);
                                clearInterval(intervalID); // Stop the interval
                                getMessages(); // Call getMessages_() function
                            } else if (response.message === 1){
                                console.log('response.message', response.message);
                                clearInterval(intervalID); // Stop the interval
                                getMessages(); // Call getMessages_() function
                            }
                            else {
                                console.log('response.message', response.message);
                            }
                        }
                    });
                }
        
                // Start the interval and store the ID in the intervalID variable
                intervalID = setInterval(checkMessages, 1000);
            })


// Delete message
function deleteMess(id) {
    console.log('deleteMess', id)
    var deleteQuestion = document.getElementById('deleteQuestion')
            deleteQuestion.style.display = 'flex';
            var data = '<div id="questCont">'+
                            '<p>'+"Usunąć wiadomość?"+'</p>'+
                            '<div class="row_cont_in_label">'+
                                '<button class="btn" onclick="deleteMessConf('+id+')">'+
                                    '<a>'+"Tak"+'</a>'+
                                '</button>'+
                                '<button class="btn" onclick="closeQuestionDeleteCurrMess()">'+
                                    '<a>'+"Nie"+'</a>'+
                                '</button>'+
                            '</div>'+
                        '</div>';
                $('#deleteQuestion').html(data)
}

function deleteMessConf(id) {
    console.log('deleteMessConf', id)

    $.ajax({
        type: 'POST',
        url: dell_mess,
        data: {
              'pk': id,
              'csrfmiddlewaretoken': csrfToken
          },
          success: (data) => {
            console.log('deleteMessConf - Success', data.response)
          },
          error: (data) => {
              alert('error', data)
          }     
})

deleteQuestion.style.display = 'none';
// tasks_container.style.display = 'flex';
}

function closeQuestionDeleteCurrMess(){
    deleteQuestion.style.display = 'none';
}


// Question for deleting all messages
function deleteQuestionMessages(work_object){

    $.ajax({
        type: 'GET',
        url: qwest_dell_all_mess,
        success: function(response){
            if(response.message === 'ok'){
                console.log('response.message', response.message)
                var deleteQuestion = document.getElementById('deleteQuestion')
                deleteQuestion.style.display = 'flex';
                var data = '<div id="questCont">'+
                                '<p>'+"Usunąć wszystkie wiadomości?"+'</p>'+
                                '<div class="row_cont_in_label">'+
                                    '<button class="btn" onclick="deleteAllMessagesWO('+work_object+')">'+
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
              alert('Wystąpił błąd')
        } 
    })

}


// Delete all messages in chat
function deleteAllMessagesWO(work_object){
    console.log('work_object', work_object)
    $.ajax({
        type: 'POST',
        url: dell_all_mess,
        data: {
            'work_object': work_object
        },
        headers: {
          'X-CSRFToken': csrfToken
        },
        success: function(response){
            if(response.message === 'ok'){
                var deleteQuestion = document.getElementById('deleteQuestion')
                deleteQuestion.style.display = 'flex';
                var data = '<div id="questCont">'+
                                '<p>'+response.content+'</p>'+
                                // '<div class="row_cont_in_label">'+
                                //     '<button class="btn" onclick="closeQuestionDelete()">'+
                                //         '<a>'+"Ok"+'</a>'+
                                //     '</button>'+
                                // '</div>'+
                            '</div>';
                    $('#deleteQuestion').html(data)
                    location.reload();
            }else{
                alert(response.message)
            }

        },
        error: function(response){
              alert('Błąd:', + response.responseJSON.message)
        } 
    })
}