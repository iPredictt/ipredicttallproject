var userData = require('../app/models/userData');
var dummyProfiles = require('../app/models/dummyProfiles');
var reportprofile = require('../app/models/ReportProfile');
var Notification =  require('../app/models/Notification');
var UserActivity =  require('../app/models/UserActivity');
var request = require('request-json');

module.exports = function(app,express){
    var api = express.Router();

    function sendNofitication(notification, createDbEntry, callback){        
        if(!notification.data.to){
            return callback({error : false, message : "receiver's deviceid is not available. could not send notificaion"});
        }
        var client = request.createClient('https://gcm-http.googleapis.com/gcm/');
        client.headers = {
            'Content-Type':'application/json',
            'Authorization':'key=AIzaSyAs_jnh-O6rP_rV-9GdeYLOd-OteAeR6Q8'
        };        
        if(createDbEntry){
            // creating notification object
            Notification.create(notification, function(err, notification){ 
                if(err){
                    return callback({error : err.toString()}); 
                }
                // when notificaiton is being created in to db. it is also being send in response to sender
                var res = {notification : notification};
                // sending notificaiton to receiver's device  
                client.post('send', notification.data, function(err, response, body) {
                    var error = 'false';
                    var message = "action performed successfully";
                    if(err !=null){
                        error = 'true';
                        message = "there is some error in sending notification";
                    }
                    res.body = body;
                    res.error = error;
                    res.message = message;
                    callback(res);            
                });
            });
        }else{
            // sending notificaiton to receiver's device  
            client.post('send', notification.data, function(err, response, body) {
                var error = 'false';
                var message = "action performed successfully";
                if(err !=null){
                    error = 'true';
                    message = "there is some error in sending notification";
                }
                callback({body : body, error: error, message : message});            
            });
        }
    }


    // function for Push notification to all users
    function sendPushNotification(data, callback){        
        var client = request.createClient('https://gcm-http.googleapis.com/gcm/');
        // if first don't work then try this line 
        //var client = request.createClient('https://gcm-http.googleapis.com/gcm/send');
        client.headers = {
            'Content-Type':'application/json',
            'Authorization':'key=AIzaSyAs_jnh-O6rP_rV-9GdeYLOd-OteAeR6Q8'
        };        
        client.post('send', data, function(err, response, body) {
            var error = 'false';
            var message = "action performed successfully";
            if(err !=null){
                error = 'true';
                message = "there is some error in sending notification";
            }
            callback({body : body, error: error, message : message});            
        });
    }

    // Daily push notification  function
    //var notifyUsers = function(){
    api.post('/wavelength/wavelength_restapi/v1/push', function(req, res){    
        var deviceidArray = [];
        userData.AppData.find({}, {_id:0,device_id:1}, function (err, users) {
            users.forEach(function(user){
                if(user.device_id && user.device_id!==null){
                    deviceidArray.push(user.device_id);
                }
            });
            var data = {
                registration_ids: deviceidArray,
                data: {
                    line1:req.body.line1,
                    line2: req.body.line2,
                    type: '5001' 
                }
            };
            
            sendPushNotification(data,
                // this is the funciton to be called when notificaiton is sent
                function(response){                                                
                    return res.send({error:'false',message:"push notification successfully"});
                }
                
            );
        });
    });


    //left swipe
    api.post('/wavelength/wavelength_restapi/v1/rejectprofile/:userid/:rejecteduserid', function(req, res){
        userData.AppData.findById(req.params.userid, function(err, user){
            if(err) {
                return res.send({ error : 'true', message : err.toString()});
            }
            if(!user || user === null) {
                return res.send({ error: 'true', message : 'User Not Found' });
            };
            // Creating a user object for rejectedProfile
            UserActivity.create({user_id : req.params.userid, otheruser_id : req.params.rejecteduserid,status:4},function(err, rejectedProfile){
                if(err){
                    return res.send({error: 'true', message : err.toString()});
                }
                return res.send({error : 'false', message : "Profile successfully added to reject list"});
            })            
        });
    });


    
    // right swipe
    api.post('/wavelength/wavelength_restapi/v1/sendfriendrequest/:userid/:receiverid', function(req, res){
        // here finding the user's object form db who want to send friendship request
        userData.AppData.findById(req.params.userid, function(err, user){
            if(err) {
                return res.send({ error : 'true', message : err.toString() });
            }
            if(!user || user === null) {
                return res.send({ error: 'true', message : 'User Not Found' });
            };
            // finding user object to whome request if to be sent.        
            userData.AppData.findById(req.params.receiverid, function(err, receiver){
                if(err) {
                    return res.send({ error : 'true', message : err.toString() });
                }
                if(!receiver || receiver === null) {
                    return res.send({ error : 'true', message : 'User Not Found' });
                };
                // this is the data object which is to be sent as notification
                var data = {
                    to: receiver.device_id,
                    data: {
                        title: 'Wavelength',
                        isBackground: false,
                        flag : 1, 
                        data: {
                            "sender_name":user.name,
                            "profile_pic": user.profile_pic,
                            "sender_id":user._id,
                            "message" : "Wants to connect with you"
                        }
                    }
                };
                // creating friendship request's object. 
                UserActivity.create({ user_id : user._id, otheruser_id : req.params.receiverid}, function(err, fRequest){
                    if(err){
                        return res.send({error : 'true', message : err.toString()});
                    }
                    // invoking sendinnotificaiotn funciton to send the notificaiotn to reveriver's device.
                    sendNofitication({ user_id : user._id, otheruser_id : req.params.receiverid, data : data }, true,
                        // this is the funciton to be called when notificaiton is sent
                        function(response){                                                
                            res.send(response);
                        }
                    );
                });
            });
        });
    });

    // accepting friend request
    api.post('/wavelength/wavelength_restapi/v1/acceptrequest/:receiverid/:senderid', function(req, res){
        // getting user's object from db who got the request
        userData.AppData.findById(req.params.receiverid, function(err, user){
            if(err) {
                return res.send({ error : 'true', message : err.toString() });
            }
            if(!user || user === null) {
                return res.send({ error : 'true', message : 'User Not Found' });
            };
            // getting user's object from db who's request is being accepted
            userData.AppData.findById(req.params.senderid, function(err, sender){
                if(err) {
                    return res.send({ error : 'true', message : err.toString() });
                }
                if(!sender || sender === null) {
                    return res.send({ error : 'true', message : 'User Not Found' });
                };
                // data to be send as notificaiton
                var data = {
                    to: sender.device_id,
                    data: {
                        title: 'Wavelength',
                        isBackground: false,
                        flag : 3,
                        data: {
                            "sender_name":user.name,
                            "profile_pic": user.profile_pic,
                            "sender_id":user._id,
                            "message" : "Accepted Your Friendship Request"
                        }
                    }
                };
                // friendship request objet is being find from db and status is being updated to 1. i mean friendship request is accepted.
                UserActivity.findOneAndUpdate({user_id : sender._id, otheruser_id : user._id}, {status : 1,$currentDate: {created_at:Date}}).exec(function(err){
                    if(err){
                        return res.send({error : 'true', message : err.toString()});
                    }
                    sendNofitication({ user_id : sender._id, otheruser_id : user._id , data : data }, true,
                        function(response){                                                
                            res.send(response);
                        }
                    );
                });  
            });
        });
    });


    // rejecting friend request
    api.post('/wavelength/wavelength_restapi/v1/rejectrequest/:receiverid/:senderid', function(req, res){
        // getting user's object from db who got the request
        userData.AppData.findById(req.params.receiverid, function(err, user){
            if(err) {
                return res.send({ error : 'true', message : err.toString() });
            }
            if(!user || user === null) {
                return res.send({ error : 'true', message : 'User Not Found' });
            };
            // getting user's object from db who's request is being rejected
            userData.AppData.findById(req.params.senderid, function(err, sender){
                if(err) {
                    return res.send({ error : 'true', message : err.toString() });
                }
                if(!sender || sender === null) {
                    return res.send({ error : 'true', message : 'User Not Found' });
                };
                // data to be sent in notificaiton
                var data = {
                    to: sender.device_id,
                    data: {
                        title: 'Wavelength',
                        isBackground: false,
                        flag : 3,
                        data: {
                            "sender_name":user.name,
                            "profile_pic": user.profile_pic,
                            "sender_id":user._id,
                            "message" : "Rejected Your Friendship Request"
                        }
                    }
                };
                // friendship request is being updated with status 2  : ie request is being rejected
                UserActivity.findOneAndUpdate({user_id : sender._id, otheruser_id : user._id}, {status : 2,$currentDate: { created_at:Date}}).exec(function(err){
                    if(err){
                        return res.send({error : 'true', message : err.toString()});
                    }
                    res.send({error : false, message : "successfully rejected request"});
                });  
            });
        });
    });

    // chatting 
    api.post('/wavelength/wavelength_restapi/v1/send_chatmessage/:senderid/:receiverid', function(req, res){
        userData.AppData.findById(req.params.receiverid, function(err, receiver){
            if(err) {
                return res.send({ error : 'true', message : err.toString() });
            }
            if(!receiver || receiver === null) {
                return res.send({ error : 'true', message : 'User Not Found' });
            };
            userData.AppData.findById(req.params.senderid, function(err, sender){
                if(err) {
                    return res.send({ error : 'true', message : err.toString() });
                }
                if(!sender || sender === null) {
                    return res.send({ error : 'true', message : 'User Not Found' });
                };
                var data = {
                    to: receiver.device_id,
                    data: {
                        title: 'Wavelength',
                        isBackground: false,
                        flag : 2,
                        data: {
                            "sender_id":sender._id,                     
                            "sender_name":sender.name,
                            "profile_pic": sender.profile_pic,
                            "created_at":new Date(),
                            "message" : req.body.message
                        }
                    }
                };
            
                // sending notificaiotn to user
                sendNofitication({ sender_id : req.params.senderid, receiver_id : receiver._id , data : data }, true,
                    function(response){                                              
                        res.send(response);
                    }
                );


            });    
        });
    });

    


    // api to delete user's profile
    // @pathparam : userid here userid is id of user who's profile is to be deleted
    api.get('/wavelength/wavelength_restapi/v1/deleteprofile/:userid', function(req, res){
        userData.AppData.findOneAndUpdate({_id:req.params.userid},{inActive:1},function(err, user) {
            if (err) {
                return res.send({ error : true, message : err.toString()});
            } else {
                return res.send({error : false, message : "Profile successfully deleted"});
            }
            
        });

    });

    // api for delete friendhsipw ie: unfriend
    // @pathparam : userid, friendid userid is id of  user who want to delete friendship request and friendid is the id of user wich whome friendship request ineed to be deleted
    api.get('/wavelength/wavelength_restapi/v1/unfriend/:userid/:friendid', function(req, res){
        UserActivity.findOneAndUpdate({user_id : req.params.userid, otheruser_id : req.params.friendid,  status : 1},{status:3},function(err, friendshipRequest){
            if(err) {
                return res.send({ error : true, message : err.toString()});
            }
            UserActivity.findOneAndUpdate({user_id : req.params.friendid, otheruser_id : req.params.userid, status : 1},{status:3},function(err, friendshipRequest){
                if(err) {
                    return res.send({ error : true, message : err.toString()});
                }
                return res.send({error : false, message : 'success'});
            });            
        });
    }); 


    // api for reporting about a user
    api.post('/wavelength/wavelength_restapi/v1/reportprofile', function(req, res){
        var ReportProfile = new reportprofile({
            user_id :req.body.user_id,
            reportprofile_id: req.body.reportprofile_id,
            report_type: req.body.report_type
        });
        ReportProfile.save(function(err){
            if(err) {
                res.statusCode = 404;
                return res.send({ error: err });
            }else{
                return res.send({ error: 'false', message:"User Reported" }); 
            }

        });
        /*UserActivity.findOneAndUpdate({user_id : req.body.user_id, otheruser_id : req.body.reportprofile_id,  status : 1},{status:5},function(err, friendshipRequest){
            if(err) {
                return res.send({ error : true, message : err.toString()});
            }
            UserActivity.findOneAndUpdate({user_id : req.body.reportprofile_id, otheruser_id : req.body.user_id, status : 1},{status:5},function(err, friendshipRequest){
                if(err) {
                    return res.send({ error : true, message : err.toString()});
                }
                return res.send({error : false, message : 'success'});
            });            
        });*/

    }); 
   

    return api
}
