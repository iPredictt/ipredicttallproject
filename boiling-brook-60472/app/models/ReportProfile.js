var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var ReportProfileSchema = new Schema({
	user_id :{ type: Number},
	reportprofile_id: { type: Number},
    report_type : Number
    // 1 Inappropriate Behaviour
    // 2 Bad offline Behaviour
    // 3 Feels like Spam
});


module.exports = mongoose.model('ReportProfile', ReportProfileSchema,'ProfileReports');