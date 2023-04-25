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

    chatSocket.send(JSON.stringify({
        'action': 'get_current_page',
        'request_id': request_id++,
        'code': window.Config.code
    }));
};

function onGetCurrentPage(page) {

}

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Received WS data", data);

    if (data.errors.length !== 0) {
        console.error("WS data contained errors", data.errors)
        for (const e of data.errors) {
            notyf.error(e);
        }
        return true;
    }

    switch (data.action) {
        case "get_current_page":
            onGetCurrentPage(data.data);
            break;
    }
};

chatSocket.onerror = function(e) {
    console.error('Chat socket error', e);
    notyf.error(e);
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly', e);
    notyf.error("Web socket disconnected");
};