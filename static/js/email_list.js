$(document).ready(function() {
    var socket = new WebSocket('ws://' + window.location.host + '/ws/import/');

    function updateProgressBar(progress, message) {
        $('.progress').css('width', progress);
        $('.progress-text').text(message);
    }

    function addEmailToTable(email) {
        var row = $('<tr>');
        row.append($('<td>').text(email.subject));
        row.append($('<td>').text(email.from_email));
        row.append($('<td>').text(email.to_email));
        row.append($('<td>').text(email.received_at));
        $('#email-table tbody').append(row);
    }

    socket.onopen = function() {
        var data = {
            emailService: $('#email-service').val(),
            login: $('#username').val(),
            password: $('#password').val()
        };

        socket.send(JSON.stringify(data));
    };

    socket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        if (data.progress) {
            updateProgressBar(data.progress, data.message);
        } else if (data.emails) {
            data.emails.forEach(function(email) {
                addEmailToTable(email);
            });
            updateProgressBar('100%', 'Получение сообщений завершено');
        }
    };
});
