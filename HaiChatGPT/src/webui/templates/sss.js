
var source = new EventSource("/stream");
var i = 0;
source.onmessage = function(event) {
    if (event.data === "<|im_end|>") {
    source.close();
    return
    }
    var div = document.createElement("div");
    div.className = i % 2 == 0 ? "user-message" : "chatbot-message";
    div.innerHTML = div.className + ":"+ event.data;
    document.getElementById("output").appendChild(div);
    i += 1;
    document.getElementById("output").scrollTop = document.getElementById("output").scrollHeight;
    // document.getElementById("output").innerHTML += event.data;
};


