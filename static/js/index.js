$(document).ready(function() {
    var data = {
        emailService: $('#email-service').val(),
        login: $('#username').val(),
        password: $('#password').val()
    };

    var socket = new WebSocket('ws://' + window.location.host + '/ws/import/');

    socket.onopen = function() {
        socket.send(JSON.stringify(data));
    };

    socket.onmessage = function(event) {
        var data = JSON.parse(event.data);

        console.log(data)

        if (data.total_messages) {
            updateProgressBar(data.total_messages, data.total_messages);
        }
        else if (data.remaining_messages) {
            updateProgressBar(data.remaining_messages, data.remaining_messages);
        }
        else if (data.emails) {
            data.emails.forEach(function(email) {
                addEmailToTable(email);
            });
        }
    };

    function updateProgressBar(remaining, total) {
        var progress = ((total - remaining) / total) * 100;
        $('.progress').css('width', progress + '%');
        $('#remaining-messages').text('Оставшиеся сообщения: ' + remaining);
    }

    function addEmailToTable(email) {
        var row = $('<tr>');
        row.append($('<td>').text(email.subject));
        row.append($('<td>').text(email.description));
        row.append($('<td>').text(email.received_at));
        $('#email-table tbody').append(row);
    }
});
