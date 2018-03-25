var mongoose = require('mongoose');
var InteractiveCanvasSchema = new mongoose.Schema({
	ad_id:String,
	text:String,
	url:String

});

var  InteractiveCanvas = module.exports = mongoose.model('canvas', InteractiveCanvasSchema,'InteractiveCanvas');	

// Get Canvas Data

module.exports.getCanvas = function(callback,limit){

    InteractiveCanvas.find(callback).limit(limit);

}