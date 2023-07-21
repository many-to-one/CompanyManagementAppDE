// chat.js

// Send message to the server
function sendMessage() {
    var sender = document.getElementById('sender').value;
    var content = document.getElementById('content').value;

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/send-message/', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            console.log('Message sent successfully.');
        }
    };
    xhr.send('sender=' + encodeURIComponent(sender) + '&content=' + encodeURIComponent(content));
}

// Fetch messages from the server
function fetchMessages() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get-messages/', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var messages = JSON.parse(xhr.responseText);
            var chatbox = document.getElementById('chatbox');
            chatbox.innerHTML = '';

            for (var i = 0; i < messages.length; i++) {
                var message = messages[i];
                var html = '<p><strong>' + message.sender + '</strong>: ' + message.content + '</p>';
                chatbox.innerHTML += html;
            }
        }
    };
    xhr.send();
}

// Periodically fetch messages every 2 seconds
setInterval(fetchMessages, 2000);
