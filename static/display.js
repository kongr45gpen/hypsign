let $status = undefined;
let request_id = 0;
const notyf = new Notyf();

window.onload = () => {
    startKeepaliveChecks();
};

const webSocket = createSocket(function (webSocket) {
    webSocket.onmessage = function (e) {
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
            case "hello":
                onHello(data.data)
                break;
            case "display_updated":
            case "reload":
                onDisplayUpdated(data.data);
                break;
            case "refresh":
                window.location.reload();
                break;
            case "keepalive":
                updateKeepalive();
        }
    };

    webSocket.send(JSON.stringify({
        'action': 'hello',
        'request_id': request_id++,
        'code': window.Config.code,
        'display': getDisplayInformation(),
        'device_id': localStorage.getItem("device_id")
    }));

    webSocket.send(JSON.stringify({
        'action': 'get_current_page',
        'request_id': request_id++,
        'code': window.Config.code
    }))
});

function onGetCurrentPage(page) {
    displayPage(page);
}

function onDisplayUpdated(page) {
    webSocket().send(JSON.stringify({
        'action': 'get_current_page',
        'request_id': request_id++,
        'code': window.Config.code
    }))
}

function onHello(data) {
    localStorage.setItem("device_id", data.device_id);
}
