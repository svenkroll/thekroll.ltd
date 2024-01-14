var eventSource = null;
var turnstileToken = null;
var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

window.onload = function() {
       renderTurnstile();
    };

function decodeHTMLEntities(text) {
    return $("<textarea/>")
    .html(text)
    .text();
}

$(document).ready(function() {
    var container = document.getElementById('messages-content');
    var ps = new PerfectScrollbar(container);
    var buffer = "";

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

        // Check if the prompt is empty
        if (prompt.trim() === '') {
            // Do nothing if the prompt is empty
            return;
        }

        // Append the prompt to the response div
        $('<div class="message message-personal">' + prompt + '</div>').appendTo($('.messages-content'));
        // Clear the prompt
        $('#prompt').val('');

        $('<div class="message new"><figure class="avatar"><img src="/static/img/grey_cookie.png" /></figure><div class="responsetext"></div></div>').appendTo($('.messages-content')).addClass('new');
        $('<div class="thinking-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>').appendTo($('.responsetext').last());

        if (eventSource) {
            eventSource.close();
        }

        eventSource = new EventSource('/chat?token=' + encodeURIComponent(turnstileToken) + '&message=' + encodeURIComponent(prompt));

        eventSource.onmessage = function(event) {
            var data = JSON.parse(event.data);

            var type = data.type;
            var dateTime = new Date();
            var time = dateTime.toLocaleTimeString();

            // Append the message to the response div based on the role
            if (type === "token") {
                buffer += data.content;
                var lastIndexOfCloseTag = buffer.lastIndexOf('>');
                var lastIndexOfOpenTag = buffer.lastIndexOf('<');
                if (lastIndexOfOpenTag == -1 || lastIndexOfOpenTag < lastIndexOfCloseTag) {
                    $('.thinking-dots').remove(); // Remove thinking dots if they exists
                    var formattedContent = buffer.replace(/\n/g, '<br>'); // Replace newline characters with <br>
                    var messageElement = $('.responsetext').last();
                    var currentText = messageElement.text();
                    messageElement.text(currentText + formattedContent);
                    // messageElement.append(formattedContent);
                    buffer = "";
                    // Scroll to the bottom of the output container
                    var messagesContentDiv = document.getElementById('messages-content');
                    messagesContentDiv.scrollTop = messagesContentDiv.scrollHeight;
                }

            }
            else if (type === "end") {
                //append last buffer if incomplete
                // Decode response
                var messageElement = $('.responsetext').last();
                var decodedResponseText = decodeHTMLEntities(messageElement.html().replace(/```html/g, '').replace(/```/g, ''));
                messageElement.html(decodedResponseText);
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
         document.getElementById('prompt').focus();
      },
   });
};