var eventSource = null;

var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

// Function to handle SSE and update the response div
function setupSSE() {
    if (eventSource) {
        eventSource.close();
    }
    eventSource = new EventSource("/stream");

    eventSource.onmessage = function(event) {
        var data = JSON.parse(event.data);

        var type = data.type;
        var content = data.content;

        var dateTime = new Date();
        var time = dateTime.toLocaleTimeString();

        // Append the message to the response div based on the role
        if (type === "token") {
            //$('<div class="message new"><figure class="avatar"><img src="/static/cookie.png" /></figure>' + content + '</div>').appendTo($('.messages-content')).addClass('new');
            $('.message').last().append(content);
            //$('#response .robot').last().append(content);
        }
        else if (type === "error") {
            console.log(content);
        }

        // Scroll to the bottom of the output container
        var messagesContentDiv = document.getElementById('messages-content');
        messagesContentDiv.scrollTop = messagesContentDiv.scrollHeight;


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
}

// Call the setupSSE function when the page is ready
$(document).ready(function() {
    setupSSE();

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
        // get the CSRF token from the cookie
        var csrftoken = Cookies.get('csrftoken');

        // set the CSRF token in the AJAX headers
        $.ajaxSetup({
            headers: { 'X-CSRFToken': csrftoken }
        });
        // Get the prompt
        var prompt = $('#prompt').val();
        var dateTime = new Date();
        var time = dateTime.toLocaleTimeString();

        // Append the prompt to the response div
        $('<div class="message message-personal">' + prompt + '</div>').appendTo($('.messages-content')).addClass('new');

        // $('#response').append('<p id="GFG1" class="human"><i class="bi bi-person"></i>: ' + prompt + '</p>');

        // Clear the prompt
        $('#prompt').val('');
        $.ajax({
            url: '/',
            type: 'POST',
            data: {
                prompt: prompt,
            },
            dataType: 'json',
            success: function(data) {
                if (data.status === 'success') {
                    // Append the response to the response div
                    // $('#response').append('<span id="GFG2" class="robot"> <i class="bi bi-robot"></i>: </span>');
                    $('<div class="message new"><figure class="avatar"><img src="/static/img/grey_cookie.png" /></figure></div>').appendTo($('.messages-content')).addClass('new');
                }
            }
        });
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
