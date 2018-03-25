var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var FriendshipRequestSchema = new Schema({
	sender_id :{ type: Number, ref: 'UserDetails' },
	receiver_id: { type: Number, ref: 'UserDetails' },
    status : {type: Number, default : 0},
    created_at :{type:Date, default: Date.now}
  // 0 for new request
  // 1 for accepted
  // 2 for rejected
  // In case of delete buddy the object is deleted from database.
});


module.exports = mongoose.model('FriendshipRequest', FriendshipRequestSchema,'UserConnectionRequests');


 
