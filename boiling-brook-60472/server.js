var express = require('express');
var bodyParser = require('body-parser');
var mongoose = require('mongoose');
var http = require('http');
var methodOverride = require('method-override');
var app = express();


var http = require('http').Server(app);
//var io = require('socket.io')(http);

mongoose.connect(process.env.MONGOLAB_URI || 'mongodb://wavelengthdeveloper:QWERTY121wavelength@139.59.39.209/wavelength');
app.use(express.static(__dirname + '/public'));


app.use(bodyParser.urlencoded({extended:true}));
app.use(bodyParser.json());
app.use(methodOverride('_method'));


app.use('/', require('./routes/api')(app, express));
app.use('/', require('./routes/userActions')(app, express));



var port = process.env.PORT || 3000;

app.listen(port, function() {

    console.log("Listening on " + port);
});


