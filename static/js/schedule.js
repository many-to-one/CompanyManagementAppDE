function hideCont(){
    var scheduleCont = document.getElementById('scheduleCont')
    $.ajax({
      type: 'GET',
      url: header,
      success: (response) => {
          if(response.menu === 'active'){
            console.log('response', response)
            scheduleCont.style.display = 'none';
          }else{
            console.log('response', response)
            scheduleCont.style.display = 'flex';
          }
        }
      })
  }
  
  
    document.addEventListener("DOMContentLoaded", function() {
      var tasksContainer = document.getElementById("tasks_container");
      tasksContainer.style.display = "block";
    });
  
    window.addEventListener("beforeunload", function() {
      var tasksContainer = document.getElementById("tasks_container");
      tasksContainer.style.display = "none";
    });
  
  
    // Question for deleting the task
    function deleteQuestionTask(pk, question, funct){
  
          $.ajax({
              type: 'POST',
              url: deleteTaskQuestion,
              data: {
                'pk': pk
              },
              dataType: 'json', 
              headers: {
                'X-CSRFToken': csrfToken
              },
              success: function(response){
                  if(response.message === 'ok'){
                      var deleteQuestion = document.getElementById('deleteQuestion')
                      deleteQuestion.style.display = 'flex';
                      var data = '<div id="questCont">'+
                                      '<p>'+question+'</p>'+
                                      '<div class="row_cont_in_label">'+
                                          '<button class="btn" onclick="'+funct+'('+pk+')">'+
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
  
      // Delete the task
      function deleteTask(pk){
        var deleteQuestion = document.getElementById('deleteQuestion')
          $.ajax({
              type: 'POST',
              url: delTask,
              data: {
                  'pk': pk,
                  'csrfmiddlewaretoken': csrfToken
              },
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
        var deleteQuestion = document.getElementById('deleteQuestion')
          deleteQuestion.style.display = 'none';
          location.reload();
      }
  
  
      function deleteAllDoneTasksQuestion(pk){
        // we doesn't need pk 
        // it just for combined function for question
        $.ajax({
          type: 'GET',
          url: delAllTQ,
          success: function(response){
                  if(response.message === 'ok'){
                      var deleteQuestion = document.getElementById('deleteQuestion')
                      deleteQuestion.style.display = 'flex';
                      var data = '<div id="questCont">'+
                                      '<p>'+response.content+'</p>'+
                                      '<div class="row_cont_in_label">'+
                                          '<button class="btn" onclick="closeQuestionDelete()">'+
                                              '<a>'+"Ok"+'</a>'+
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