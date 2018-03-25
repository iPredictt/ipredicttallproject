var express = require('express');
var bodyParser = require('body-parser');

var http = require('http');
var mysql = require('mysql');
var methodOverride = require('method-override');

var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);


app.use(express.static(__dirname + '/web'));

var connection = mysql.createConnection({
  host     : '54.254.219.225',
  user     : 'chatbot',
  password : 'chatbotcareerletics@456',
  database : 'careerletics_new'
});

io.on('connection', function(socket){
    socket.on('message', function (data) {

        var answer1 = 'select uuid,email from candidate where uuid = ?';
        console.log(uuid);
        connection.query(answer1,data.token,function(err,query){
            if(query.length==0){
                console.log("false entry");
            }else{
                row = JSON.stringify(query);
                json = JSON.parse(row);
                uuid = json[0].uuid;
                email = json[0].email;
                if(uuid == data.token && email == data.email){
                    answer2 = 'INSERT INTO `email_unsubscription_users` (`uuid`,`email`,`subscription-type`) VALUES(?, ?,?) ON DUPLICATE KEY UPDATE email = VALUES(email)';
                    connection.query(answer2,[data.token,data.email,data.type],function(err,query){
                        console.log("success");

                    })


                         
                } 
            }

        });
    });

});

app.use(bodyParser.urlencoded({extended:true}));
app.use(bodyParser.json());
app.use(methodOverride('_method'));
var port = process.env.PORT || 3457;

var server = http.listen(port, function() {

    console.log("Listening on " + port);
});
