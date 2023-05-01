function createSocket(onopen) {
    if (window.location.protocol === "https:") {
        wssProtocol = "wss://";
    } else {
        wssProtocol = "ws://";
    }

    let webSocket = new WebSocket(
        wssProtocol + window.location.host + '/ws/signage/'
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

function lazyLoadElement($element, $loadingElement) {
    var $container = document.getElementById("container");
    var $loadingIndicator = document.getElementById("js--loading-indicator");
    var old_children = $container.children;
    var start = new Date();

    if ($loadingElement === undefined) {
        $loadingElement = $element;
    }

    $loadingIndicator.classList.remove("hidden");

    var perform_display = function() {
        console.log("content loading completed in " + (new Date() - start) + "ms");

        // Next perform display will do nothing
        perform_display = function() {};
        
        $element.classList.remove("iframe-loading");
        for (var child of old_children) {
            $container.removeChild(child);
        }

        $loadingIndicator.classList.add("hidden");
    }

    $loadingElement.onload = perform_display;
    $element.id = 'main-display';
    $element.classList.add("iframe-loading");

    $container.appendChild($element);

    setTimeout(function() {
        perform_display();
    }, 5000);
}

function displayPage(page) {
    const $loadingIndicator = document.getElementById("js--loading-indicator");

    if (page === undefined || page === null) {
        // Add placeholder-container and placeholder with display code
        var placeholder = document.createElement("div");
        placeholder.id = "main-display";
        placeholder.classList.add("placeholder");
        placeholder.setAttribute("title", "No page set up for display");
        placeholder.innerText = window.Config.code;

        var placeholderContainer = document.createElement("div");
        placeholderContainer.classList.add("placeholder-container");
        placeholderContainer.appendChild(placeholder);

        document.getElementById("container").replaceChildren(placeholderContainer);

        $loadingIndicator.classList.add("hidden");
    } else if (page['mime_type'].startsWith("image")) {
        var $container = document.createElement("div");
        $container.classList.add("image-container");

        var $image = document.createElement("img");
        $image.id = 'main-display';

        if (page['cover']) {
            $image.classList.add("image-fullwidth");
        } else {
            $image.classList.add("image-contain");
        }
        $image.setAttribute("src", page['path']);
        $container.appendChild($image);

        lazyLoadElement($container, $image);
    } else {
        var $iframe = document.createElement("iframe");
        $iframe.setAttribute("src", page['path']);
        $iframe.setAttribute("allow", "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share");
        
        lazyLoadElement($iframe);
    }
}

function getDisplayInformation() {
    return {
        "width": window.screen.availWidth,
        "height": window.screen.availHeight,
        "screen_width": window.screen.width,
        "screen_height": window.screen.height,
        "dpr": window.devicePixelRatio,
        "user_agent": window.navigator.userAgent,
    }
}

function sendScreenshot() {
    try {
        var element;

        if (document.getElementById('main-display').contentWindow) {
            try {
                element = document.getElementById('main-display').contentWindow.body;
            } catch (e) {
                console.warn("Could not get iframe body", e);
                element = document.body;
            }
        } else {
            element = document.body;
        }

        domtoimage.toJpeg(element, { quality: 0.7 })
            .then(function (dataUrl) {
                console.log("Sending screenshot of size " + dataUrl.length)
                webSocket().send(JSON.stringify({
                    "action": "screenshot",
                    "data": dataUrl,
                    "request_id": 0,
                }));
            })
            .catch(function (e) {
                console.warn("Error while sending screenshot", e);
            })
    } catch (e) {
        console.warn("Error while taking screenshot", e);
    }
}

let lastKeepalive = new Date();

function updateKeepalive() {
    lastKeepalive = new Date();
}

function checkKeepalive() {
    //console.debug("Last keepalive received " + (new Date() - lastKeepalive)/1000 + " s ago");
    if (new Date() - lastKeepalive > 1000 * 60 * 2) {
        console.log("No keepalive received in " + (new Date() - lastKeepalive)/1000/60 + " min");
    }

    if (new Date() - lastKeepalive > 1000 * 60 * 5) {
        console.error("No keepalive received in 5 minutes, checking if internet connection exists");

        // Check if we have a connection
        fetch('/').then((response) => {
            if (response.ok) {
              console.error("Connection to server is OK, refreshing...")
              window.location.reload();
            } else {
                console.error("Unknown error in connection")
            }
          }).catch((error) => {
            console.error("Connection Error. Will keep displaying current image.", error);
          });
    }
}

function startKeepaliveChecks() {
    setInterval(checkKeepalive, 10000);
}