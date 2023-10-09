// Check if the user is scrolling
chatWindow.addEventListener('scroll', handleScroll);
setInterval(checkScrollActivity, 500);
var scrollActive = false;

function handleScroll() {
  scrollActive = true;
  clearTimeout(scrollTimeout);

  var scrollTimeout = setTimeout(function() {
    scrollActive = false;
  }, 200); 
}

function checkScrollActivity() {
    
    if (scrollActive) {
      shouldToBottom = false; // if the User is scrolling the scrollTop will be not in bottom on the window
    }else if (chatWindow.scrollHeight - chatWindow.scrollTop > 600){
      chatDown.style.display = 'block' // Make the chat_down button active
      if(chatDownQuantity) {
          chatDownQuantity.style.display = 'block'; //Show the quantity of unread messages
      }
    }else if (chatWindow.scrollHeight - chatWindow.scrollTop < 600){
      chatDown.style.display = 'none' // Make the chat_down button inactive
      if(chatDownQuantity) {
          chatDownQuantity.style.display = 'none' //Hide the quantity of unread messages
      }
    }
  }


  // The online unread messages count
  function showCount(){
      $.ajax({
      type: 'GET',
      url: "{% url 'showCount' work_object.pk %}",
      success: (response) => {
          var data = response.count
          console.log('showCount', data)
          if (data > 0){
              console.log('showCount > 0', data)
              chat_down_quantity.textContent = data
          }else{
              chat_down_quantity.textContent = 0
          }
      }
      })
  }


  // The chat window will shows the last message on the bottom 
  function scrollBottom() {
      if (shouldToBottom === true){
          chatWindow.scrollTop = chatWindow.scrollHeight
      }
  }

  // Go up down the chat and 
  function lastMessage() {
      chatWindow.scrollTop = chatWindow.scrollHeight
  }

 
 // WORK OBJECT STATUS CHANGE
   function changeStatus(event){
    event.preventDefault();
    var btnTitle = event.currentTarget.querySelector('.btn-title');
    var status = 'Zakończone'
    if (btnTitle.textContent === 'Zakończ') {
            btnTitle.textContent = 'Aktywuj';
            status = 'Zakończone';
        } else {
            btnTitle.textContent = 'Zakończ';
            status = 'Aktywne';
        }
    
    $.ajax({
      type: 'POST',
      url: chwost,
      data: {
          'status': status,
      },
      headers: {
          'X-CSRFToken': csrfToken
      },
      success: (data) => {
        console.log(data)
      },
      error: (data) => {
          console.log('error')
      }                
    })        
}