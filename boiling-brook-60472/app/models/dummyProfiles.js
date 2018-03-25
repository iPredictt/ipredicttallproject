var mongoose = require('mongoose');

var dummyUsersSchema = new mongoose.Schema({
    name: String,
    email: String,
    profile_pic: String,
    location:String,
    dob:String,
    bio:String,
    education:[String],
    pie_chart:[],
    work:[String],
    hometown:String,
    image_url:[String]

});



var dummyUsers = module.exports = mongoose.model('dummyProfiles', dummyUsersSchema,'dummyUsers');

// Get dummyProfiles

module.exports.getDummyProfiles = function(callback,limit){

    dummyUsers.find(callback).limit(10);
}