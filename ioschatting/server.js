var express = require('express');
var bodyParser = require('body-parser');
var mongoose = require('mongoose');
var http = require('http');
var methodOverride = require('method-override');
var fileUpload = require('express-fileupload');
var app = express();
var apns = require('apn');
mongoose.Promise = require('bluebird');





var http = require('http').Server(app);
var io = require('socket.io')(http);
//*************************************************************//

app.get('/1', function(req, res){
  res.sendFile(__dirname + '/index.html');
});
app.get('/2', function(req, res){
  res.sendFile(__dirname + '/index1.html');
});

var ChatMessage = require('./app/models/chatMessage');
var userData = require('./app/models/userData');

var users = {};
var sockets = {};
function sendiosNotification(notification,callback){
    if(!notification.data.to){
        return callback({error : false, message : "receiver's deviceid is not available. could not send notificaion"});
    }
    var client = new apns.Provider({
        cert:"./cert/cert.pem",
        key:"./cert/key.pem",
        production: true,

    });
    var notifi = new apns.Notification();
    notifi.topic = "com.iPredictt.WavelengthiOS"
    notifi.alert = notification.data.message;
    notifi.title = notification.data.username;
    device_token = notification.data.to;     
    client.send(notifi,device_token)
}

io.on('connection', function(socket){
	socket.on('init', function(username){
		console.log(username);
		users[username] = socket.id,
		sockets[socket.id] = { username : username, socket : socket };  // Store a reference to your socke
		socket.emit('chat message', { message : "welcome", from : "server"});

		userData.findById(username,{firstname:1},function(err,userdata){
			sockets[socket.id].user_name  = userdata.firstname;

		});
	});
  
	// Private message is sent from client with username of person you want to 'private message'
    socket.on('chat message', function(to, message) {
        // Lookup the socket of the user you want to private message, and send them your message
		var msg = { 
			message : message, 
			from : sockets[socket.id].username 
		}
        ChatMessage.create({sender_id : msg.from, receiver_id : to, message : message}).then(function(err, message){
        	//console.log(users);
		    if(users[to]){
        		sockets[users[to]].socket.emit('chat message', msg);
        	}else{
        		userData.findById(to,{device_token:1},function(err,userid){
        			if(userid.device_token == ''){
        				sockets[users[to]].socket.emit('chat message', msg);
        			}else{
        				var data = {
                    		to: userid.device_token,
                    		username:sockets[socket.id].user_name,
                    		message:msg.message,
						};

						//console.log(data);
                		sendiosNotification({ data : data });

        			}
        			
        		});

        	}
			
		});
    });      
	
	socket.on('disconnect', function () {		
        if(sockets[socket.id]){
        	userid = sockets[socket.id].username;
        	console.log(sockets[socket.id].username);
            io.emit('user disconnected', { message : sockets[socket.id].username+" is disconnected", from : "server"});
            delete sockets[socket.id];
	    	delete users[userid];
        }		
	});
});


//*********************************************************************//

//mongoose.connect(process.env.MONGOLAB_URI || 'mongodb://wavelengthadmin:wavelengthappsecret@52.77.224.77/wavelength');
//mongoose.Promise = global.Promise;
mongoose.connect(process.env.MONGOLAB_URI || 'mongodb://abintesting:wavelengthdeveloper@ds017862.mlab.com:17862/testing_abin');
app.use(express.static(__dirname + '/public'));


app.use(bodyParser.urlencoded({extended:true}));
app.use(bodyParser.json());
app.use(methodOverride('_method'));
app.use(fileUpload());

//app.use('/', require('./routes/userActions')(app, express));



var port = process.env.PORT || 3000;

var server = http.listen(port, function() {

    console.log("Listening on " + port);
});



