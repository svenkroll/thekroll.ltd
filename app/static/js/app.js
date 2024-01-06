var eventSource = null;
var turnstileToken = null;
var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

window.onload = function() {
       renderTurnstile();
    };

$(document).ready(function() {
    var container = document.getElementById('messages-content');
    var ps = new PerfectScrollbar(container);

    $('#prompt').keypress(function(event) {
        if (event.keyCode === 13 && !event.shiftKey) {
            event.preventDefault();
            $('form').submit();
        }
    });

    $('form').on('submit', function(event) {
        event.preventDefault();

        // Get the prompt
        var prompt = $('#prompt').val();

        // Append the prompt to the response div
        $('<div class="message message-personal">' + prompt + '</div>').appendTo($('.messages-content')).addClass('new');
        // Clear the prompt
        $('#prompt').val('');

        $('<div class="message new"><figure class="avatar"><img src="/static/img/grey_cookie.png" /></figure></div>').appendTo($('.messages-content')).addClass('new');

        if (eventSource) {
            eventSource.close();
        }

        eventSource = new EventSource('/chat?token=' + encodeURIComponent(turnstileToken) + '&message=' + encodeURIComponent(prompt));

        eventSource.onmessage = function(event) {
            var data = JSON.parse(event.data);

            var type = data.type;
            var content = data.content;

            var dateTime = new Date();
            var time = dateTime.toLocaleTimeString();

            // Append the message to the response div based on the role
            if (type === "token") {
                var formattedContent = content.replace(/\n/g, '<br>'); // Replace newline characters with <br>
                var messageElement = $('.message').last();
                messageElement.append(formattedContent);
                // Scroll to the bottom of the output container
                var messagesContentDiv = document.getElementById('messages-content');
                messagesContentDiv.scrollTop = messagesContentDiv.scrollHeight;
            }
            else if (type === "error") {
                console.log(content);
            }
        };

        eventSource.onopen = function(event) {
            console.log("SSE connection opened.");
        };

        // Handle errors
        eventSource.onerror = function(event) {
            console.error("EventSource failed:", event);
            eventSource.close();
        };

        // Close the EventSource when the page is unloaded
        window.onbeforeunload = function() {
            console.error("SSE connection closed.");
            eventSource.close();
        };
    });
});

function addTextAndSubmit(textToAdd) {
    // Prevent default action of the hyperlink
    event.preventDefault();

    // Add the passed text to the textarea
    var textArea = document.getElementById('prompt');
    textArea.value = textToAdd; // Use the passed text

    // Simulate a click on the submit button
    document.getElementById('submitBtn').click();
}

function renderTurnstile() {
   document.getElementById('message-form').style.display = 'none';
   document.getElementById('turnstile-container').style.display = 'block';
   turnstile.render('#turnstile-container', {
      sitekey: '0x4AAAAAAAPB-kgckXDcD0S-',
      theme: 'dark',
      'response-field': false,
      callback: function(token) {
         turnstileToken = token;
         document.getElementById('message-form').style.display = 'block';
         document.getElementById('turnstile-container').style.display = 'none';
      },
   });
};