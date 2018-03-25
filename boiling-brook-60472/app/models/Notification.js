var mongoose = require('mongoose');
var Schema = mongoose.Schema;
// This collection used to stores notification data.

var NotificationSchema = new Schema({
	sender_id :{ type: Number, ref: 'UserDetails' },
	receiver_id: { type: Number, ref: 'UserDetails' },
    data : {type : Object},
});
NotificationSchema.pre('save', function(next){
  this.data.data.data.created_at = new Date();
  next();
});
module.exports = mongoose.model('Notification', NotificationSchema,'Notifications');


 
