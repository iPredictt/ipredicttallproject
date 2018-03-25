var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var UserLoginSchema = new Schema({

    //_id:{type:String,default:uuid.v1()},
    facebook_id:String, // fb
    created_at:{type: Date, default: Date.now},

    email: String, // fb or linkedin
    profile_pic: String, // fb or linkedin
    
    social_provider:String, // fb or linkedin
    identifier:Number, // server
    score:  {type:Number,default:70}, // server
    
    location: String, // fb 
    
    dob: String, // fb
    trade: String,
    interest:[String],
    bio: String, // fb
    education: [String], // fb 
    
    likes:[{_id:false,created_time:Date,name:String,category:String}], // fb
    work:[String], // fb or linkedin or app
    events:[{_id:false,description:String,end_time:Date,name:String,place:{_id:false,street:String,name:String,city:String,country:String,latitude:String,longitude:String,zip:Number},rsvp_status:String,start_time:Date}], // fb
    posts:[{_id:false,created_time:Date,description:String,likes:[{_id:false,name:String}],comments:[{_id:false,name:String,message:String,created_time:Date,comments:[{_id:false,created_time:Date,name:String,message:String}]}],message:String,place:{_id:false,street:String,name:String,city:String,country:String,latitude:String,longitude:String,zip:Number},shares:{count:Number},story:String}], // fb
    
    hometown:String, // fb
    image_url:[String], // fb
    
    friend_list:{_id:false,total_count:Number,friends:[{name:String,id:Number,_id:false}]}, //fb
    tagged_places:[{_id:false,created_time:Date,place:{city:String,country:String,latitude:String,longitude:String,zip:Number,name:String,street:String}}], // fb
    
    // linkedin
    firstname: String, // fb or linkedin
    lastname:String, // fb or linkedin
    
    headline:String, //  linkedin
    linkedin_id:String, // linkedin
    
    industry:String, // linkedin
    location:{country:{code:String},name:String}, // linkedin
    
    connections:Number, // linkedin
    positions:{_total:Number,values:[{company:{name:String},id:Number,isCurrent:Boolean,location:{country:{code:String},name:String},startDate:{month:Number,year:Number},title:String}]}, // linkedin
    summary:String, // linkedin 
    
    device_id:String, // app
    device_token:String // app
   
    
});
//{ _id: false });



module.exports = mongoose.model('UserLogin', UserLoginSchema,'UserData');








