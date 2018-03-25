var express = require('express');
var http = require('http');
var mysql = require('mysql');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var sync = require('synchronize');
var natural = require('natural');
var path = require("path");
var fs = require("fs");
var uuid = require('node-uuid');
var typeis=require('typeis');
var AWS = require('aws-sdk');



const winston = require('winston');
var logger = new (winston.Logger)({
  transports: [
    new (winston.transports.Console)(),
    new (winston.transports.File)({ filename: "log.js" })
  ]
});


AWS.config.loadFromPath('./aws/credentials.json');

var s3 = new AWS.S3();

app.use(express.static(__dirname + '/web'));

//***********************My-sql***********************************//

var connection = mysql.createConnection({
  host     : '54.254.219.225',
  user     : 'chatbot',
  password : 'chatbotcareerletics@456',
  database : 'careerletics_new'
});

connection.connect(function(err){
if(!err) {
    console.log("Database is connected ... nn");    
} else {
    console.log("Error connecting database ... nn");    
}
});
//**********************Socket.io**************************************//
var users = {};
var sockets = {};
tokenizer = new natural.TreebankWordTokenizer();


io.on('connection', function(socket){

    socket.on('init', function(username){

        sockets[socket.id] = { username : username, socket : socket };  // Store a reference to your socket
        var queryString = 'SELECT name,id FROM candidate WHERE uuid =?';
        connection.query('SELECT name,candidate_id FROM candidate WHERE uuid =?', username,function(err,query){
            if(query.length ==0){
                socket.emit('chat message',{message:"You are not a registered user!"});               
            }else{
                
                row = JSON.stringify(query);
                json = JSON.parse(row);
                name = json[0].name;
                id = json[0].candidate_id;
                users[socket.id]={name : name, id : id};
                logger.log('info',id+" "+"User is started chatbot");
                socket.emit('chat message',{message:"Hi \n" + name +"\t We need some information to process your job application. Chatbot – Amber will take the details. Thank You!",key:"Q"});
            }
        });       
    });
    // Private message is sent from client with username of person you want to 'private message'
    socket.on('chat message', function(to, message,key) {
        var msg = {
            message : message,
            from : sockets[socket.id].username,
           // user_id:users.user_id
        }
        var queryquestion1 = 'select * from chatbot where candidate_id =?';       
        if (message=='ok') {
            key ="Q1";  
        }
        console.log("Key value:"+key);
        var letters = /^[a-zA-Z]+(([\'\,\.\- ][a-zA-Z ])?[a-zA-Z]*)*$/;
        connection.query(queryquestion1,users[socket.id].id,function(err,rows){
            if(rows){
                var d = JSON.parse(JSON.stringify(rows));
                try {
                    sync.fiber(function() {
                        
                        switch (key) {
                            case "Q1":
                            var curr_ctc = d[0].current_ctc;
                            if(curr_ctc == ''|| curr_ctc == null){
                                logger.log('info',"current ctc question asked to "+" "+users[socket.id].id)
                                socket.emit('chat message',{message:"Please enter your current annual CTC in lakhs.",key:"A1"});
                                break;
                                
                            }else if(curr_ctc != ''){
                                logger.log('info',"current ctc already in db"+" "+users[socket.id].id);
                                key = "Q2";
                                
                            }
                    
                            case "A1":
                            if (key=="A1"){
                                data1=tokenizer.tokenize(message);
                                var int = /(^\d*\.?\d)(\w*)$/;
                                var mUnt="xas";
                                var slr,slrV;
                                
                                for (var i=0;i<data1.length;i++){
                                
                                    slrV = data1[i].split(int);
                                    if (!isNaN(slrV[1]))
                                    {    
                                        slr=slrV[1];
                                        if (slrV[2].match(/^[A-Za-z]+$/))
                                           mUnt=slrV[2];
                                        else if (i<data1.length-1)
                                           mUnt=data1[i+1];
                                    }   
                                }
                                logger.log('info',"ctc enter by user"+" "+message+" "+users[socket.id].id);    

                                if(natural.JaroWinklerDistance("lakh,lac,lkh",mUnt)>0.6){
                                    var answer1 = 'update chatbot SET current_ctc = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[slr,users[socket.id].id], sync.defer()));
                                    key="Q2";
                                }
                                else if(natural.JaroWinklerDistance("cr,crore,crs",mUnt)>0.6){
                                    var answer1 = 'update chatbot SET current_ctc = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[slr*100,users[socket.id].id], sync.defer()));
                                    key="Q2";

                                }
                                else if ((slr>=0) && (mUnt=="xas")){
                                    var answer1 = 'update chatbot SET current_ctc = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[slr,users[socket.id].id], sync.defer()));
                                    key="Q2";
                                }    
                                else{
                                    socket.emit('chat message', { message : "Sorry, your input could not be processed. Please enter the information in correct format mentioned at end of each question." ,key :"A1"});
                                    break;  
                                }
                            }

                            case "Q2":
                            if (key=="Q2"){
                                var expec_ctc = d[0].expected_ctc;
                                if(expec_ctc ==''|| expec_ctc == null){
                                    logger.log('info',"expected CTC asked to user "+" "+users[socket.id].id)
                                    socket.emit('chat message',{message:"Please enter your expected annual CTC in lakhs.",key:"A2"});
                                    break;
                            
                                }else if(expec_ctc != ''){
                                    logger.log('info',"expected ctc already in db "+" "+users[socket.id].id)
                                    key = "Q3";
                                    
                                }
                            }

                            case "A2":
                            if (key=="A2"){
                                data1=tokenizer.tokenize(message);
                                var int = /(^\d*\.?\d)(\w*)$/;
                                var mUnt="xas";
                                var slr,slrV;
                                
                                for (var i=0;i<data1.length;i++){
                                
                                    slrV = data1[i].split(int);
                                    if (!isNaN(slrV[1]))
                                    {    
                                        slr=slrV[1];
                                        if (slrV[2].match(/^[A-Za-z]+$/))
                                           mUnt=slrV[2];
                                        else if (i<data1.length-1)
                                           mUnt=data1[i+1];
                                    }   
                                }
                                logger.log('info',"expected ctc enter by user"+ " "+message+" "+users[socket.id].id);    

                                if(natural.JaroWinklerDistance("lakh,lac,lkh",mUnt)>0.6){
                                    var answer1 = 'update chatbot SET expected_ctc = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[slr,users[socket.id].id], sync.defer()));
                                    key="Q3";
                                }
                                else if(natural.JaroWinklerDistance("cr,crore,crs",mUnt)>0.6){
                                    var answer1 = 'update chatbot SET expected_ctc = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[slr*100,users[socket.id].id], sync.defer()));
                                    key="Q3";

                                }
                                else if ((slr>=0) && (mUnt=="xas")){
                                    var answer1 = 'update chatbot SET expected_ctc = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[slr,users[socket.id].id], sync.defer()));
                                    key="Q3";
                                }    
                                else{
                                    socket.emit('chat message', { message : "Sorry, your input could not be processed. Please enter the information in correct format mentioned at end of each question." ,key :"A2"});
                                    break;  
                                }
                            }

                            case "Q3":
                            if (key=="Q3"){
                                var curr_location = d[0].current_location;

                                if(curr_location == '' || curr_location == null){
                                    logger.log('info',"current job location question asked"+" "+users[socket.id].id);
                                    socket.emit('chat message',{message:"Where is your current job location? Please name the city/nearest major city.",key:"A3"});
                                    break;
                     
                                }else if(curr_location != ''){
                                    logger.log('info',"current location already in db"+" "+users[socket.id].id);
                                    key="Q4";
                                  
                                }
                            }

                            case "A3":
                            if (key=="A3"){
                                if(message.match(letters)){
                                    logger.log('info',"current location enter by user"+" "+message+" "+users[socket.id].id);
                                    var answer1 = 'update chatbot SET current_location = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[message,users[socket.id].id], sync.defer()));
                                    key="Q4";

                                }else{
                                    socket.emit('chat message', { message : "Sorry, your input could not be processed. Please enter the information in correct format mentioned at end of each question." ,key :"A3"});
                                    break;

                                }
                                
                                
                            }

                            case "Q4":
                            if (key=="Q4"){
                                var expec_location = d[0].expected_location;
                                if(expec_location == '' || expec_location == null){
                                    logger.log('info',"question asked for preferred job location"+" "+users[socket.id].id);
                                    socket.emit('chat message',{message:"Please enter your preferred job location. Please name the city/nearest major city.",key :"A4"});
                                    break;
                                }else if(expec_location != ''){
                                    logger.log('info',"answer already in db"+" "+users[socket.id].id);
                                    key="Q5";
                                    
                                }

                            }

                            case "A4":
                            if (key=="A4"){
                                if(message.match(letters)){
                                    logger.log('info',"expected location enter by user"+" "+message+" "+users[socket.id].id);
                                    var answer1 = 'update chatbot SET expected_location = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[message,users[socket.id].id], sync.defer()));
                                    key="Q5";

                                }else{
                                    socket.emit('chat message', { message : "Sorry, your input could not be processed. Please enter the information in correct format mentioned at end of each question." ,key :"A4"});
                                    break;

                                }
                                
                                

                            }

                            case "Q5":
                            if (key=="Q5"){
             
                                var notice_period = d[0].notice_period;
                                if(notice_period == '' || notice_period == null){
                                    logger.log('info',"question asked for preferred job location"+" "+users[socket.id].id);
                                    socket.emit('chat message',{message:"Please enter your notice period in months.",key :"A5"});
                                    break;
                                    
                                }else if(notice_period != ''){
                                    logger.log('info',"data already in db"+" "+users[socket.id].id);
                                    key="Q6";
                                    
                                }
                            }

                            case "A5":
                            if (key=="A5"){
                                data1=tokenizer.tokenize(message);
                                var int = /(^\d*\.?\d)(\w*)$/;
                                var mUnt="xaz";
                                var slr,slrV;
                                for (var i=0;i<data1.length;i++){
                                
                                    slrV = data1[i].split(int);
                                    if (!isNaN(slrV[1]))
                                    {    
                                        slr=slrV[1];
                                        if (slrV[2].match(/^[A-Za-z]+$/))
                                           mUnt=slrV[2];
                                        else if (i<data1.length-1)
                                           mUnt=data1[i+1];
                                    }   
                                }
                                logger.log('info',"notice period enter by user"+" "+message+" "+users[socket.id].id);
                                  

                                if(natural.JaroWinklerDistance("month,mnth,mth",mUnt)>0.6){
                                    var answer1 = 'update chatbot SET notice_period = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[slr,users[socket.id].id], sync.defer()));
                                    key="Q6";
                                }
                                else if(natural.JaroWinklerDistance("day",mUnt)>0.6){
                                    var answer1 = 'update chatbot SET notice_period = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[slr/30,users[socket.id].id], sync.defer()));
                                    key="Q6";

                                }
                                else if(natural.JaroWinklerDistance("week,wks",mUnt)>0.6){
                                    var answer1 = 'update chatbot SET notice_period = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[slr/4,users[socket.id].id], sync.defer()));
                                    key="Q6";

                                }
                                else if ((slr>=0) && (mUnt=="xaz")){
                                    var answer1 = 'update chatbot SET notice_period = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[slr,users[socket.id].id], sync.defer()));
                                    key="Q6";
                                }    
                                else{
                                    socket.emit('chat message', { message : "Sorry, your input could not be processed. Please enter the information in correct format mentioned at end of each question." ,key :"A5"});
                                    break;  
                                }
                                
                            }    
                            
                        

                            case "Q6":
                            if (key=="Q6"){
                                var rol = d[0].reason_of_leaving;
                                if(rol == '' || rol == null){
                                    logger.log('info',"question asked for reasons for new job opportunity"+" "+users[socket.id].id);
                                    socket.emit('chat message',{message:"Enter reasons for seeking new opportunity.",key :"A6"});
                                    break;
                                }else if(rol != ''){
                                    logger.log('info',"data already in db"+" "+users[socket.id].id);
                                    key="Q7";
                      
                                }
                            }

                            case "A6":
                            if (key=="A6"){
                                if(message.match(letters)){
                                    logger.log('info',"question asked for reasons for new job opportunity"+" "+message+" "+users[socket.id].id);
                                    var answer1 = 'update chatbot SET reason_of_leaving = ? WHERE candidate_id = ?';
                                    var query = sync.await(connection.query(answer1,[message,users[socket.id].id], sync.defer()));
                                    key="Q7";
                                }else{
                                    socket.emit('chat message', { message : "Sorry, your input could not be processed. Please enter the information in correct format mentioned at end of each question.",key :"A6"});
                                    break;
                                }
                               
                            }

                            case "Q7":
                            if (key=="Q7"){
                                var ref = d[0].socialref;
                                if(ref == '' || ref == null){
                                    logger.log('info',"question asked for social reference links"+" "+users[socket.id].id);
                                    socket.emit('chat message',{message:"Submit URL for your profile pages (LinkedIn/Facebook/Github/StackOverflow)",key :"A7"});
                                    break;
                                }else if(ref != ''){
                                    logger.log('info',"data already in db"+" "+users[socket.id].id);
                                    key="Q8";
                      
                                }
                            }

                            case "A7":
                            if (key=="A7"){
                                
                                logger.log('info',"question asked for reasons for new job opportunity"+" "+message+" "+users[socket.id].id);
                                var answer1 = 'update chatbot SET socialref = ? WHERE candidate_id = ?';
                                var query = sync.await(connection.query(answer1,[message,users[socket.id].id], sync.defer()));
                                key="Q8";
                                
                               
                            }


                            case "Q8":
                            if (key=="Q8")
                            {
                               logger.log('info',"question asked for video interview"+" "+users[socket.id].id);
                               socket.emit('chat message', { message : "Now, would you like to give us a 60 second Video Interview. This will make your profile stronger.",key :"VQ1"});
                               socket.emit('chat message', { message : " Video Panel.",key :"VA1"});
                            }

                            case "VA1":
                            if (key=="VA1"){
                                if( message.typeis('String')){
                                    socket.emit('chat message', { message : "Invalid Input , Please record video and submit it.",key :"VQ1"});
                                    socket.emit('chat message', { message : " Video Panel.",key :"VA1"});
                                    break;
                                }
                                else
                                {
                                    logger.log('info',"User successfully submit  video interview"+" "+users[socket.id].id);
                                    var fileName = uuid.v4();
                                    writeToDisk(message.video.dataURL, fileName + '.webm');
                                    var answer1 = 'update chatbot SET chat_videofile = ? WHERE candidate_id = ?';
                                    fileFullName = fileName + '.mp4';
                                    var query = sync.await(connection.query(answer1,[fileFullName,users[socket.id].id], sync.defer()));
                                                             
                                    key="Q9";
                                }
                            } 

                            case "Q9":
                            if (key=="Q9")
                            {
                                logger.log('info',"user all information is in db"+" "+users[socket.id].id);
                                socket.emit('chat message',{message:"Thanks for sharing! Have a nice day!"});
                            }

                        }
                    });
                }
                catch(err){
                    
                    logger.log('info',"Error in switch:"+" "+err);
                }   

            }    
            else{
                logger.log('info',"unidentified access comes to chatbot");
                socket.emit('chat message',{message:"You are not a registered user!"});
            }      
        });
    });
});

function writeToDisk(dataURL, fileName) {
    var fileExtension = fileName.split('.').pop(),
        fileRootNameWithBase = './uploads/' + fileName,
        filePath = fileRootNameWithBase,
        fileID = 2,
        fileBuffer;

    // @todo return the new filename to client
    while (fs.existsSync(filePath)) {
        filePath = fileRootNameWithBase + '(' + fileID + ').' + fileExtension;
        fileID += 1;
    }

    dataURL = dataURL.split(',').pop();
    fileBuffer = new Buffer(dataURL, 'base64');
    fs.writeFileSync(filePath, fileBuffer);

    console.log('filePath', filePath);
    sendToS3(fileName,fileBuffer);
    

}

function sendToS3(fileName,fileBuffer){

    var myBucket = 'careerletics-candidate-video-interviews';
    var myKey = '' + fileName.split('.')[0] + '.mp4';
    params = {
        Bucket: myBucket,
        Key: myKey,
        Body:fileBuffer,
        ContentEncoding: 'base64',
        ContentType : 'video/mp4'
    };
    s3.putObject(params, function(err, url) {
        if (err) {
            console.log(err);
        } else {
            console.log({Url : "https://S3.ap-south-1.amazonaws.com/careerletics-candidate-video-interviews/"+myKey});
        }
    });
}



var port = process.env.PORT || 3100;

var server = http.listen(port, function() {

    console.log("Listening on " + port);
});


