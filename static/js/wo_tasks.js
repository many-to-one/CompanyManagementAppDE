function showTasks(user, work_object){
    //GET
    $.ajax({
        type: 'GET',
        url: showT,
        data: {
          'user': user,
          'work_object': work_object
        },
        success: function(response){
            for(var key in response.tasks_list){
                if(response.tasks_list[key]){
                    var date =  '<div id="taskDateImg">'+
                                    '<div id="taskDateBg">'+
                                        '<div id="taskDate">'+
                                            '<p>'+
                                                response.tasks_list[key].date.slice(0, 2)+
                                            '</p>'+
                                            '<p>'+
                                                response.tasks_list[key].abbreviated_month+
                                            '</p>'+
                                        '</div>'+
                                        '<p id="taskYear">'+
                                            response.tasks_list[key].date.slice(-4)+
                                        '</p>'+
                                    '</div>'+
                                '</div>';
                    var taskElement = response.tasks_list[key].done === true ? 
                    '<p id="done">' + response.tasks_list[key].content + '</p>' : 
                    '<p>' + response.tasks_list[key].content + '</p>';
                    var deleteTaskBtn = response.tasks_list[key].done === true?
                    '<img class="label_img_task" id="deleteTaskBtn" src="'+delete_icon+'" width="30" height="30" onclick="deleteQuestionTask('+response.tasks_list[key].id+', '+user+', '+work_object+')">' :
                    '';
                    var taskStyle = response.tasks_list[key].done === true ?
                    'doneTaskColor' :
                    'activeTaskColor';
                    var data = '<div id="labelTaskCont">' + 
                                    '<div id="task" class="'+taskStyle+'">' +

                                        '<div class="row_task_cont">'+
                                            '<div id="taskDateCont">'+  
                                                date +
                                            '</div>'+
                                            taskElement +
                                        '</div>'+

                                      '<div class="row_task_cont">'+
                                        '<img class="label_img_task" src="'+done_icon+'" width="35" height="35" onclick="doneTask('+response.tasks_list[key].id+', '+user+', '+work_object+')">' +
                                          superus+
                                             deleteTaskBtn +
                                          end_superus+
                                      '</div>'+

                                    '</div>' +
                                '</div>';
                    $('#taskContent').append(data);
                }
            }
        }
    })

    tasks_container.style.display = 'flex'
    pageCont.style.filter = 'blur(4px)'
        if(tasks_container.style.display === 'flex'){
            data = '<img class="label_img_task" id="closeTaskBtn" src="'+close_icon+'" width="30" height="30" onclick="closeTasks()">' +
            '<div id="taskContent">'+ 
            '</div>'+
          '<div>'+
          superus +
            '<form method="POST" id="taskForm">'+
              token +
               '<textarea wrap="soft" class="contentTask" id="content"></textarea>'+
               '<div id="task_mini_cont">'+
                 '<div class="label_img_task">'+
                  '<div class="label_datetimepicker">'+
                   '<input type="date" id="datetimepickerTask">'+
                   '</div>'+
                  '</div>'+
                  '<br>'+
                 '<img id="addTask" class="label_img_task" src="'+add_icon+'" width="30" height="30" onclick="newTask(' + user + ', ' + work_object + ', event)">' +
               '</div>'+
            '</form>'+
            end_superus+
         '</div>';
        }else if(tasks_container.style.display === 'flex'){
            tasks_container.style.display = 'none';
            data = ''
        }
        tasks_container.innerHTML = data
}

// Create a new Task
function newTask(user, work_object, event){
    event.preventDefault();
    var datetimepickerValue = document.getElementById("datetimepickerTask").value;
    var content = document.getElementById("content").value;
    //POST
    $.ajax({
        type: 'POST',
        url: newT,
        data: {
              'date': datetimepickerValue,
              'content': content,
              'user': user,
              'work_object': work_object,
              'csrfmiddlewaretoken': csrfToken
          },
          success: (data) => {
            content.value = '';
            showTasks(user, work_object)
          },
          error: (data) => {
              alert('error', data)
          }     
    })
}


    // Close the Task window
    function closeTasks(){
        tasks_container.style.display = 'none';
        pageCont.style.filter = 'none'
    }

    // Finish the task
    function doneTask(pk, user, work_object){
        $.ajax({
            type: 'POST',
            url: doneT,
            data: {
                'pk': pk,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response){
                if(response.message === true){
                    showTasks(user, work_object)
                }else{
                    showTasks(user, work_object)
                }
            },
            error: function(response) {
                  alert('Błąd:', response.message)
            }  
        })
    }

// Question for deleting the task
function deleteQuestionTask(pk, user, work_object){
    $.ajax({
        type: 'POST',
        url: delTQ,
        data: {
            'pk': pk,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function(response){
            if(response.message === 'ok'){
                var deleteQuestion = document.getElementById('deleteQuestion')
                tasks_container.style.display = 'none';
                deleteQuestion.style.display = 'flex';
                var data = '<div id="questCont">'+
                                '<p>'+"Usunąć te zadanie?"+'</p>'+
                                '<div class="row_cont_in_label">'+
                                    '<button class="btn" onclick="deleteTask('+pk+', '+user+', '+work_object+')">'+
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
function deleteTask(pk, user, work_object){
    var deleteQuestion = document.getElementById('deleteQuestion')
    $.ajax({
        type: 'POST',
        url: delT,
        data: {
            'pk': pk,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function(response){
            deleteQuestion.style.display = 'none';
            showTasks(user, work_object);
        },
        error: function(response){
              alert('Błąd:', + response.responseJSON.message)
        } 
    })
}

function closeQuestionDelete(){
    var deleteQuestion = document.getElementById('deleteQuestion')
    deleteQuestion.style.display = 'none';
    tasks_container.style.display = 'flex';
    location.reload();
}