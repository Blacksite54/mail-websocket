$(document).ready(function() {
    var socket = new WebSocket('ws://' + window.location.host + '/ws/import/');

    $('#import-btn').click(function() {
        var emailService = $('#email-service').val();
        var email = $('#email').val();
        var password = $('#password').val();

        socket.send(JSON.stringify({
            'email_service': emailService,
            'email': email,
            'password': password
        }));

        $('.progress').css('width', '0%');
        $('.progress-text').text('0%');
        $('.message').text('');
    });

    socket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        $('.progress').css('width', data.progress);
        $('.progress-text').text(data.progress);
        $('.message').text(data.message);
    };
});
