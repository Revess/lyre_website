var socket = io();

function generate_text(){
    socket.emit('generated_text', document.getElementById("prompt").value);
}

socket.on("await", () => {
    document.getElementById("output").innerHTML = "still processing the previous request";
});

socket.on("message", (data) => {
    document.getElementById("output").innerHTML = data;
});