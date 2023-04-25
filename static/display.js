let $status = undefined;

window.onload = () => {
    console.log("Well well well");
    $status = document.getElementById('js--status');
};

const chatSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/signage/'
);

chatSocket.onopen = function(e) {
    $status.innerHTML = "Connected";

    chatSocket.send(JSON.stringify({
        'type': 'introduction',
        'code': window.Config.code
    }));
};

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data);
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};