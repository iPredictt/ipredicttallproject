var mongoose = require('mongoose');
var Schema = mongoose.Schema;
var ChatMessageSchema = new Schema({

    created_at:{type: Date, default: Date.now},
    sender_id : { type: Object, ref: 'UserLogin' },
    receiver_id : { type: Object, ref: 'UserLogin' },
    message : String    
});
//{ _id: false });



module.exports = mongoose.model('ChatMessage', ChatMessageSchema,'UserChatting');



/*// Get dummyProfiles

module.exports.getUserdata = function(callback,limit){

    UserDetails.find(callback).limit(limit);

}

module.exports.getUserById = function(id,callback){

    UserDetails.findById(id,callback);

} */




