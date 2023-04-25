function displayPage(page) {
    var iframe = document.createElement("iframe");
    iframe.setAttribute("src", page['path']);
    iframe.setAttribute("allow", "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share");
    document.getElementById("container").replaceChildren(iframe);
}