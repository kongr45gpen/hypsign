let $status = undefined;
let request_id = 0;
const notyf = new Notyf();

window.onload = () => {
};

const chatSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/signage/'
);

chatSocket.onopen = function(e) {
    notyf.success('Connected');

    chatSocket.send(JSON.stringify({
        'action': 'hello',
        'request_id': request_id++,
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