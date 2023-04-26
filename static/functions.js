function createSocket(onopen) {
    let webSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/signage/'
    );

    webSocket.onerror = function(e) {
        console.error('Chat socket error', e);
        if (notyf !== undefined) {
            notyf.error(e);
        }
    };
    
    webSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly', e);
        if (notyf !== undefined) {
            notyf.error("Web socket disconnected");

            setTimeout(function() {
                webSocket = createSocket(onopen)();
              }, 1000);
        }
    };

    webSocket.onopen = function(e) {
        if (onopen !== undefined) {
            onopen(webSocket, e);
        }
        notyf.success('Connected');
    }

    // Returns a function so that we always have the working version of the websocket, even after disconnects
    return function() { return webSocket };
}

function displayPage(page) {
    if (page === undefined || page === null) {
        // Add placeholder-container and placeholder with display code
        var placeholder = document.createElement("div");
        placeholder.classList.add("placeholder");
        placeholder.setAttribute("title", "No page set up for display");
        placeholder.innerText = window.Config.code;
        var placeholderContainer = document.createElement("div");
        placeholderContainer.classList.add("placeholder-container");
        placeholderContainer.appendChild(placeholder);
        document.getElementById("container").replaceChildren(placeholderContainer);
    } else {
        console.error('page exists', page);
        var iframe = document.createElement("iframe");
        iframe.setAttribute("src", page['path']);
        iframe.setAttribute("allow", "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share");
        document.getElementById("container").replaceChildren(iframe);
    }
}

function getDisplayInformation() {
    return {
        "width": window.screen.availHeight,
        "height": window.screen.availWidth,
        "screen_width": window.screen.width,
        "screen_height": window.screen.height,
        "dpr": window.devicePixelRatio,
        "user_agent": window.navigator.userAgent,
    }
}