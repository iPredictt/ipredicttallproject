var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var FriendshipRequestSchema = new Schema({
	user_id :{ type: Number, ref: 'UserDetails' },
	otheruser_id: { type: Number, ref: 'UserDetails' },
    status : {type: Number, default : 0},
    created_at :{type:Date, default: Date.now},
  
  
});

module.exports = mongoose.model('FriendshipRequest', FriendshipRequestSchema,'UserActivity');
