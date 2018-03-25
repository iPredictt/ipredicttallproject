var mongoose = require('mongoose');
var Schema = mongoose.Schema;
var UserPostSchema = new Schema({

    created_at:{type: Date, default: Date.now},
    _id:Number,
	name :String,
	email: String, 
    profile_pic: String, 
    social_provider:String,
    device_id:String,
    identifier:Number,
    score:  Number,
    location: String,
    dob: String,
    bio: String,
    education: [String],
    likes:[{_id:false,created_time:Date,name:String,category:String}],
    work:[String],
    events:[{_id:false,description:String,end_time:Date,name:String,place:{_id:false,street:String,name:String,city:String,country:String,latitude:String,longitude:String,zip:Number},rsvp_status:String,start_time:Date}],
    posts:[{_id:false,created_time:Date,description:String,likes:[{_id:false,name:String}],comments:[{_id:false,name:String,message:String,created_time:Date,comments:[{_id:false,created_time:Date,name:String,message:String}]}],message:String,place:{_id:false,street:String,name:String,city:String,country:String,latitude:String,longitude:String,zip:Number},shares:{count:Number},story:String}],
    hometown:String,
    image_url:[String],
    friend_list:{_id:false,total_count:Number,friends:[{name:String,_id:false}]},
    tagged_places:[{_id:false,created_time:Date,place:{city:String,country:String,latitude:String,longitude:String,zip:Number,name:String,street:String}}]

},
{ _id: false });




var AppData = mongoose.model('UserDetails', UserPostSchema,'UserLoginData');
var RawData  = mongoose.model('UserRawData', UserPostSchema,'UserRawData');

module.exports = {
    AppData: AppData,
    RawData: RawData
    
};


/*// Get dummyProfiles

module.exports.getUserdata = function(callback,limit){

    UserDetails.find(callback).limit(limit);

}

module.exports.getUserById = function(id,callback){

    UserDetails.findById(id,callback);

} */




