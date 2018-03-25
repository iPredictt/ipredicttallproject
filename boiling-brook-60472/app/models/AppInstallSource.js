var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var AppSourceSchema = new Schema({
	device_id:String,
    user_id :{type: Number, default : 0},
    referrer : String,
    device_detail : String,
    installed_at :{type:Date, default: Date.now}
});


module.exports = mongoose.model('AppData', AppSourceSchema, 'UserAppData');
