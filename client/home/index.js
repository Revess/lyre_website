var socket = io();


function generate_text(){
    socket.emit('generated_text', document.getElementById("prompt").value);
    
}

function login(){
    socket.emit('login', true);
}

socket.on("await", () => {
    document.getElementById("output").innerHTML = "still processing the previous request";
});

socket.on("message", (data) => {
    document.getElementById("output").innerHTML = data;
});

socket.on("approved", (data) => {
    window.open("../user_page/index.html");
});
