const path = require('path');
const express = require('express');
const app = express();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const os = require('os');
var session = require('express-session');
var bodyParser = require('body-parser');
const osc = require('node-osc');

var clients = {};
var receivers = {};
var ip_address = '127.0.0.1';
var message_queue = [];
var python = new osc.Client("127.0.0.1",5001);
//43280

http.listen(5000, function(){
    console.log('listening on ' + ip_address + ':5000');
});

app.use(session({
	secret: 'secret',
	resave: true,
	saveUninitialized: true
}));
app.use(bodyParser.urlencoded({extended : true}));
app.use(bodyParser.json());

app.get('/', function(req, res) {
	res.sendFile(path.join(__dirname + '/client/login_page/index.html'));
});

app.post('/auth', function(req, res) {
	var username = req.body.username;
	var password = req.body.password;
	if (username && password) {
        if (username == "admin" && password == "admin"){
			req.session.loggedin = true;
			req.session.username = username;
			res.redirect('/home');
			res.end();
		} else {
			res.send('Incorrect Username and/or Password!');
			res.end();
		}			
	} else {
		res.send('Please enter Username and Password!');
		res.end();
	}
});

app.get('/home', function(req, res) {
	res.sendFile(path.join(__dirname + '/client/home/index.html'));
});

app.get('/index.js', function(req, res) {
    res.setHeader('Content-Type', 'application/javascript');
    res.sendFile(__dirname + '/client/home/index.js');
});

app.post('/submit_input', function(req,res){
    var input = req.body.prompt;
    console.log(input)
    res.send("Click Recorded")
});

// app.get('/input_field', function(request, response) {
//     var input = request.body.prompt;
//     console.log(request.body.prompt,request.body.button)
//     if (input == "test"){
//         console.log(input)
//     }
// 	if (request.session.loggedin) {
// 	    response.sendFile(path.join(__dirname + '/client/home/index.html'));
//     } else {
// 		response.send('Please login to view this page!');
// 	}
// });

// io.sockets.setMaxListeners(0);

// io.on('connection', function(socket){
//     clients[socket.id] = socket;
//     receivers[socket.id] = new osc.Server(5002,"127.0.0.1", () => {
//         console.log('OSC Server is listening', socket.id);
//     });

//     socket.on('disconnect', function(reason){
//         delete clients[socket.id];
//     });
    
//     //get the userinput data
//     socket.on('generated_text', function(data){
//         var pass = true;
//         if (data.length == 0){
//             socket.emit("await");
//         } else{
//             message_queue.forEach(function(client){
//                 if (client[1] == socket.id){
//                     pass = false;
//                     socket.emit("await");
//                 }
//             });
//             if (pass){
//                 message_queue.push([data,socket.id]);
//                 python.send("/input_string", message_queue[message_queue.length - 1], function() {});
//             }
//         }
//     });
    
//     receivers[socket.id].on("message", function (oscMsg) {
//         console.log(oscMsg);
//         if (oscMsg[0] == "/output"){
//             message_queue.forEach(function(client,index){
//                 if (client[1] == oscMsg[2]){
//                     message_queue.splice(index);
//                 }
//             });
//             io.to(oscMsg[2]).emit("message",oscMsg[1]);
//         }
//     });

//     //On killing the process
//     process.on('SIGINT',function(){
//         socket.disconnect(true);
//         process.exit (0);
//     });
// });