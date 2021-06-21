const path = require('path');
const express = require('express');
const app = express();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const os = require('os');
const osc = require('node-osc');

var clients = {};
var receivers = {};
var ip_address = '192.168.10.174';
var message_queue = [];
var python = new osc.Client("127.0.0.1",5001);
//43280

http.listen(5003, function(){
    console.log('listening on ' + ip_address + ':5003');
});

app.use(express.static(path.join(__dirname, 'client')));

io.sockets.setMaxListeners(0);

io.on('connection', function(socket){
    clients[socket.id] = socket;
    receivers[socket.id] = new osc.Server(5002,"127.0.0.1", () => {
        console.log('OSC Server is listening', socket.id);
    });

    socket.on('disconnect', function(reason){
        delete clients[socket.id];
    });
    
    //get the userinput data
    socket.on('generated_text', function(data){
        var pass = true;
        if (data.length == 0){
            socket.emit("await");
        } else{
            message_queue.forEach(function(client){
                if (client[1] == socket.id){
                    pass = false;
                    socket.emit("await");
                }
            });
            if (pass){
                message_queue.push([data,socket.id]);
                python.send("/input_string", message_queue[message_queue.length - 1], function() {});
            }
        }
    });
    
    receivers[socket.id].on("message", function (oscMsg) {
        console.log(oscMsg);
        if (oscMsg[0] == "/output"){
            message_queue.forEach(function(client,index){
                if (client[1] == oscMsg[2]){
                    message_queue.splice(index);
                }
            });
            io.to(oscMsg[2]).emit("message",oscMsg[1]);
        }
    });

    //On killing the process
    process.on('SIGINT',function(){
        socket.disconnect(true);
        process.exit (0);
    });
});