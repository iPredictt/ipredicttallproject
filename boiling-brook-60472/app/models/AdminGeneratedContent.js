var mongoose = require('mongoose');
var ContentSchema = new mongoose.Schema({
	content_id:Number,
	tag:String,
	name:String,
	description:String,
	type:String,
	graphic:String

});

module.exports = mongoose.model('content', ContentSchema,'Admincontent');	

