const path = require('path');
const express = require('express');
const app = express();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const os = require('os');
const osc = require('node-osc');

var clients = {};
var ip_address = '192.168.10.201';
var message_queue = [];
var python = new osc.Client("127.0.0.1",5001);
var receiver = new osc.Server(5002,"127.0.0.1", () => {
    console.log('OSC Server is listening');
});
//43280

http.listen(5000, function(){
    console.log('listening on ' + ip_address + ':5000');
});

app.use(express.static(path.join(__dirname, 'client')));

io.sockets.setMaxListeners(0);

io.on('connection', function(socket){
    clients[socket.id] = socket;

    socket.on('disconnect', function(reason){
        delete clients[socket.id];
    });
    
    //get the userinput data
    socket.on('generated_text', function(data){
        var pass = true;
        message_queue.forEach(function(client){
            if (client[1] == socket.id){
                pass = false;
                socket.emit("await");
            }
        });
        if (pass){
            message_queue.push([data,socket.id]);
            console.log(message_queue)
            python.send("/input_string", message_queue[0], function() {});
        }
    });
    
    receiver.on("message", function (oscMsg) {
        message_queue.forEach(function(client,index){
            if (client[1] == oscMsg[1]){
                message_queue.splice(index);
                throw BreakException;
            }
        });
        socket.emit("message",oscMsg[1])
        console.log("An OSC message just arrived!", 1);
    });

    //On killing the process
    process.on('SIGINT',function(){
        socket.disconnect(true);
        process.exit (0);
    });
});