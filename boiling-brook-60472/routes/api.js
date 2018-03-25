var userData = require('../app/models/userData');
var dummyProfiles = require('../app/models/dummyProfiles');
var AppSource = require('../app/models/AppInstallSource');
var reportprofile = require('../app/models/ReportProfile');
var canvas = require('../app/models/Canvas');
var Notification =  require('../app/models/Notification');
var UserActivity =  require('../app/models/UserActivity');
var AdminContent = require('../app/models/AdminGeneratedContent');
var request = require('request-json');

module.exports = function(app,express){
    var api = express.Router();

    // This api uses for dummy profiles data.
    api.get('/wavelength/wavelength_restapi/v1/get_dummy_profiles', function(req,res){
        dummyProfiles.find({}, function(err, user){
            if(!user) {
                res.statusCode = 404;
                return res.send({ error: err });
            }
            if (!err) {
                return res.send({ error: 'false', user:user });
            }
        });
    });
   

    // This api stores user login data coming from facebook. we are using facebook_id as _id
    api.post('/wavelength/wavelength_restapi/v1/post_user_details',function(req,res){

        

        var userProfile = {
            identifier:0,
            _id:req.body.facebook_id,
            name :req.body.name,
            email: req.body.email,
            profile_pic: req.body.profile_pic?req.body.profile_pic:'',
            social_provider: req.body.social_provider?req.body.social_provider:'',
            score: req.body.score?req.body.score:70,
            location: req.body.location?req.body.location:'',
            dob:req.body.dob?req.body.dob:"",
            bio:req.body.bio?req.body.bio:"",
            education: req.body.education?req.body.education:"",
            likes: req.body.likes?req.body.likes:"",
            work:req.body.work?req.body.work:"",
            events:req.body.events?req.body.events:"",
            posts:req.body.posts?req.body.posts:"",
            hometown:req.body.hometown?req.body.hometown:"",
            image_url:req.body.image_url?req.body.image_url:"",
            friend_list:req.body.friend_list?req.body.friend_list:"",
            tagged_places:req.body.tagged_places?req.body.tagged_places:""

        };
        var update = true;
        // Storing user data into 2 collections Rawdata in raw collection & AppData is live collection which app uses.
        // Code is for new user creation and update on old user login.
        userData.RawData.findOneAndUpdate({_id:userProfile._id}, userProfile,  function(err, user){            
            if(err) {
                res.statusCode = 404;
                return res.send({ error: err });
            }
            if(!user){
                update = false;
                userData.RawData.create(userProfile, function(err, user){
                    if(err) {
                        res.statusCode = 404;
                        return res.send({ error: err });
                    }
                    userData.AppData.create(userProfile, function(err, _user){
                       return res.send({ error: 'false', user:_user });  
                    });                    
                });
            }else{
                if(update){
                    userData.AppData.findOneAndUpdate({_id:userProfile._id}, userProfile, function(err, _user){
                        return res.send({ error: 'false', user:_user }); 
                    });
                }
            }           
        });
    });

    
    // Put request for updating a user device_id
    api.put('/wavelength/wavelength_restapi/v1/put_user_device_id/:_id', function (req, res){
        userData.AppData.findOneAndUpdate({_id : req.params._id}, {device_id : req.body.device_id}, function (err, user) {
            if(!user) {
                res.statusCode = 404;
                return res.send({ error: ' Found' });
            }
            if (err) {
                return res.send({ error: 'true', error:err.toString()});
            }
            userData.RawData.findOneAndUpdate({_id : req.params._id}, {device_id : req.body.device_id}, function (err, user) {
                return res.send({ error: 'false', message:'device id inserted' });                
            });            
        });
    });

    //api for  updating user data 
    api.put('/wavelength/wavelength_restapi/v1/update_data/:_id', function(req,res){
        var objForUpdate = {};

        if (req.body.bio) objForUpdate.bio = req.body.bio;
        if (req.body.work) objForUpdate.work = req.body.work;
        var setObj = { $set: objForUpdate }
        userData.AppData.findOneAndUpdate({_id : req.params._id}, objForUpdate, function (err, user) {
            if(!user) {
                res.statusCode = 404;
                return res.send({ error: ' Found' });
            }
            else{
                return res.send({ error: 'false', message:"Your profile Updated"});
            }

        });
    }); 


   // Get request for getting a single user matching Profiles
    api.get('/wavelength/wavelength_restapi/v1/matching_profiles/:_id', function(req, res) {
        userData.AppData.findOne({_id : req.params._id}, function (err, user) {
            if(err) {
                res.statusCode = 500;
                return res.send({ error : err });
            }
            if(!user) {
                res.statusCode = 404;
                return res.send({ error : 'User Not Found' });
            }
                       
            var mybuddyList = [];
            UserActivity.find({user_id : user._id, status : { $in : [0,1,2,3,4,5]}}, 'otheruser_id').populate("otheruser_id","_id").exec(function(err, friendshipRequests){            
                friendshipRequests.forEach(function(friendshipRequest, index){
                    if(friendshipRequest.otheruser_id!==null)
                    mybuddyList.push(friendshipRequest.otheruser_id._id);
                });
                UserActivity.find({otheruser_id : user._id, status : { $in : [0,1,2,3,4,5]}}, 'user_id').populate("user_id","_id").exec(function(err, friendshipRequests){
                    friendshipRequests.forEach(function(friendshipRequest, index){
                        if(friendshipRequest.user_id!==null)
                        mybuddyList.push(friendshipRequest.user_id._id);
                    });
                    var notIn = [user._id].concat(mybuddyList);
                    userData.AppData.find({_id : { $not : { $in : notIn}},},{name:1,device_id:1,_id:1,profile_pic:1,location:1,bio:1,dob:1,image_url:1,likes:1,education:1,work:1,hometown:1,pie_chart:1},{sort: {created_at: -1},limit:15}, function(err, users){
                        if(err) {
                            res.statusCode = 500;
                            return res.send({ error : err });
                        }
                        if(users.length == 0){
                            return res.send({ error : true, message : "no matching profile found"});   
                        }
                        return res.send({ error : false, profiles: users });   
                            
                            
                    })                    
                });        
            });         
        });
    });     


    
    // get request for marketing interactive canvas
    api.get('/wavelength/wavelength_restapi/v1/interactive_canvas',function(req,res){
        canvas.find({}, function(err, user){
            if(!user) {
                res.statusCode = 404;
                return res.send({ error: 'Found' });
            }
            if (!err) {
                return res.send({ error: 'false', user:user });
            }
        });
    });

    // get request for getting buddy list
    api.get('/wavelength/wavelength_restapi/v1/getbuddylist/:userid', function(req,res){

        userData.AppData.findOne({_id : req.params.userid}, function (err, user) {
            if(err) {
                res.statusCode = 500;
                return res.send({ error : err });
            }
            if(!user) {
                res.statusCode = 404;
                return res.send({ error : 'User Not Found' });
            } 
              
            var mybuddyList = [];
            
            UserActivity.find({user_id : req.params.userid, status : 1}, 'otheruser_id').populate("otheruser_id","_id name device_id profile_pic").exec(function(err, friendshipRequests){            
                friendshipRequests.forEach(function(friendshipRequest, index){
                    if(friendshipRequest.otheruser_id!==null){
                        mybuddyList.push(friendshipRequest.otheruser_id);
                    }                
                });
                UserActivity.find({otheruser_id : req.params.userid, status : 1}, 'user_id').populate("user_id","_id name device_id profile_pic").exec(function(err, friendshipRequests){
                    friendshipRequests.forEach(function(friendshipRequest, index){
                        if(friendshipRequest.user_id!==null){
                            mybuddyList.push(friendshipRequest.user_id);
                        }
                    });
                    if(mybuddyList.length == 0){
                        return res.send({error : 'true', message : "You don't have any buddy list"});
                    }
                    // here buddylist in response and error : false
                    res.send({buddylist : mybuddyList, error : false});
                });    
            });
        });
    });    

     
    
    // API  for getting pending request
    api.get('/wavelength/wavelength_restapi/v1/getpendingrequest/:userid', function(req,res){        
        var pendingfriendrequest = [];
        
        UserActivity.find({otheruser_id : req.params.userid, status : 0}).populate("user_id","_id name device_id profile_pic").exec(function(err, friendshipRequests){
            friendshipRequests.forEach(function(friendshipRequest, index){
                if(friendshipRequest.user_id){
                    pendingfriendrequest.push({_id : friendshipRequest.user_id._id, name : friendshipRequest.user_id.name, profile_pic:friendshipRequest.user_id.profile_pic, device_id : friendshipRequest.user_id.device_id, created_at : friendshipRequest.created_at});
                }                
            });
            if(pendingfriendrequest.length == 0){
                return res.send({error : 'true', message : "You don't have any pending request"});
            }
            //sending pending request in response
            res.send({pendingfrindrequest : pendingfriendrequest, error : false});
        });
    });

    // get request for user profile in buddy list
    api.get('/wavelength/wavelength_restapi/v1/my_buddy_details/:_id',function(req,res){
        userData.AppData.findById(req.params._id,{score:0,rejected:0,posts:0,events:0,email:0,social_provider:0}, function (err, user) {
            if(!user) {
                res.statusCode = 404;
                return res.send({ error: 'Found' });
            }
            if (!err) {
                return res.send({ error: 'false', user:user });
            }
        });
    });

    // get request for content
    api.get('/wavelength/wavelength_restapi/v1/content',function(req,res){
        AdminContent.find({},  function (err, user) {
            if(!user) {
                res.statusCode = 404;
                return res.send({ error: 'Found' });
            }
            if (!err) {
                return res.send({ error: 'false', user:user });
            }
        });
    });

    // post request for storing content
    api.post('/wavelength/wavelength_restapi/v1/post_content', function(req,res){

        var contentData = {
            content_id:req.body.content_id,
            tag:req.body.tag,
            name:req.body.name,
            description:req.body.description,
            type:req.body.type,
            graphic:req.body.graphic
            
        }; 
        AdminContent.create(contentData, function(err, data){
            return res.send({ message:'Data Inserted' });  
        }); 



    });

    // get request for user profile in buddy list
    api.get('/wavelength/wavelength_restapi/v1/my_profile_data/:_id',function(req,res){
        userData.AppData.findById(req.params._id,{pie_chart:1,_id:0}, function (err, user) {
            if(!user) {
                res.statusCode = 404;
                return res.send({ error: 'Found' });
            }
            if (!err) {
                return res.send({ error: 'false', user:user });
            }
        });
    });

    // App Install Source
    api.post('/wavelength/wavelength_restapi/v1/app_install_source',function(req,res){

        var Source ={
            device_id:req.body.device_id,
            user_id:req.body.facebook_id,
            referrer:req.body.referrer,
            device_detail:req.body.device_detail
        };
        AppSource.findOneAndUpdate({device_id:Source.device_id},{$currentDate: {installed_at:Date},user_id:Source.user_id}, Source, function(err, user){            
            if(!user){
                AppSource.create(Source, function(err, user){
                    return res.send({ error: 'false',message:'User Login in App'});
                    
                });
            }else{
                return res.send({error:'false',message:'User App Installed'})
            }
        });            
    });

    



    return api


}

